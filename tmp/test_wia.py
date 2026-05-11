import win32com.client
import pythoncom
import sys

def test_wia():
    print("Testing WIA...")
    try:
        pythoncom.CoInitialize()
        device_manager = win32com.client.Dispatch("WIA.DeviceManager")
        print(f"DeviceManager found. Connection count: {device_manager.DeviceInfos.Count}")
        for device_info in device_manager.DeviceInfos:
            print(f"Device: {device_info.Properties('Name').Value} (Type: {device_info.Type})")
            if device_info.Type == 1:
                print("Scanner found. Testing connect...")
                try:
                    scanner = device_info.Connect()
                    print("Successfully connected to scanner.")
                    print(f"Scanner Items: {scanner.Items.Count}")
                    if scanner.Items.Count > 0:
                        print("Found scan items.")
                    else:
                        print("No scan items found. This might be why Items[1] fails.")
                except Exception as e:
                    print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    test_wia()
