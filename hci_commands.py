

def get_paired_devices(self, interface="hci0"):
    paired = {}
    adapter_path = f"/org/bluez/{interface}"
    objects = self.object_manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if "org.bluez.Device1" in interfaces:
            props = interfaces["org.bluez.Device1"]
            if props.get("Paired", False) and props.get("Adapter") == adapter_path:
                address = props.get("Address")
                name = props.get("Name", "Unknown")
                paired[address] = name
    return paired

def get_connected_devices(self, interface="hci0"):
    connected = {}
    adapter_path = f"/org/bluez/{interface}"
    objects = self.object_manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if "org.bluez.Device1" in interfaces:
            props = interfaces["org.bluez.Device1"]
            if props.get("Connected", False) and props.get("Adapter") == adapter_path:
                address = props.get("Address")
                name = props.get("Name", "Unknown")
                connected[address] = name
    return connected




import subprocess
import psutil
import time
import dbus

class DaemonManager:
    def __init__(self):
        self.processes = {}

    def is_running(self, name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == name:
                return True
        return False

    def is_defunct(self, name):
        for proc in psutil.process_iter(['name', 'status']):
            if proc.info['name'] == name and proc.status() == psutil.STATUS_ZOMBIE:
                return True
        return False

    def stop_process(self, name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == name:
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()

    def start_daemons(self):
        daemon_cmds = {
            "bluetoothd": ["bluetoothd", "-n", "-d", "--compat"],
            "pulseaudio": ["pulseaudio", "--start"]
        }

        for name, cmd in daemon_cmds.items():
            if self.is_defunct(name) or self.is_running(name):
                self.stop_process(name)
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes[name] = proc
                print(f"[DaemonManager] Started {name}")
            except Exception as e:
                print(f"[DaemonManager] Failed to start {name}: {e}")

        # Wait for DBus availability (optional)
        self.wait_for_dbus_service('org.bluez')
        self.wait_for_dbus_service('org.PulseAudio1')

    def stop_daemons(self):
        for name in ["bluetoothd", "pulseaudio"]:
            self.stop_process(name)
            print(f"[DaemonManager] Stopped {name}")

    def wait_for_dbus_service(self, service_name, timeout=10):
        bus = dbus.SystemBus() if service_name == "org.bluez" else dbus.SessionBus()
        for _ in range(timeout):
            try:
                if service_name in bus.list_names():
                    print(f"[DaemonManager] DBus service {service_name} is available.")
                    return
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError(f"Timeout waiting for DBus service: {service_name}")




hci_commands = {
    "Link Control commands": "0x01",
    "Link Policy commands": "0x02",
    "Controller and Baseband commands": "0x03",
    "Informational parameters": "0x04",
    "Status parameters": "0x05",
    "Testing commands": "0x06",
    "LE Controller commands": "0x08"
}

link_control_commands = {
    "Inquiry": ["0x0001", [{"LAP": "0x9E8B33", "length": 3}, {"Inquiry_Length": "0x8"}, {"Num_Responses": "0x0"}]],
    "Inquiry Cancel": ["0x0002",  []],
    "Periodic Inquiry Mode": ["0x0003", [{"Max_Period_Length": "0x0010", "length": 2}, {"Min_Period_Length": "0x000a", "length": 2}, {"LAP": "0x9E8B33", "length": 3}, {"Inquiry_Length": "0x08"},{"Num_Responses": "0x00"}]],
    "Exit Periodic Inquiry Mode": ["0x0004", []],
    "Create Connection": ["0x0005", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Packet_Type": "0xcc18", "length": 2}, {"Page_Scan_Repetition_Mode": "0x00"}, {"Reserved": "0x00"}, {"Clock_Offset": "0x0000", "length": 2}, {"Allow_Role_Switch": "0x01"}]],
    "Disconnect": ["0x0006", [{"Connection_Handle": "0x0000", "length": 2}, {"Reason": "0x13"}]],
    "Create Connection Cancel": ["0x0008", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "Accept Connection Request": ["0x0009", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Role": "0x00"}]],
    "Reject Connection Request": ["0x000a", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Reason": "0x0D"}]],
    "Link Key Request Reply": ["0x000b", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Link_Key": "0x000000000000000000000000000000000", "length": 16}]],
    "Link Key Request Negative Reply": ["0x000c", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "PIN Code Request Reply": ["0x000d", [{"BD_ADDR": "0x665544332211", "length": 6}, {"PIN_Code_Length": "0x01"}, {"PIN_Code": "0x000000000000000000000000000000000", "length": 16}]],
    "PIN Code Request Negative Reply": ["0x000e", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "Change Connection Packet Type": ["0x000f", [{"Connection_Handle": "0x0000", "length": 2}, {"Packet_Type": "0x330e", "length": 2}]],
    "Authentication Requested": ["0x0011", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Set Connection Encryption": ["0x0013", [{"Connection_Handle": "0x0000", "length": 2}, {"Encryption_Enable": "0x00"}]],
    "Change Connection Link Key": ["0x0015", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Link Key Selection": ["0x0017", [{"Key_Flag": "0x00"}]],
    "Remote Name Request": ["0x0019", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Page_Scan_Repetition_Mode": "0x00"}, {"Reserved": "0x00"}, {"Clock_Offset": "0x0000", "length": 2}]],
    "Remote Name Request Cancel": ["0x001a", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "Read Remote Supported Features": ["0x001b", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read Remote Extended Features": ["0x001c", [{"Connection_Handle": "0x0000", "length": 2}, {"Page_Number": "0x00"}]],
    "Read Remote Version Information": ["0x001d", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read Clock Offset": ["0x001f", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read LMP Handle": ["0x0020", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Setup Synchronous Connection": ["0x0028", [{"Connection_Handle": "0x0000", "length": 2}, {"Transmit_Bandwidth": "0x00000000", "length": 4}, {"Receive_Bandwidth": "0x00000000", "length": 4}, {"Max_Latency": "0x0000", "length": 2}, {"Voice_Setting": "0x0000", "length": 2}, {"Retransmission_Effort": "0x00"}, {"Packet_Type": "0x0000", "length": 2}]],
    "Accept Synchronous Connection Request": ["0x0029", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Transmit_Bandwidth": "0x00000000", "length": 4}, {"Receive_Bandwidth": "0x00000000", "length": 4}, {"Max_Latency": "0x0000", "length": 2}, {"Voice_Setting": "0x0000", "length": 2}, {"Retransmission_Effort": "0x00"}, {"Packet_Type": "0x0000", "length": 2}]],
    "Reject Synchronous Connection Request": ["0x002a", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Reason": "0x0d"}]],
    "IO Capability Request Reply": ["0x002b", [{"BD_ADDR": "0x665544332211", "length": 6}, {"IO_Capability": "0x03"}, {"OOB_Data_Present": "0x00"}, {"Authentication_Requirements": "0x03"}]],
    "User Confirmation Request Reply": ["0x002c", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "User Confirmation Request Negative Reply": ["0x002d", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "User Passkey Request Reply": ["0x002e", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Numeric_Value": "0x00000000", "length": 4}]],
    "User Passkey Request Negative Reply": ["0x002f", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "Remote OOB Data Request Reply": ["0x0030", [{"BD_ADDR": "0x665544332211", "length": 6}, {"C": "0x12345678901234567890123456789012", "length": 16}, {"R": "0x01212345678901234567890123456789", "length": 16}]],
    "Remote OOB Data Request Negative Reply": ["0x0033", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "IO Capability Request Negative Reply": ["0x0034", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Reason": "0x05"}]],
    "Enhanced Setup Synchronous Connection": ["0x003d", [{"Connection_Handle": "0x0000", "length": 2}, {"Transmit_Bandwidth": "0xffffffff", "length": 4}, {"Receive_Bandwidth":"0xffffffff", "length": 4}, {"Transmit_Coding_Format": "0x0000000000", "length": 5}, {"Receive_Coding_Format": "0x0000000000", "length": 5}, {"Transmit_Codec_Frame_Size": "0x0001", "length": 2}, {"Receive_Codec_Frame_Size": "0x0001", "length": 2}, {"Input_Bandwidth": "0x00000002", "length": 4}, {"Output_Bandwidth": "0x00000002", "length": 4}, {"Input_Coding_Format": "0x0000000000", "length": 5}, {"Output_Coding_Format": "0x0000000000", "length": 5}, {"Input_Coded_Data_Size": "0x0001", "length": 2}, {"Output_Coded_Data_Size": "0x0001", "length": 2}, {"Input_PCM_Data_Format": "0x01"}, {"Output_PCM_Data_Format": "0x01"}, {"Input_PCM_Sample_Payload_MSB_Position": "0x01"}, {"Output_PCM_Sample_Payload_MSB_Position": "0x01"}, {"Input_Data_Path": "0x00"}, {"Output_Data_Path": "0x00"}, {"Input_Transport_Unit_Size": "0x0a"}, {"Output_Transport_Unit_Size": "0x0a"}, {"Max_Latency": "0xffff", "length": 2}, {"Packet_Type": "0x003f", "length": 2}, {"Retransmission_Effort": "0x01"}]],
    "Enhanced Accept Synchronous Connection Request": ["0x003e", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Transmit_Bandwidth": "0xffffffff", "length": 4}, {"Receive_Bandwidth":"0xffffffff", "length": 4}, {"Transmit_Coding_Format": "0x0000000000", "length": 5}, {"Receive_Coding_Format": "0x0000000000", "length": 5}, {"Transmit_Codec_Frame_Size": "0x0001", "length": 2}, {"Receive_Codec_Frame_Size": "0x0001", "length": 2}, {"Input_Bandwidth": "0x00000002", "length": 4}, {"Output_Bandwidth": "0x00000002", "length": 4}, {"Input_Coding_Format": "0x0000000000", "length": 5}, {"Output_Coding_Format": "0x0000000000", "length": 5}, {"Input_Coded_Data_Size": "0x0001", "length": 2}, {"Output_Coded_Data_Size": "0x0001", "length": 2}, {"Input_PCM_Data_Format": "0x01"}, {"Output_PCM_Data_Format": "0x01"}, {"Input_PCM_Sample_Payload_MSB_Position": "0x01"}, {"Output_PCM_Sample_Payload_MSB_Position": "0x01"}, {"Input_Data_Path": "0x00"}, {"Output_Data_Path": "0x00"}, {"Input_Transport_Unit_Size": "0x0a"}, {"Output_Transport_Unit_Size": "0x0a"}, {"Max_Latency": "0xffff", "length": 2}, {"Packet_Type": "0x003f", "length": 2}, {"Retransmission_Effort": "0x01"}]],
    "Truncated Page": ["0x003f", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Page_Scan_Repetition_Mode": "0x00"}, {"Clock_Offset": "0x0000", "length": 2}]],
    "Truncated Page Cancel": ["0x0040", [{"BD_ADDR": "0x665544332211", "length": 6}]],
    "Set Connectionless Peripheral Broadcast": ["0x0041", [{"Enable": "0x01"}, {"LT_ADDR": "0x01"}, {"LPO_Allowed": "0x01"}, {"Packet_Type": "0xcc18", "length": 2}, {"Interval_Min": "0x00b0", "length": 2}, {"Interval_Max": "0x00b0", "length": 2}, {"Supervision_Timeout": "0x00b0", "length": 2}]],
    "Set Connectionless Peripheral Broadcast Receive": ["0x0042", [{"Enable": "0x01"}, {"BD_ADDR": "0x665544332211", "length": 6}, {"LT_ADDR": "0x01"}, {"Interval": "0x0002", "length": 2}, {"Clock_Offset": "0x00000000", "length": 4}, {"Next_Connectionless_Peripheral_Broadcast_Clock": "0x00000000", "length": 4}, {"Supervision_Timeout": "0x00b0", "length": 2}, {"Remote_Timing_Accuracy": "0x01"}, {"Skip": "0x00"}, {"Packet_Type": "0xcc18", "length": 2}, {"AFH_Channel_Map": "0xffffffffffffffffffff", "length": 10}]],
    "Start Synchronization Train": ["0x0043", []],
    "Receive Synchronization Train": ["0x0044", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Sync_Scan_Timeout": "0x0002", "length": 2}, {"Sync_Scan_Window": "0x0022", "length": 2}, {"Sync_Scan_Interval": "0x0026", "length": 2}]],
    "Remote OOB Extended Data Request Reply": ["0x0045", [{"BD_ADDR": "0x665544332211", "length": 6}, {"C_192": "0x12345678901234567890123456789012", "length": 16}, {"R_192": "0x12345678901234567890123456789012", "length": 16}, {"C_256": "0x12345678901234567890123456789012", "length": 16}, {"R_256": "0x12345678901234567890123456789012", "length": 16}]]
}

link_policy_commands = {
    "Hold Mode": ["0x0001", [{"Connection_Handle": "0x0000", "length": 2}, {"Hold_Mode_Max_Interval": "0x0008", "length": 2}, {"Hold_Mode_Min_Interval": "0x0008", "length": 2}]],
    "Sniff Mode": ["0x0003", [{"Connection_Handle": "0x0000", "length": 2}, {"Sniff_Max_Interval": "0x0500", "length": 2}, {"Sniff_Min_Interval": "0x0100", "length": 2}, {"Sniff_Attempt": "0x0006", "length": 2}, {"Sniff_Timeout": "0x0010", "length": 2}]],
    "Exit Sniff Mode": ["0x0004", [{"Connection_Handle": "0x0000", "length": 2}]],
    "QoS Setup": ["0x0007", [{"Connection_Handle": "0x0000", "length": 2}, {"Unused": "0x00"}, {"Service_Type": "0x00"}, {"Token_Rate": "0x00000000", "length": 4}, {"Peak_Bandwidth": "0x00000000", "length": 4}, {"Latency": "0x00000000", "length": 4}, {"Delay_Variation": "0x00000000", "length": 4}]],
    "Role Discovery": ["0x0009", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Switch Role": ["0x000b", [{"BD_ADDR": "0x665544332211", "length": 6}, {"Role": "0x00"}]],
    "Read Link Policy Settings": ["0x000c", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Write Link Policy Settings": ["0x000d", [{"Connection_Handle": "0x0000", "length": 2}, {"Link_Policy_Settings": "0x0003", "length": 2}]],
    "Read Default Link Policy Settings": ["0x000e", []],
    "Write Default Link Policy Settings": ["0x000f", [{"Default_Link_Policy_Settings": "0x0003", "length": 2}]],
    "Flow Specification": ["0x0010", [{"Connection_Handle": "0x0000", "length": 2}, {"Unused": "0x00"}, {"Flow_Direction": "0x00"}, {"Service_Type": "0x00"}, {"Token_Rate": "0x00000000", "length": 4}, {"Token_Bucket_Size": "0x00000000", "length": 4}, {"Peak_Bandwidth": "0x00000000", "length": 4}, {"Access_Latency": "0x00000000", "length": 4}]],
    "Sniff Subrating": ["0x0011", [{"Connection_Handle": "0x0000", "length": 2}, {"Max_Latency": "0x0004", "length": 2}, {"Min_Remote_Timeout": "0x0002", "length": 2}, {"Min_Local_Timeout": "0x0002", "length": 2}]]
}

controller_and_baseband_commands = {
    "Set Event Mask": ["0x001", []],
    "Reset": ["0x0003", []],
    "Set Event Filter": ["0x0005", [{"Filter_Type": "0x01"}, {"Filter_Condition_Type": "0x00"}, {"Condition": "0x000000", "length": 3}]],
    "Flush": ["0x0008",  [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read PIN Type": ["0x0009",  []],
    "Write PIN Type": ["0x000a", [{"PIN_Type": '0x00'}]],
    "Read Stored Link Key": ["0x000d",  [{"BD_ADDR": "0x665544332211", "length": 6}, {"Read_All": "0x00"}]],
    "Write Stored Link Key": ["0x0011",  [{"Num_Keys_To_Write": "0x01"}, {"BD_ADDR": "0x665544332211", "length": 6}, {"Link_Key": "0x00000000000000000000000000000000", "length": 16}]], #Todo (length of BD_ADDR: Num_Keys_To_Write × 6 octets) (length of Link_Key: Num_Keys_To_Write × 16 octets)
    "Delete Stored Link Key": ["0x0012",  [{"BD_ADDR": "0x665544332211", "length": 6}, {"Delete_All": "0x00"}]],
    "Write Local Name": ["0x0013", [{"Local_Name": "0x7665645f74736574", "length": 248}]],
    "Read Local Name": ["0x0014", []],
    "Read Connection Accept Timeout": ["0x0015", []],
    "Write Connection Accept Timeout": ["0x0016", [{"Connection_Accept_timeout": "0x7d00", "length": 2}]],
    "Read Page Timeout": ["0x0017", []],
    "Write Page Timeout": ["0x0018", [{"Page_Timeout": "0x2000", "length": 2}]],
    "Read Scan Enable": ["0x0019", []],
    "Write Scan Enable": ["0x001a", [{"Scan_Enable": "0x01", "length": 2}]],
    "Read Page Scan Activity": ["0x001b", []],
    "Write Page Scan Activity": ["0x001c", [{"Page_Scan_Interval": "0x0800", "length": 2}, {"Page_Scan_Window": "0x0012", "length": 2}]],
    "Read Inquiry Scan Activity": ["0x001d", []],
    "Write Inquiry Scan Activity": ["0x001e", [{"Inquiry_Scan_Interval": "0x1000", "length": 2}, {"Inquiry_Scan_Window": "0x0012", "length": 2}]],
    "Read Authentication Enable": ["0x001f", []],
    "Write Authentication Enable": ["0x0020", [{"Authentication_Enable": "0x01"}]],
    "Read Class of Device": ["0x0023", []],
    "Write Class of Device": ["0x0024", [{"Class_Of_Device": "0x000104", "length": 3}]],
    "Read Voice Setting": ["0x0025", []],
    "Write Voice Setting": ["0x0026", [{"Voice_Setting": "0x0060", "length": 2}]],
    "Read Automatic Flush Timeout": ["0x0027", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Write Automatic Flush Timeout": ["0x0028", [{"Connection_Handle": "0x0000", "length": 2}, {"Flush_Timeout": "0x0008", "length": 2}]],
    "Read Num Broadcast Retransmissions": ["0x0029", []],
    "Write Num Broadcast Retransmissions": ["0x002a", [{"Num_Broadcast_Retransmissions": "0x01"}]],
    "Read Hold Mode Activity": ["0x002b", []],
    "Write Hold Mode Activity": ["0x002c", [{"Hold_Mode_Activity": "0x00"}]],
    "Read Transmit Power Level": ["0x002d", [{"Connection_Handle": "0x0000", "length": 2}, {"Type": "0x00"}]],
    "Read Synchronous Flow Control Enable": ["0x002e", []],
    "Write Synchronous Flow Control Enable": ["0x002f", [{"Synchronous_Flow_Control_Enable": "0x00"}]],
    "Set Controller To Host Flow Control": ["0x0031", [{"Flow_Control_Enable": "0x00"}]],
    "Host Buffer Size": ["0x0033", [{"Host_ACL_Data_Packet_Length": "0x0008", "length": 2}, {"Host_Synchronous_Data_Packet_Length": "0x02"}, {"Host_Total_Num_ACL_Data_Packets": "0x0008", "length": 2}, {"Host_Total_Num_Synchronous_Data_Packets": "0x0000", "length": 2}]],
    "Host Number Of Completed Packets":["0x0035", [{"Num_Handles": "0x01"}, {"Connection_Handle": "0x0000", "length": 2}, {"Host_Num_Completed_Packets": "0x0002", "length": 2}]], #Todo (Connection_handle: Num_Handles × 2 octets) (Host_Num_Completed_Packets: Num_Handles × 2 octets)
    "Read Link Supervision Timeout": ["0x0036", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Write Link Supervision Timeout": ["0x0037", [{"Connection_Handle": "0x0000", "length": 2}, {"Link_Supervision_Timeout": "0x7d00", "length": 2}]],
    "Read Number Of Supported IAC": ["0x0038", []],
    "Read Current IAC LAP": ["0x0039", []],
    "Write Current IAC LAP": ["0x003a", [{"Num_Current_IAC": "0x01"}, {"IAC_LAP": "0x9E8B33", "length": 3}]], # ToDo: Length of IAC_LAP = Num_Current_IAC*3 octets
    "Set AFH Host Channel Classification": ["0x003f", [{"AFH_Host_Channel_Classification": "0xffffffffffffffffffff", "length": 10}]],
    "Read Inquiry Scan Type": ["0x0042", []],
    "Write Inquiry Scan Type": ["0x0043", [{"Scan_Type": "0x00"}]],
    "Read Inquiry Mode": ["0x0044", []],
    "Write Inquiry Mode": ["0x0045", [{"Inquiry_Mode": "0x00"}]],
    "Read Page Scan Type": ["0x0046", []],
    "Write Page Scan Type": ["0x0047", [{"Page_Scan_Type": "0x00"}]],
    "Read AFH Channel Assessment Mode ": ["0x0048", []],
    "Write AFH Channel Assessment Mode ": ["0x0049", [{"AFH_Channel_Assessment_Mode": "0x01"}]],
    "Read Extended Inquiry Response": ["0x0051", []],
    "Write Extended Inquiry Response": ["0x0052", [{"FEC_Required": "0x01"}, {"Extended_Inquiry_Response": "0x110c110e180a18011800030b054102461d6b00021009000a0235362e35205a65756c42090b", "length": 240}]],
    "Refresh Encryption Key": ["0x0053", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read Simple Pairing Mode ": ["0x0055", []],
    "Write Simple Pairing Mode ": ["0x0056", [{"Simple_Pairing_Mode": "0x00"}]],
    "Read Local OOB Data": ["0x0057", []],
    "Read Inquiry Response Transmit Power Level": ["0x0058", []],
    "Write Inquiry Response Transmit Power Level": ["0x0059", [{"TX_Power": "0x00"}]],
    "Read Default Erroneous Data Reporting": ["0x005a", []],
    "Write Default Erroneous Data Reporting": ["0x005b", [{"Erroneous_Data_Reporting": "0x00"}]],
    "Enhanced Flush": ["0x005f", [{"Connection_Handle": "0x0000", "length": 2}, {"Packet_Type": "0x00"}]],
    "Send Keypress Notification": ["0x0060", {"BD_ADDR": "0x665544332211", "length": 6}, {"Notification_Type": "0x00"}],
    "Set Event Mask Page 2": ["0x0063", [{"Event_Mask_Page_2": "0x0000000000000000", "length": 8}]],
    "Read Flow Control Mode": ["0x0066", []],
    "Write Flow Control Mode": ["0x0067", [{"Flow_Control_Mode": "0x00"}]],
    "Read Enhanced Transmit Power Level": ["0x0068", [{"Connection_Handle": "0x0000", "length": 2}, {"Type": "0x00"}]],
    "Read LE Host Support": ["0x006c", []],
    "Write LE Host Support": ["0x006d", [{"LE_Supported_Host": "0x00"}, {"Unused": "0x00"}]],
    "Set MWS Channel Parameters": ["0x006e", [{"MWS_Channel_Enable": "0x01"}, {"MWS_RX_Center_Frequency": "0x0002", "length": 2}, {"MWS_TX_Center_Frequency": "0x0002", "length": 2}, {"MWS_RX_Channel_Bandwidth": "0x0002", "length": 2}, {"MWS_TX_Channel_Bandwidth": "0x0002", "length": 2}, {"MWS_Channel_Type": "0x00"}]],
    "Set External Frame Configuration": ["0x006f", [{"MWS_Frame_Duration": "0x0008", "length": 2}, {"MWS_Frame_Sync_Assert_Offset": "0x0008", "length": 2}, {"MWS_Frame_Sync_Assert_Jitter": "0x0008", "length": 2}, {"MWS_Num_Periods": "0x01"}, {"Period_Duration": "0x0008", "length": 2}, {"Period_Type": "0x00"}]], #Todo (Period_Duration: MWS_Num_Periods × 2 octets) (Period_Type[i]: MWS_Num_Periods × 1 octet)
    "Set MWS Signaling": ["0x0070", [{"MWS_RX_Assert_Offset": "0x0008", "length": 2}, {"MWS_RX_Assert_Jitter": "0x0008", "length": 2}, {"MWS_RX_Deassert_Offset": "0x0008", "length": 2}, {"MWS_RX_Deassert_Jitter": "0x0008", "length": 2}, {"MWS_TX_Assert_Offset": "0x0008", "length": 2}, {"MWS_TX_Assert_Jitter": "0x0008", "length": 2}, {"MWS_TX_Deassert_Offset": "0x0008", "length": 2}, {"MWS_TX_Deassert_Jitter": "0x0008", "length": 2}, {"MWS_Pattern_Assert_Offset": "0x0008", "length": 2}, {"MWS_Pattern_Assert_Jitter": "0x0008", "length": 2}, {"MWS_Inactivity_Duration_Assert_Offset": "0x0008", "length": 2}, {"MWS_Inactivity_Duration_Assert_Jitter": "0x0008", "length": 2}, {"MWS_Scan_Frequency_Assert_Offset": "0x0008", "length": 2}, {"MWS_Scan_Frequency_Assert_Jitter": "0x0008", "length": 2}, {"MWS_Priority_Assert_Offset_Request": "0x0008", "length": 2}]],
    "Set MWS Transport Layer": ["0x0071", [{"Transport_Layer": "0x01"}, {"To_MWS_Baud_Rate": "0x00000000", "length": 4}, {"From_MWS_Baud_Rate": "0x00000000", "length": 4}]],
    "Set MWS Scan Frequency Table": ["0x0072", [{"Num_Scan_Frequencies": "0x01"}, {"Scan_Frequency_Low": "0x0008", "length": 2}, {"Scan_Frequency_High": "0x0008", "length": 2}]], #Todo: (Scan_Frequency_Low: Num_Scan_Frequencies × 2 octets) (Scan_Frequency_High: Num_Scan_Frequencies × 2 octets)
    "Set MWS_PATTERN Configuration": ["0x0073", [{"MWS_Pattern_Index": "0x01"}, {"MWS_Pattern_Num_Intervals": "0x01"}, {"MWS_Pattern_Interval_Duration": "0x0008", "length": 2}, {"MWS_Pattern_Interval_Type": "0x00"}]],
    "Set Reserved LT_ADDR": ["0x0074", [{"LT_ADDR": "0x01"}]],
    "Delete Reserved LT_ADDR": ["0x0075", [{"LT_ADDR": "0x01"}]],
    "Set Connectionless Peripheral Broadcast Data": ["0x0076", [{"LT_ADDR": "0x01"}, {"Fragment": "0x01"}, {"Data_Length": "0x01"}, {"Data": "0x11"}]], #Todo (Data: Data_Length octets)
    "Read Synchronization Train Parameters": ["0x0077", []],
    "Write Synchronization Train Parameters": ["0x0078", [{"Interval_Min": "0x0020", "length": 2}, {"Interval_Max": "0x0040", "length": 2}, {"Sync_Train_Timeout": "0x00000004", "length": 4}, {"Service_Data": "0x00"}]],
    "Read Secure Connections Host Support": ["0x0079", []],
    "Write Secure Connections Host Support": ["0x007a", [{"Secure_Connections_Host_Support": "0x00"}]],
    "Read Authenticated Payload Timeout": ["0x007b", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Write Authenticated Payload Timeout": ["0x007c", [{"Connection_Handle": "0x0000", "length": 2}, {"Authenticated_Payload_Timeout": "0x0008", "length": 2}]],
    "Read Local OOB Extended Data ": ["0x007d", []],
    "Read Extended Page Timeout": ["0x007e", []],
    "Write Extended Page Timeout": ["0x007f", [{"Extended_Page_Timeout": "0x0001", "length": 2}]],
    "Read Extended Inquiry Length": ["0x0080", []],
    "Write Extended Inquiry Length": ["0x0081", [{"Extended_Inquiry_Length": "0x0001", "length": 2}]],
    "Set Ecosystem Base Interval": ["0x0082", [{"Interval": "0x0000", "length": 2}]],
    "Configure Data Path": ["0x0083", [{"Data_Path_Direction": "0x00"}, {"Data_Path_ID":"0x00"}, {"Vendor_Specific_Config_Length": "0x01"}, {"Vendor_Specific_Config": "0x11"}]], #Todo (Vendor_Specific_Config: Vendor_Specific_Config_Length octets)
    "Set Min Encryption Key Size": ["0x0084", {"Min_Encryption_Key_Size": "0x01"}]
}

informational_parameters = {
    "Read Local Version Information": ["0x0001", []],
    "Read Local Supported Commands": ["0x0002", []],
    "Read Local Supported Features": ["0x0003", []],
    "Read Local Extended Features": ["0x0004", []],
    "Read Buffer Size": ["0x0005", []],
    "Read BD_ADDR": ["0x0009", []],
    "Read Data Block Size": ["0x000a", []],
    "Read Local Supported Codecs [v1]": ["0x000b", []],
    "Read Local Simple Pairing Options": ["0x000c", []],
    "Read Local Supported Codecs [v2]": ["0x000d", []],
    "Read Local Supported Codec Capabilities": ["0x000e", [{"Codec_ID": "0x0000000000", "length": 5}, {"Logical_Transport_Type": "0x00"}, {"Direction": "0x00"}]],
    # "Read Local Supported Controller Delay": ["0x000e", [{"Codec_ID": "0x0000000000", "length": 5}, {"Logical_Transport_Type": "0x00"}, {"Direction": "0x00"}, {"Codec_Configuration_Length": ""}, {"Codec_Configuration": ""}]], # ToDo
}

status_parameters = {
    "Read Failed Contact Counter": ["0x0001", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Reset Failed Contact Counter": ["0x0002", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read Link Quality Counter": ["0x0003", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read RSSI": ["0x0005", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read AFH Channel Map": ["0x0006", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Read Clock": ["0x0007", [{"Connection_Handle": "0x0000", "length": 2}, {"Which_Clock": "0x00"}]],
    "Read Encryption Key Size": ["0x0008", [{"Connection_Handle": "0x0000", "length": 2}]],
    "Get MWS Transport Layer Configuration": ["0x000c", []],
    "Set Triggered Clock Capture": ["0x000d", [{"Connection_Handle": "0x0000", "length": 2}, {"Enable": "0x01"}, {"Which_Clock": "0x00"}, {"LPO_Allowed": "0x01"}, {"Num_Clock_Captures_To_Filter": "0x00"}]]
}

testing_commands = {
    "Read Loopback Mode": ["0x0001", []],
    "Write Loopback Mode": ["0x0002", [{"Loopback_Mode": "0x00"}]],
    "Enable Implementation Under Test Mode": ["0x0003", []],
    "Write Simple Pairing Debug Mode": ["0x0004", [{"Simple_Pairing_Debug_Mode": "0x00"}]],
    "Write Secure Connections Test Mode": ["0x000a", [{"Connection_Handle": "0x0000", "length": 2}, {"DM1_ACL-U_Mode": "0x00"}, {"eSCO_Loopback_Mode": "0x00"}]]
}

le_controller_commands = {
    "LE Set Event Mask": ["0x0001", [{"LE_Event_Mask": "0x000000000000001f", "length": 8}]],
    "LE Read Buffer Size [v1]": ["0x0002", []],
    "LE Read Buffer Size [v2]": ["0x0060", []],
    "LE Read Local Supported Features Page 0": ["0x0003", []],
    "LE Set Random Address": ["0x0005", [{"Random_Address": "0x665544332211", "length": 6}]],
    "LE Set Advertising Parameters": ["0x0006", [{"Advertising_Interval_Min": "0x00b0", "length": 2}, {"Advertising_Interval_Max": "0x00b0", "length": 2}, {"Advertising_Type": "0x00"}, {"Own_Address_Type": "0x00"}, {"Peer_Address_Type": "0x00"}, {"Peer_Address": "0x000000000000", "length": 6}, {"Advertising_Channel_Map": "0x07"}, {"Advertising_Filter_Policy": "0x00"}]],
    "LE Read Advertising Physical Channel Tx Power": ["0x0007", []],
    "LE Set Advertising Data": ["0x0008", [{"Advertising_Data_Length": "0x08"}, {"Advertising_Data": "0x7665645f74736574", "length": 31}]],
    "LE Set Scan Response Data": ["0x0009", [{"Scan_Response_Data_Length": "0x05"}, {"Scan_Response_Data": "0x1122334455", "length": 31}]],
    "LE Set Advertising Enable": ["0x00a", [{"Advertising_Enable": "0x00"}]],
    "LE Set Scan Parameters": ["0x000b", [{"LE_Scan_Type": "0x00"}, {"LE_Scan_Interval": "0x0010", "length": 2}, {"LE_Scan_Window": "0x0010", "length": 2}, {"Own_Address_Type": "0x00"}, {"Scanning_Filter_Policy": "0x00"}]],
    "LE Set Scan Enable": ["0x000c", [{"LE_Scan_Enable": "0x01"}, {"Filter_Duplicates": "0x00"}]],
    "LE Create Connection": ["0x000d", [{"LE_Scan_Interval": "0x4000", "length": 2}, {"LE_Scan_Window": "0x4000", "length": 2}, {"Initiator_Filter_Policy": "0x00"}, {"Peer_Address_Type": "0x00"}, {"Peer_Address": "0x000000000000", "length": 6}, {"Own_Address_Type": "0x00"}, {"Connection_Interval_Min": "0x0c80", "length": 2}, {"Connection_Interval_Max": "0x0c80", "length": 2}, {"Max_Latency": "0x0000", "length": 2}, {"Supervision_Timeout": "0x0c80", "length": 2}, {"Min_CE_Length": "0x0100", "length": 2}, {"Max_CE_Length": "0x0100", "length": 2}]],
    "LE Create Connection Cancel": ["0x000e", []],
    "LE Read Filter Accept List Size": ["0x000f", []],
    "LE Clear Filter Accept List": ["0x0010", []],
    "LE Add Device To Filter Accept List": ["0x0011", [{"Address_Type": "0x00"}, {"Address": "0x665544332211", "length": 6}]],
    "LE Remove Device From Filter Accept List": ["0x0012", [{"Address_Type": "0x00"}, {"Address": "0x665544332211", "length": 6}]],
    "LE Connection Update": ["0x0013", [{"Connection_Handle": "0x0000", "length": 2}, {"Connection_Interval_Min": "0x0c80", "length": 2}, {"Connection_Interval_Max": "0x0c80", "length": 2}, {"Max_Latency": "0x0000", "length": 2}, {"Supervision_Timeout": "0x0c80", "length": 2}, {"Min_CE_Length": "0x0100", "length": 2}, {"Max_CE_Length": "0x0100", "length": 2}]],
    "LE Set Host Channel Classification": ["0x0014", [{"Channel_Map": "0x1fffffffff", "length": 5}]],
    "LE Read Channel Map": ["0x0015", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Read Remote Features Page 0": ["0x0016", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Encrypt": ["0x0017", [{"Key": "0x1234567890abcdef1234567890abcdef", "length": 16}, {"Plaintext_Data": "0x1234567890abcdef1234567890abcdef", "length": 16}]],
    "LE Rand": ["0x0018", []],
    "LE Enable Encryption": ["0x0019", [{"Connection_Handle": "0x0000", "length": 2}, {"Random_Number": "0x1234567890abcdef", "length": 8}, {"Encrypted_Diversifier": "0x000a", "length": 2}, {"Long_Term_Key": "0x1234567890abcdef1234567890abcdef", "length": 16}]],
    "LE Long Term Key Request Reply": ["0x001a", [{"Connection_Handle": "0x0000", "length": 2}, {"Long_Term_Key": "0x1234567890abcdef1234567890abcdef", "length": 16}]],
    "LE Long Term Key Request Negative Reply": ["0x001b", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Read Supported States": ["0x001c", []],
    "LE Receiver Test [v1]": ["0x001d", [{"RX_Channel": "0x08"}]],
    "LE Transmitter Test [v1]": ["0x001e", [{"TX_Channel": "0x08"}, {"Test_Data_Length": "0x0a"}, {"Packet_Payload": "0x00"}]],
    "LE Test End": ["0x001f", []],
    "LE Remote Connection Parameter Request Reply": ["0x0020", [{"Connection_Handle": "0x0000", "length": 2}, {"Interval_Min": "0x0c80", "length": 2}, {"Interval_Max": "0x0c80", "length": 2}, {"Max_Latency": "0x0000", "length": 2}, {"Timeout": "0x0c80", "length": 2}, {"Min_CE_Length": "0x0100", "length": 2}, {"Max_CE_Length": "0x0100", "length": 2}]],
    "LE Remote Connection Parameter Request Negative Reply": ["0x0021", [{"Connection_Handle": "0x0000", "length": 2}, {"Reason": "0x3b"}]],
    "LE Receiver Test [v2]": ["0x0033", [{"RX_Channel": "0x08"}, {"PHY": "0x01"}, {"Modulation_Index": "0x00"}]],
    "LE Transmitter Test [v2]": ["0x0034", [{"TX_Channel": "0x08"}, {"Test_Data_Length": "0x0a"}, {"Packet_Payload": "0x00"}, {"PHY": "0x01"}]],
    "LE Receiver Test [v3]": ["0x004f", [{"RX_Channel": "0x08"}, {"PHY": "0x01"}, {"Modulation_Index": "0x00"}, {"Expected_CTE_Length": "0x00"}, {"Expected_CTE_Type": "0x01"}, {"Slot_Durations": "0x01"}, {"Switching_Pattern_Length": "0x02"}, {"Antenna_IDs[i]": "0x0001", "length": 2}]],  # Todo Antenna_IDs[i]: Switching_Pattern_Length × 1 octet
    "LE Transmitter Test [v3]": ["0x0050", [{"TX_Channel": "0x08"}, {"Test_Data_Length": "0x0a"}, {"Packet_Payload": "0x00"}, {"PHY": "0x01"}, {"CTE_Length": "0x00"}, {"CTE_Type": "0x01"}, {"Switching_Pattern_Length": "0x02"}, {"Antenna_IDs[i]": "0x0001", "length": 2}]],  # Todo Antenna_IDs[i]: Switching_Pattern_Length × 1 octet
    "LE Transmitter Test [v4]": ["0x007b", [{"TX_Channel": "0x08"}, {"Test_Data_Length": "0x0a"}, {"Packet_Payload": "0x00"}, {"PHY": "0x01"}, {"CTE_Length": "0x00"}, {"CTE_Type": "0x01"}, {"Switching_Pattern_Length": "0x02"}, {"Antenna_IDs[i]": "0x0001", "length": 2}, {"TX_Power_Level": "0x7f"}]],  # Todo Antenna_IDs[i]: Switching_Pattern_Length × 1 octet
    "LE Set Data Length command ": ["0x0022", [{"Connection_Handle": "0x0000", "length": 2}, {"TX_Octets": "0x00fb", "length": 2}, {"TX_Time": "0x4290", "length": 2}]],
    "LE Read Suggested Default Data Length": ["0x0023", []],
    "LE Write Suggested Default Data Length": ["0x0024", [{"Suggested_Max_TX_Octets": "0x00fb", "length": 2}, {"Suggested_Max_TX_Time": "0x4290", "length": 2}]],
    "LE Read Local P-256 Public Key": ["0x0025", []],
    "LE Generate DHKey [v1]": ["0x0026", [{"Key_X_Coordinate": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "length": 32}, {"Key_Y_Coordinate": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "length": 32}]],
    "LE Generate DHKey [v2]": ["0x005e", [{"Key_X_Coordinate": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "length": 32}, {"Key_Y_Coordinate": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "length": 32}, {"Key_Type": "0x00"}]],
    "LE Add Device To Resolving List": ["0x0027", [{"Peer_Identity_Address_Type": "0x00"}, {"Peer_Identity_Address": "0x000000000000", "length": 6}, {"Peer_IRK": "0x1234567890abcdef1234567890abcdef", "length": 16}, {"Local_IRK": "0x1234567890abcdef1234567890abcdef", "length": 16}]],
    "LE Remove Device From Resolving List": ["0x0028", [{"Peer_Identity_Address_Type": "0x00"}, {"Peer_Identity_Address": "0x000000000000", "length": 6}]],
    "LE Clear Resolving List": ["0x0029", []],
    "LE Read Resolving List Size": ["0x002a", []],
    "LE Read Peer Resolvable Address": ["0x002b", [{"Peer_Identity_Address_Type": "0x00"}, {"Peer_Identity_Address": "0x000000000000", "length": 6}]],
    "LE Read Local Resolvable Address": ["0x002c", [{"Peer_Identity_Address_Type": "0x00"}, {"Peer_Identity_Address": "0x000000000000", "length": 6}]],
    "LE Set Address Resolution Enable": ["0x002d", [{"Address_Resolution_Enable": "0x00"}]],
    "LE Set Resolvable Private Address Timeout": ["0x002e", [{"RPA_Timeout": "0x0e10", "length": 2}]],
    "LE Read Maximum Data Length": ["0x002f", []],
    "LE Read PHY": ["0x0030", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Set Default PHY": ["0x0031", [{"All_PHYs": "0x00"}, {"TX_PHYs": "0x00"}, {"RX_PHYs": "0x00"}]],
    "LE Set PHY": ["0x0032", [{"Connection_Handle": "0x0000", "length": 2}, {"All_PHYs": "0x00"}, {"TX_PHYs": "0x00"}, {"RX_PHYs": "0x00"}, {"PHY_Options": "0x0000", "length": 2}]],
    "LE Set Advertising Set Random Address": ["0x0035", [{"Advertising_Handle": "0x00"}, {"Random_Address": "0x665544332211", "length": 6}]],
    "LE Set Extended Advertising Parameters [v1]": ["0x0036", [{"Advertising_Handle": "0x00"}, {"Advertising_Event_Properties": "0x0007", "length": 2}, {"Primary_Advertising_Interval_Min": "0xFFFFFF", "length": 3}, {"Primary_Advertising_Interval_Max": "0xFFFFFF", "length": 3},  {"Primary_Advertising_Channel_Map": "0x03"}, {"Own_Address_Type": "0x00"}, {"Peer_Address_Type": "0x00"}, {"Peer_Address": "0x000000000000", "length": 6}, {"Advertising_Filter_Policy": "0x00"}, {"Advertising_TX_Power": "0x7f"}, {"Primary_Advertising_PHY": "0x01"}, {"Secondary_Advertising_Max_Skip": "0x00"}, {"Secondary_Advertising_PHY": "0x01"}, {"Advertising_SID": "0x0f"}, {"Scan_Request_Notification_Enable": "0x01"}]],
    "LE Set Extended Advertising Parameters [v2]": ["0x007f", [{"Advertising_Handle": "0x00"}, {"Advertising_Event_Properties": "0x0007", "length": 2}, {"Primary_Advertising_Interval_Min": "0xFFFFFF", "length": 3}, {"Primary_Advertising_Interval_Max": "0xFFFFFF", "length": 3},  {"Primary_Advertising_Channel_Map": "0x03"}, {"Own_Address_Type": "0x00"}, {"Peer_Address_Type": "0x00"}, {"Peer_Address": "0x000000000000", "length": 6}, {"Advertising_Filter_Policy": "0x00"}, {"Advertising_TX_Power": "0x7f"}, {"Primary_Advertising_PHY": "0x01"}, {"Secondary_Advertising_Max_Skip": "0x00"}, {"Secondary_Advertising_PHY": "0x01"}, {"Advertising_SID": "0x0f"}, {"Scan_Request_Notification_Enable": "0x01"}, {"Primary_Advertising_PHY_Options": "0x00"}, {"Secondary_Advertising_PHY_Options": "0x00"}]],
    "LE Set Extended Advertising Data": ["0x0037", [{"Advertising_Handle": "0x00"}, {"Operation": "0x00"}, {"Fragment_Preference": "0x00"}, {"Advertising_Data_Length": "0x08"}, {"Advertising_Data": "0x7665645f74736574", "length": 8}]], # Todo: Advertising_Data: Advertising_Data_Length octets
    "LE Set Extended Scan Response Data": ["0x0038", [{"Advertising_Handle": "0x00"}, {"Operation": "0x00"}, {"Fragment_Preference": "0x00"}, {"Scan_Response_Data_Length": "0x05"}, {"Scan_Response_Data": "0x1122334455", "length": 5}]], # Todo: Scan_Response_Data: Scan_Response_Data_Length octets
    "LE Set Extended Advertising Enable": ["0x0039", [{"Enable": "0x01"}, {"Num_Sets": "0x01"}, {"Advertising_Handle": "0x00"}, {"Duration": "0x0000", "length": 2}, {"Max_Extended_Advertising_Events": "0x00"}]],  # Todo: (Advertising_Handle[i]: Num_Sets × 1 octet) (Duration[i]: Num_Sets × 2 octets) (Max_Extended_Advertising_Events[i]: Num_Sets × 1 octet)
    "LE Read Maximum Advertising Data Length": ["0x003a", []],
    "LE Read Number of Supported Advertising Sets": ["0x003b", []],
    "LE Remove Advertising Set": ["0x003c", [{"Advertising_Handle": "0x00"}]],
    "LE Clear Advertising Sets": ["0x003d", []],
    "LE Set Periodic Advertising Parameters": [],
    "LE Set Periodic Advertising Data": ["0x003f", [{"Advertising_Handle": "0x00"}, {"Operation": "0x00"}, {"Advertising_Data_Length": "0x08"}, {"Advertising_Data": "0x7665645f74736574", "length": 8}]],  # Todo: Advertising_Data: Advertising_Data_Length octets
    "LE Set Periodic Advertising Enable": ["0x0040", [{"Enable": "0x01"}, {"Advertising_Handle": "0x00"}]],
    "LE Set Extended Scan Parameters": [],
    "LE Set Extended Scan Enable": [],
    "LE Extended Create Connection": [],
    "LE Periodic Advertising Create Sync": [],
    "LE Periodic Advertising Create Sync Cancel": ["0x0045", []],
    "LE Periodic Advertising Terminate Sync command": ["0x0046", [{"Sync_Handle": "0x0eff", "length": 2}]],
    "LE Add Device To Periodic Advertiser List": ["0x0047", [{"Advertiser_Address_Type": "0x00"}, {"Advertiser_Address": "0x000000000000", "length": 6}, {"Advertising_SID": "0x0f"}]],
    "LE Remove Device From Periodic Advertiser List": ["0x0048", [{"Advertiser_Address_Type": "0x00"}, {"Advertiser_Address": "0x000000000000", "length": 6}, {"Advertising_SID": "0x0f"}]],
    "LE Clear Periodic Advertiser List": ["0x0049", []],
    "LE Read Periodic Advertiser List Size": ["0x004a", []],
    "LE Read Transmit Power": ["0x004b", []],
    "LE Read RF Path Compensation": ["0x004c", []],
    "LE Write RF Path Compensation": ["0x004d", [{"RF_TX_Path_Compensation_Value": "0xFB00", "length": 2}, {"RF_RX_Path_Compensation_Value": "0xFB00", "length": 2}]],
    "LE Set Privacy Mode": ["0x004e", [{"Peer_Identity_Address_Type": "0x00"}, {"Peer_Identity_Address": "0x000000000000", "length": 6}, {"Privacy_Mode": "0x00"}]],
    "LE Set Connectionless CTE Transmit Parameters": ["0x0051", [{"Advertising_Handle": "0x00"}, {"CTE_Length": "0x14"}, {"CTE_Type": "0x00"}, {"CTE_Count": "0x10"}, {"Switching_Pattern_Length": "0x02"}, {"Antenna_IDs": "0x0000", "length": 2}]],
    "LE Set Connectionless CTE Transmit Enable": [],
    "LE Set Connectionless IQ Sampling Enable": [],
    "LE Set Connection CTE Receive Parameters": [],
    "LE Set Connection CTE Transmit Parameters": [],
    "LE Connection CTE Request Enable": [],
    "LE Connection CTE Response Enable": [],
    "LE Read Antenna Information": [],
    "LE Set Periodic Advertising Receive Enable": [],
    "LE Periodic Advertising Sync Transfer": [],
    "LE Periodic Advertising Set Info Transfer": [],
    "LE Set Periodic Advertising Sync Transfer Parameters": [],
    "LE Set Default Periodic Advertising Sync Transfer Parameters": [],
    "LE Modify Sleep Clock Accuracy": [],
    "LE Read ISO TX Sync": [],
    "LE Set CIG Parameters": [],
    "LE Set CIG Parameters Test": [],
    "LE Create CIS": [],
    "LE Remove CIG": [],
    "LE Accept CIS Request": ["0x0066", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Reject CIS Request": ["0x0067", [{"Connection_Handle": "0x0000", "length": 2}, {"Reason": "0x1f"}]],
    "LE Create BIG": [],
    "LE Create BIG Test": [],
    "LE Terminate BIG": ["0x006A", [{"BIG_Handle": "0x00"}, {"Reason": "0x1f"}]],
    "LE BIG Create Sync": [],
    "LE BIG Terminate Sync": ["0x006c", [{"BIG_Handle": "0x00"}]],
    "LE Request Peer SCA": ["0x006d", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Setup ISO Data Path": [],
    "LE Remove ISO Data Path": ["0x006f", [{"Connection_Handle": "0x0000", "length": 2}, {"Data_Path_Direction": "0x01"}]],
    "LE ISO Transmit Test": ["0x0070", [{"Connection_Handle": "0x0000", "length": 2}, {"Payload_Type": "0x01"}]],
    "LE ISO Receive Test": ["0x0071", [{"Connection_Handle": "0x0000", "length": 2}, {"Payload_Type": "0x01"}]],
    "LE ISO Read Test Counters": ["0x0072", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE ISO Test End": ["0x0073", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Set Host Feature [v1]": ["0x0074", [{"Bit_Number": "0x00"}, {"Bit_Value": "0x01"}]],
    "LE Set Host Feature [v2]": ["0x0097", [{"Bit_Number": "0x0000", "length": 2}, {"Bit_Value": "0x01"}]],
    "LE Read ISO Link Quality": ["0x0075", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE Enhanced Read Transmit Power Level": ["0x0076", [{"Connection_Handle": "0x0000", "length": 2}, {"PHY": "0x01"}]],
    "LE Read Remote Transmit Power Level": ["0x0077", [{"Connection_Handle": "0x0000", "length": 2}, {"PHY": "0x01"}]],
    "LE Set Path Loss Reporting Parameters": [],
    "LE Set Path Loss Reporting Enable": ["0x0079", [{"Connection_Handle": "0x0000", "length": 2}, {"Enable": "0x01"}]],
    "LE Set Transmit Power Reporting Enable": ["0x007a", [{"Connection_Handle": "0x0000", "length": 2}, {"Local_Enable": "0x01"}, {"Remote_Enable": "0x01"}]],
    "LE Set Data Related Address Changes": [],
    "LE Set Default Subrate": [],
    "LE Subrate Request": [],
    "LE Set Periodic Advertising Subevent Data": [],
    "LE Set Periodic Advertising Response Data": [],
    "LE Set Periodic Sync Subevent": [],
    "LE Read All Local Supported Features": ["0x0087", []],
    "LE Read All Remote Features": ["0x0088", [{"Connection_Handle": "0x0000", "length": 2}, {"Pages_Requested": "0x00"}]],
    "LE CS Read Local Supported Capabilities": ["0x0089", []],
    "LE CS Read Remote Supported Capabilities": ["0x008a", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE CS Write Cached Remote Supported Capabilities": ["0x008b", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE CS Security Enable": ["0x008c", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE CS Set Default Settings": ["0x008d", [{"Connection_Handle": "0x0000", "length": 2}, {"Role_Enable": "0x01"}, {"CS_SYNC_Antenna_Selection": "0xff"}, {"Max_TX_Power": "0x0a"}]],
    "LE CS Read Remote FAE Table": ["0x008e", [{"Connection_Handle": "0x0000", "length": 2}]],
    "LE CS Write Cached Remote FAE Table": ["0x008f", [{"Connection_Handle": "0x0000", "length": 2}, {"Remote_FAE_Table": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "length": 72}]],
    "LE CS Create Config": ["0x0090", [{"Connection_Handle": "0x0000", "length": 2}, {"Config_ID": "0x02"}, {"Create_Context": "0x00"}, {"Main_Mode_Type": "0x01"}, {"Sub_Mode_Type": "0x01"}, {"Min_Main_Mode_Steps": "0x0a"}, {"Max_Main_Mode_Steps": "0x0b"}, {"Main_Mode_Repetition": "0x01"}, {"Mode_0_Steps": "0x01"}, {"Role": "0x00"}, {"RTT_Type": "0x00"}, {"CS_SYNC_PHY": "0x01"}, {"Channel_Map": "0xffffffffffffffffffff", "length": 10}, {"Channel_Map_Repetition": "0xff"}, {"Channel_Selection_Type": "0x00"}, {"Ch3c_Shape": "0x00"}, {"Ch3c_Jump": "0x02"}, {"Reserved": "0x00"}]],
    "LE CS Remove Config": ["0x0091", [{"Connection_Handle": "0x0000", "length": 2}, {"Config_ID": "0x02"}]],
    "LE CS Set Channel Classification": ["0x0092", {"Channel_Classification": "0x7fffffffffffffffffff", "length": 10}],
    "LE CS Set Procedure Parameters": ["0x0093", [{"Connection_Handle": "0x0000", "length": 2}, {"Config_ID": "0x02"}, {"Max_Procedure_Len": "0xFFFF", "length": 2}, {"Min_Procedure_Interval": "0xffff", "length": 2}, {"Max_Procedure_Interval": "0xffff", "length": 2}, {"Max_Procedure_Count": "0x00ff", "length": 2}, {"Min_Subevent_Len": "0x000fff", "length": 3}, {"Max_Subevent_Len": "0x00ffff", "length": 3}, {"Tone_Antenna_Config_Selection": "0x02"}, {"PHY": "0x01"}, {"Tx_Power_Delta": "0x80"}, {"Preferred_Peer_Antenna": "0x01"}, {"SNR_Control_Initiator": "0x00"}, {"SNR_Control_Reflector": "0x00"}]],
    "LE CS Procedure Enable": ["0x0094", [{"Connection_Handle": "0x0000", "length": 2}, {"Config_ID": "0x02"}, {"Enable": "0x01"}]],
    "LE CS Test": ["0x0095", [{"Main_Mode_Type": "0x01"}, {"Sub_Mode_Type": "0x01"}, {"Main_Mode_Repetition": "0x00"}, {"Mode_0_Steps": "0x03"}, {"Role": "0x00"}, {"RTT_Type": "0x00"}, {"CS_SYNC_PHY": "0x01"}, {"CS_SYNC_Antenna_Selection": "0x02"}, {"Subevent_Len": "0x0000ff", "length": 3}, {"Subevent_Interval": "0x0000", "length": 2}, {"Max_Num_Subevents": "0x00"}, {"Transmit_Power_Level": "0x7f"}, {"T_IP1_Time": "0x0a"}, {"T_IP2_Time": "0x14"}, {"T_FCS_Time": "0x1e"}, {"T_PM_Time": "0x28"}, {"T_SW_Time": "0x01"}, {"Tone_Antenna_Config_Selection": "0x07"}, {"Reserved": "0x00"}, {"SNR_Control_Initiator": "0x00"}, {"SNR_Control_Reflector": "0x01"}, {"DRBG_Nonce": "0x0001", "length": 2}, {"Channel_Map_Repetition": "0xff"}, {"Override_Config": "0x000f", "length": 2}, {"Override_Parameters_Length": "0x01"}, {"Override_Parameters_Data": "0x11"}]],  # Todo: Override_Parameters_Data: Override_Parameters_Length octets
    "LE CS Test End": ["0x0096", []],
    "LE Set Decision Data": ["0x0080", [{"Advertising_Handle": "0x00"}, {"Decision_Type_Flags": "0x01"}, {"Decision_Data_Length": "0x02"}, {"Decision_Data": "0x1111", "length": 2}]],  # Todo: Decision_Data: Decision_Data_Length octets
    "LE Set Decision Instructions": ["0x0081", [{"Num_Tests": "0x01"}, {"Test_Flags": "0x01"}, {"Test_Field": "0x20"}, {"Test_Parameters": "0x1234567890abcdef1234567890abcdef", "length": 16}]],  # Todo: (Test_Flags[i]: Num_Tests × 1 octet) (Test_Field[i]: Num_Tests × 1 octet) (Test_Parameters[i]: Num_Tests × 16 octets)
    "LE Add Device To Monitored Advertisers List": ["0x0098", [{"Address_Type": "0x00"}, {"Address": "0x000000000000", "length": 6}, {"RSSI_Threshold_Low": "0x0a"}, {"RSSI_Threshold_High": "0xaa"}, {"Timeout": "0x01"}]],
    "LE Remove Device From Monitored Advertisers List": ["0x0099", [{"Address_Type": "0x00"}, {"Address": "0x000000000000", "length": 6}]],
    "LE Clear Monitored Advertisers List": ["0x009a", []],
    "LE Enable Monitoring Advertisers": ["0x009c", [{"Enable": "0x01"}]],
    "LE Read Monitored Advertisers List Size": ["0x009B", []],
    "LE Frame Space Update": ["0x009d", [{"Connection_Handle": "0x0000", "length": 2}, {"Frame_Space_Min": "0x2710", "length": 2}, {"Frame_Space_Max": "0x2710", "length": 2}, {"PHYS": "0x01"}, {"Spacing_Types": "0x001f", "length": 2}]]
}

{"Num_Config_Supported": "0x04"},
{"Max_Consecutive_Procedures_Supported": "0x0000", "length": 2},
{"Num_Antennas_Supported": "0x01"},
{"Max_Antenna_Paths_Supported": "0x01"},
{"Roles_Supported": "0x01"},
{"Modes_Supported": "0x01"},
{"RTT_Capability": "0x01"},
{"RTT_AA_Only_N": "0x01"},
{"RTT_Sounding_N": "0x01"},
{"RTT_Random_Payload_N": ""},
{"NADM_Sounding_Capability"},
{"NADM_Random_Capability"},
{"CS_SYNC_PHYs_Supported"},
{"Subfeatures_Supported"},
{"T_IP1_Times_Supported"},
{"T_IP2_Times_Supported"},
{"T_FCS_Times_Supported"},
{"T_PM_Times_Supported"},
{"T_SW_Time_Supported"},
{"TX_SNR_Capability"}
