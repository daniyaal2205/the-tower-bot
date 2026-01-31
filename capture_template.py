import subprocess
import os
import sys
import time

# Verify ADB path
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
adb_dir = os.path.join(script_dir, "platform-tools")
if os.path.isdir(adb_dir):
    os.environ["PATH"] = adb_dir + os.pathsep + os.environ["PATH"]

def get_connected_device():
    try:
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]: 
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                return parts[0]
    except Exception as e:
        print(f"Error checking devices: {e}")
    return None

def main():
    print("--- TEMPLATE CAPTURE TOOL ---")
    print("This tool will take a screenshot of your emulator.")
    print("Use the generated image to crop your buttons!")
    print("----------------------------")
    
    print("Checking for connected device...")
    device_id = get_connected_device()
    
    if not device_id:
        print("Error: No device found! Make sure emulator is running.")
        input("Press Enter to exit...")
        return
        
    print(f"Connected to: {device_id}")

    print("Capturing screen...")
    try:
        # Capture to temp location
        subprocess.run(f"adb -s {device_id} shell screencap -p /data/local/tmp/template_source.png", shell=True, check=True)
        # Pull to computer
        subprocess.run(f"adb -s {device_id} pull /data/local/tmp/template_source.png TEMPLATE_SOURCE.png", shell=True, check=True)
        
        print("\nSUCCESS!")
        print(f"Image saved as: {os.path.join(script_dir, 'TEMPLATE_SOURCE.png')}")
        print("\nINSTRUCTIONS:")
        print("1. Open 'TEMPLATE_SOURCE.png' in Paint or Photos.")
        print("2. Crop the buttons (Start Battle.png, Defence.png, etc.).")
        print("3. Save them into 'The Tower Buttons' folder.")
        print("   (Overwrite the old ones!)")
        
    except Exception as e:
        print(f"Error: {e}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
