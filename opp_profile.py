import dbus
import dbus.service
import dbus.mainloop.glib
import os
import subprocess
import time

class OPPManager:
    """
    Manages Object Push Profile (OPP) operations over Bluetooth using BlueZ and OBEX.

    This class can send files to Bluetooth devices and start/stop a local OBEX server
    to receive incoming file transfers.
    """

    def __init__(self):
        """
        Initialize the OPPManager with default values.
        """
        self.last_session_path = None
        self.opp_process = None

    def send_file_via_obex(self, device_address, file_path):
        """
        Send a file to a Bluetooth device via OBEX (Object Push Profile).

        args:
            device_address (str): Bluetooth address of the target device (e.g., 'XX:XX:XX:XX:XX:XX').
            file_path (str): Absolute path to the file to send.

        Returns:
            tuple: A tuple of (status, message). Status can be 'complete', 'error', or 'unknown'.
        """
        if not os.path.exists(file_path):
            msg = f"File does not exist: {file_path}"
            print(msg)
            return "error", msg

        try:
            session_bus = dbus.SessionBus()
            obex_service = "org.bluez.obex"
            manager_obj = session_bus.get_object(obex_service, "/org/bluez/obex")
            manager = dbus.Interface(manager_obj, "org.bluez.obex.Client1")

            # Clean up old session if it exists
            if self.last_session_path:
                try:
                    manager.RemoveSession(self.last_session_path)
                    print(f"Removed previous session: {self.last_session_path}")
                    time.sleep(1.0)
                except Exception as e:
                    print(f"Previous session cleanup failed: {e}")

            # Create a new OBEX session
            session_path = manager.CreateSession(device_address, {"Target": dbus.String("opp")})
            session_path = str(session_path)
            self.last_session_path = session_path
            print(f"Created OBEX session: {session_path}")

            # Push the file
            opp_obj = session_bus.get_object(obex_service, session_path)
            opp = dbus.Interface(opp_obj, "org.bluez.obex.ObjectPush1")
            transfer_path = opp.SendFile(file_path)
            transfer_path = str(transfer_path)
            print(f"Transfer started: {transfer_path}")

            # Monitor transfer status
            transfer_obj = session_bus.get_object(obex_service, transfer_path)
            transfer_props = dbus.Interface(transfer_obj, "org.freedesktop.DBus.Properties")

            status = "unknown"
            for _ in range(40):
                status = str(transfer_props.Get("org.bluez.obex.Transfer1", "Status"))
                print(f"Transfer status: {status}")
                if status in ["complete", "error"]:
                    break
                time.sleep(0.5)

            # Always remove session
            try:
                manager.RemoveSession(session_path)
                self.last_session_path = None
                print("Session removed after transfer.")
            except Exception as e:
                print(f"Error removing session: {e}")

            return status, f"Transfer finished with status: {status}"

        except Exception as e:
            msg = f"OBEX file send failed: {e}"
            print(msg)
            return "error", msg

    def start_opp_receiver(self, save_directory="/tmp"):
        """
        Start an OBEX Object Push server to receive files over Bluetooth.

        args:
            save_directory (str): Directory where received files will be stored.

        Returns:
            bool: True if server started successfully, False otherwise.
        """
        try:
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            if self.opp_process and self.opp_process.poll() is None:
                self.opp_process.terminate()
                self.opp_process.wait()
                print("Previous OPP server stopped.")


            self.opp_process = subprocess.Popen([
                "obexpushd",
                "-B",  # Bluetooth
                "-o", save_directory,
                "-n"  # No confirmation prompt
            ])

            print(f"OPP server started. Receiving files to {save_directory}")
            return True
        except Exception as e:
            print(f"Error starting OPP server: {e}")
            return False

    def stop_opp_receiver(self):
        """
        Stop the OBEX Object Push server if it's currently running.

        args: None
        returns: None
        """
        if self.opp_process and self.opp_process.poll() is None:
            self.opp_process.terminate()
            self.opp_process.wait()
            print("OPP server stopped.")
