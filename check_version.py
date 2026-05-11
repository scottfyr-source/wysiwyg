import json
import os
import shutil
import sys

# Configuration
SERVER_DIR = r"\\192.168.0.108\FYRShare\Tools\FYRTools\WYSIWYG"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_TO_SYNC = ["version.json", "changelog.txt"]

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return None

def get_version_tuple(data):
    if not data: return (0,0,0,0)
    return (
        int(data.get('major', 0)),
        int(data.get('minor', 0)),
        int(data.get('patch', 0)),
        int(data.get('build', 0))
    )

def main():
    print("--- Version Check ---")
    
    if not os.path.exists(SERVER_DIR):
        print(f"Server path not found: {SERVER_DIR}")
        print("Skipping version check (Offline Mode).")
        return

    local_v_path = os.path.join(LOCAL_DIR, "version.json")
    server_v_path = os.path.join(SERVER_DIR, "version.json")

    local_data = load_json(local_v_path)
    server_data = load_json(server_v_path)

    if not server_data:
        print("Server version.json missing. Skipping check.")
        return

    l_ver = get_version_tuple(local_data)
    s_ver = get_version_tuple(server_data)

    l_str = ".".join(map(str, l_ver))
    s_str = ".".join(map(str, s_ver))

    print(f"Local Version:  {l_str}")
    print(f"Server Version: {s_str}")

    if s_ver > l_ver:
        print("\n" + "!"*60)
        print("WARNING: Your local version is OLDER than the server version.")
        print("!"*60)
        print("You should pull the latest version info before building.")
        
        choice = input("\nDo you want to PULL version.json and changelog.txt from server? (y/n): ")
        if choice.lower() == 'y':
            print("Syncing files...")
            for fname in FILES_TO_SYNC:
                src = os.path.join(SERVER_DIR, fname)
                dst = os.path.join(LOCAL_DIR, fname)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"Pulled: {fname}")
                else:
                    print(f"Missing on server: {fname}")
            print("Sync complete. Proceeding with build...")
        else:
            print("Proceeding with older local version...")
    elif l_ver > s_ver:
        print("Local version is NEWER. You are building an update.")
    else:
        print("Versions match.")
    
    print("-" * 20 + "\n")

if __name__ == "__main__":
    main()