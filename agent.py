def controller_selected(self, address):
    """
    Handles logic when a controller is selected from the list. Stores the bd_address and interface.

    Args:
        address: selected controller bd_address.

    returns: None
    """
    controller = address.text()
    self.log.info(f"Controller Selected: {controller}")
    self.controller.bd_address = controller

    if controller in self.controller.controllers_list:
        self.controller.interface = self.controller.controllers_list[controller]
    
    bluetooth_device_manager = BluetoothDeviceManager(interface=self.controller.interface)
    bluetooth_device_manager.power_on_adapter()

    # Remove previous interface detail row if it exists
    if self.previous_row_selected is not None:
        self.controllers_list_widget.takeItem(self.previous_row_selected)
        self.previous_row_selected = None

    # Get current row and insert interface detail below it
    row = self.controllers_list_widget.currentRow()
    item = QListWidgetItem(self.controller.get_controller_interface_details())
    item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
    self.controllers_list_widget.insertItem(row + 1, item)
    self.previous_row_selected = row + 1
    def controller_selected(self, address):
        """
        Handles logic when  a controller is selected from the list. Stores the bd_address and interface.

        Args:
            address: selected controller bd_address.

        returns: None

        """
        controller=address.text()
        self.log.info(f"Controller Selected: {controller}")
        self.controller.bd_address = controller

        if controller in self.controller.controllers_list:
            self.controller.interface=self.controller.controllers_list[controller]
        bluetooth_device_manager=BluetoothDeviceManager(interface=self.controller.interface)
        #run(self.log, f"hciconfig -a {self.controller.interface} up")
        bluetooth_device_manager.power_on_adapter()

        if self.previous_row_selected:
            self.controllers_list_widget.takeItem(self.previous_row_selected)


        row = self.controllers_list_widget.currentRow()
        item = QListWidgetItem(self.controller.get_controller_interface_details())
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.controllers_list_widget.insertItem(row + 1, item)
        self.previous_row_selected = row + 1























from __future__ import absolute_import, print_function, unicode_literals
from optparse import OptionParser
import dbus
import dbus.service
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

bus_name = 'org.bluez'
agent_interface = 'org.bluez.Agent1'
agent_path = "/test/agent"

bus = None
device_obj = None
dev_path = None

def ask(prompt):
    """
    Prompt the user for input.
    """
    try:
        return raw_input(prompt)
    except:
        return input(prompt)

def set_trusted(path):
    """
    Set the Bluetooth device at the given D-Bus path as trusted.

    Args:
        path (str): The D-Bus object path of the device.
    returns:
    	None
    """
    props = dbus.Interface(bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties")
    props.Set("org.bluez.Device1", "Trusted", True)

def dev_connect(path):
    """
    Connect to the Bluetooth device at the specified D-Bus path.

    Args:
        path (str): The D-Bus object path of the device.
    returns:
    	None
    """
    dev = dbus.Interface(bus.get_object("org.bluez", path), "org.bluez.Device1")
    dev.Connect()

class Rejected(dbus.DBusException):
    """
    Custom exception to signal rejection by the user or agent.
    """
    _dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
    """
    Implements the BlueZ Agent1 interface to handle pairing and authorization.

    This agent handles user interactions for PIN/passkey confirmation and
    trust setup via D-Bus methods.
    """
    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        """
        Set whether the agent should terminate the main loop on release.

        Args:
            exit_on_release (bool): If True, stop the main loop on release.
        returns:
        	None
        """
        self.exit_on_release = exit_on_release

    @dbus.service.method(agent_interface, in_signature="", out_signature="")
    def Release(self):
        """
        Called when the agent is released by BlueZ.

        args: None
        returns: None
        """
        print("Release")
        if self.exit_on_release:
            mainloop.quit()

    @dbus.service.method(agent_interface, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        """
        Ask the user to authorize a service request.

        Args:
            device (str): The device object path.
            uuid (str): The UUID of the requested service.
        returns:
        	None
        """
        print("AuthorizeService (%s, %s)" % (device, uuid))
        authorize = ask("Authorize connection (yes/no): ")
        if authorize == "yes":
            return
        raise Rejected("Connection rejected by user")

    @dbus.service.method(agent_interface, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        """
        Ask the user to enter a PIN code for pairing.

        Args:
            device (str): The device object path.

        Returns:
            str: The PIN code entered by the user.
        """
        print("RequestPinCode (%s)" % (device))
        set_trusted(device)
        return ask("Enter PIN Code: ")

    @dbus.service.method(agent_interface, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        """
        Ask the user to enter a numeric passkey.

        Args:
            device (str): The device object path.

        Returns:
            dbus.UInt32: The passkey as a 32-bit unsigned integer.
        """
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = ask("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(agent_interface, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        """
        Display the passkey and how many digits have been entered so far.

        Args:
            device (str): The device object path.
            passkey (int): The passkey to display.
            entered (int): Number of digits entered so far.
        returns:
        	None
        """
        print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

    @dbus.service.method(agent_interface, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        """
        Display a PIN code for manual entry.

        Args:
            device (str): The device object path.
            pincode (str): The PIN code to display.
        returns:
        	None
        """
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(agent_interface, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """
        Ask the user to confirm the displayed passkey.

        Args:
            device (str): The device object path.
            passkey (int): The passkey to confirm.
        returns:
        	None
        """
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        confirm = ask("Confirm passkey (yes/no): ")
        if confirm == "yes":
            set_trusted(device)
            return
        raise Rejected("Passkey doesn't match")

    @dbus.service.method(agent_interface, in_signature="ou", out_signature=" ")
    def RequestConfirmation(self, device, passkey):
        """
        Ask the user to confirm the displayed passkey.

        Args:
            device (str): The device object path.
            passkey (int): The passkey to confirm.

        Returns:
            int: The confirmed passkey.
        """
        print("Request-Confirmation (%s,%06d)" % (device, passkey))
        confirm = ask("Confirm passkey (yes/no):")
        if confirm == "yes":
            set_trusted(device)
            return passkey
        raise Rejected("Passkey does not match")

    @dbus.service.method(agent_interface, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        """
        Ask the user to authorize pairing with the device.

        Args:
            device (str): The device object path.
        returns:
        	None
        """
        print("RequestAuthorization (%s)" % (device))
        auth = ask("Authorize? (yes/no): ")
        if auth == "yes":
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(agent_interface, in_signature="", out_signature="")
    def Cancel(self):
        """
        Called if the pairing request was canceled.

        args: None
        returns: None
        """
        print("Cancel")

def pair_reply():
    """
    Callback when the device has been successfully paired.

    args: None
    returns: None
    """
    print("Device paired")
    set_trusted(dev_path)
    dev_connect(dev_path)
    mainloop.quit()

def pair_error(error):
    """
    Callback when pairing fails.

    Args:
        error (dbus.DBusException): The exception raised during pairing.
    returns:
    	None
    """
    err_name = error.get_dbus_name()
    if err_name == "org.freedesktop.DBus.Error.NoReply" and device_obj:
        print("Timed out. Cancelling pairing")
        device_obj.CancelPairing()
    else:
        print("Creating device failed: %s" % (error))
    mainloop.quit()

if __name__ == '__main__':
    """
    Entry point for the pairing agent.

    Registers the agent with BlueZ, optionally pairs with a device if specified,
    and enters the main loop.
    """
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    capability = "DisplayYesNo"

    parser = OptionParser()
    parser.add_option("-i", "--adapter", action="store",
                      type="string",
                      dest="adapter_pattern",
                      default=None)
    parser.add_option("-c", "--capability", action="store",
                      type="string", dest="capability")
    parser.add_option("-t", "--timeout", action="store",
                      type="int", dest="timeout",
                      default=60000)
    (options, args) = parser.parse_args()
    if options.capability:
        capability = options.capability

    path = "/test/agent"
    agent = Agent(bus, path)

    mainloop = GObject.MainLoop()

    obj = bus.get_object(bus_name, "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    manager.RegisterAgent(path, capability)

    print("Agent registered")

    if len(args) > 0 and args[0].startswith("hci"):
        options.adapter_pattern = args[0]
        del args[:1]

    if len(args) > 0:
        device = bluezutils.find_device(args[0], options.adapter_pattern)
        dev_path = device.object_path
        agent.set_exit_on_release(False)
        device.Pair(reply_handler=pair_reply, error_handler=pair_error,
                    timeout=60000)
        device_obj = device
    else:
        manager.RequestDefaultAgent(path)

    mainloop.run()
