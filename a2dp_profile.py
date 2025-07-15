import dbus
import subprocess
from Backend_lib.Linux.daemons import BluezServices


class A2DPManager:
    """
    Manages A2DP Bluetooth audio streaming and media control using BlueZ and PulseAudio.

    This class handles device discovery, sink management, audio file streaming, and
    media control (play/pause/next/previous/rewind) via the MediaControl1 D-Bus interface.
    """

    def __init__(self, interface=None):
        """
        Initialize the A2DPManager.

        Args:
            interface (str, optional): The Bluetooth adapter interface (e.g., hci0).
        returns:
            None
        """
        self.interface = interface
        self.bus = dbus.SystemBus()
        self.bluez_services = BluezServices(interface=self.interface)
        self.stream_process = None
        self.device_sink = None

    def start_streaming(self, device_address, audio_file):
        """
        Start A2DP audio streaming to a Bluetooth device.

        Args:
            device_address (str): The MAC address of the target Bluetooth device.
            audio_file (str): Path to the audio file to stream (.wav or .mp3).

        Returns:
            bool: True if streaming starts successfully, False otherwise.
        """
        print(f"Starting A2DP streaming to {device_address} with file: {audio_file}")
        device_path = self.bluez_services.find_device_path(device_address)
        if not device_path:
            print(f"Device path not found for address {device_address}")
            return False

        self.device_sink = self.get_sink_for_device(device_address)
        if not self.device_sink:
            print("No PulseAudio sink found for the selected Bluetooth device.")
            return False

        # Convert MP3 to WAV if needed
        if audio_file.endswith(".mp3"):
            wav_file = "/tmp/temp_audio.wav"
            if not self.convert_mp3_to_wav(audio_file, wav_file):
                return False
            audio_file = wav_file

        try:
            self.stream_process = subprocess.Popen(
                ["aplay", "-D", "pulse", audio_file],
                env={**subprocess.os.environ, "PULSE_SINK": self.device_sink}
            )
            print(f"Streaming audio to {device_address}")
            return True
        except Exception as e:
            print(f"Error while starting streaming: {e}")
            return False

    def convert_mp3_to_wav(self, audio_path, wav_path):
        """
        Convert an MP3 file to WAV format using ffmpeg.

        Args:
            audio_path (str): Path to the MP3 file.
            wav_path (str): Output path for the converted WAV file.

        Returns:
            bool: True if conversion succeeds, False otherwise.
        """
        try:
            subprocess.run(['ffmpeg', '-y', '-i', audio_path, wav_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed [mp3 to wav]: {e}")
            return False

    def stop_streaming(self):
        """
        Stop the currently active A2DP audio streaming process.

        Returns:
            bool: True if stopped successfully, False otherwise.
        """
        print("Stopping A2DP streaming...")
        if self.stream_process:
            try:
                self.stream_process.terminate()
                self.stream_process.wait()
                self.stream_process = None
                print("Streaming stopped successfully.")
                return True
            except Exception as e:
                print(f"Error while stopping streaming: {e}")
                return False
        else:
            print("No active streaming process.")
            return False

    def _get_media_control_interface(self, address):
        """
        Retrieve the MediaControl1 interface for a given device.

        Args:
            address (str): The MAC address of the Bluetooth device.

        Returns:
            dbus.Interface: The MediaControl1 D-Bus interface or None if not found.
        """
        try:
            om = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
            objects = om.GetManagedObjects()
            formatted_addr = address.replace(":", "_").upper()

            print("Searching for MediaControl1 interface...")
            for path, interfaces in objects.items():
                if "org.bluez.MediaControl1" in interfaces and formatted_addr in path:
                    print(f"Found MediaControl1 interface at: {path}")
                    return dbus.Interface(
                        self.bus.get_object("org.bluez", path),
                        "org.bluez.MediaControl1"
                    )
            print(f"No MediaControl1 interface found for device: {address}")
        except Exception as e:
            print(f"Failed to get MediaControl1 interface: {e}")
        return None

    def play(self, address):
        """
        Send Play command to the Bluetooth device.

        Args:
            address (str): MAC address of the device.
        returns:
            None
        """
        try:
            control = self._get_media_control_interface(address)
            if control:
                control.Play()
                print(f"Sent Play to {address}")
        except Exception as e:
            print(f"Failed to play: {e}")

    def pause(self, address):
        """
        Send Pause command to the Bluetooth device.

        Args:
            address (str): MAC address of the device.
        returns:
            None
        """
        try:
            control = self._get_media_control_interface(address)
            if control:
                control.Pause()
                print(f"Sent Pause to {address}")
        except Exception as e:
            print(f"Failed to pause: {e}")

    def next(self, address):
        """
        Send Next command to the Bluetooth device.

        Args:
            address (str): MAC address of the device.
        returns:
            None
        """
        try:
            control = self._get_media_control_interface(address)
            if control:
                control.Next()
                print(f"Sent Next to {address}")
        except Exception as e:
            print(f"Failed to send Next: {e}")

    def previous(self, address):
        """
        Send Previous command to the Bluetooth device.

        Args:
            address (str): MAC address of the device.
        returns:
            None
        """
        try:
            control = self._get_media_control_interface(address)
            if control:
                control.Previous()
                print(f"Sent Previous to {address}")
        except Exception as e:
            print(f"Failed to send Previous: {e}")

    def rewind(self, address):
        """
        Send Rewind command to the Bluetooth device.

        Args:
            address (str): MAC address of the device.
        returns:
            None
        """
        try:
            control = self._get_media_control_interface(address)
            if control:
                control.Rewind()
                print(f"Sent Rewind to {address}")
        except Exception as e:
            print(f"Failed to send Rewind: {e}")

    def get_connected_a2dp_sink_devices(self):
        """
        Get a list of currently connected A2DP sink devices.

        args: None
        Returns:
            dict: Dictionary of connected device MAC addresses and their names.
        """
        self.bluez_services.refresh_device_list()
        return {
            addr: dev["Name"]
            for addr, dev in self.bluez_services.devices.items()
            if dev["Connected"] and any("110b" in uuid.lower() for uuid in dev["UUIDs"])
        }

    def get_connected_a2dp_source_devices(self):
        """
        Get a list of currently connected A2DP source devices.

        args: None
        Returns:
            dict: Dictionary of connected device MAC addresses and their names.
        """
        self.bluez_services.refresh_device_list()
        return {
            addr: dev["Name"]
            for addr, dev in self.bluez_services.devices.items()
            if dev["Connected"] and any("110a" in uuid.lower() for uuid in dev["UUIDs"])
        }

    def set_device_address(self, address):
        """
        Set the current device for streaming and media control.

        Args:
            address (str): The MAC address of the target Bluetooth device.
        returns:
            None
        """
        self.device_address = address
        self.device_path = self.bluez_services.find_device_path(address)
        self.device_sink = self.get_sink_for_device(address)

    def get_sink_for_device(self, address):
        """
        Get the PulseAudio sink name for the given Bluetooth device address.

        Args:
            address (str): MAC address of the Bluetooth device.

        Returns:
            str or None: The sink name if found, otherwise None.
        """
        try:
            sinks_output = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True)
            address_formatted = address.replace(":", "_").lower()
            for line in sinks_output.splitlines():
                if address_formatted in line.lower():
                    sink_name = line.split()[1]
                    return sink_name
        except Exception as e:
            print(f"Error getting sink for device: {e}")
        return None
