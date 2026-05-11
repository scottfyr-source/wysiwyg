import os
import sys
import time
import shutil
import subprocess

# Determine the directory where this script (or compiled exe) is running
if getattr(sys, 'frozen', False):
    SOURCE_DIR = os.path.dirname(sys.executable)
else:
    SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration
DEST_FOLDER = r"C:\FYRTOOLS\WYSIWYG"
SHORTCUT_NAME = "WYSIWYG.lnk"
FILES_TO_INSTALL = [
    "WYSIWYG.exe",
    "index.html",
    "editor.html",
    "admin.html",
    "search.html",
    "data.json",
    "fyrlogo.png",
    "fyr-logo.ico",
    "media_formats.json",
    "version.json",
    "changelog.txt",
    "styles.css",
    "style_guide.html",
    "walmart.html",
    "walmart.js"
]

SUB_DIRECTORIES_TO_INSTALL = [
    "WalmartSheet",
    "UberPaste",
    "WysiScan"
]

def install():
    print(f"Installer running from: {SOURCE_DIR}")
    print(f"Installing to: {DEST_FOLDER}")
    
    try:
        # 0. Close application if running
        print("Closing any running instances...")
        os.system('taskkill /F /IM WYSIWYG.exe >nul 2>&1')
        time.sleep(1) # Give Windows a moment to release the file handle

        # 1. Create the local directory
        if not os.path.exists(DEST_FOLDER):
            os.makedirs(DEST_FOLDER)
            print(f"Created folder: {DEST_FOLDER}")

        # 2. Copy files
        for filename in FILES_TO_INSTALL:
            src = os.path.join(SOURCE_DIR, filename)
            dst = os.path.join(DEST_FOLDER, filename)
            
            if os.path.exists(src):
                # Retry loop for locked files
                for attempt in range(5):
                    try:
                        print(f"Copying {filename} (Attempt {attempt+1})...")
                        shutil.copy2(src, dst)
                        break
                    except PermissionError:
                        if attempt < 4:
                            print(f"File locked. Waiting 2 seconds...")
                            time.sleep(2)
                        else:
                            print(f"ERROR: Could not copy {filename}. It may be in use.")
                            raise
            else:
                print(f"WARNING: Source file not found: {filename}")

        # 3. Copy subdirectories
        for subdir in SUB_DIRECTORIES_TO_INSTALL:
            src_dir = os.path.join(SOURCE_DIR, subdir)
            dst_dir = os.path.join(DEST_FOLDER, subdir)
            if os.path.isdir(src_dir):
                print(f"Copying directory {subdir}...")
                try:
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
                except Exception as e:
                    print(f"WARNING: Could not copy directory {subdir}: {e}")
            else:
                print(f"WARNING: Source directory not found: {src_dir}")

        # 4. Copy the existing Shortcut
        shortcut_src = os.path.join(SOURCE_DIR, SHORTCUT_NAME)
        
        user_desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        user_startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        
        targets = [os.path.join(user_desktop, SHORTCUT_NAME), os.path.join(user_startup, SHORTCUT_NAME)]

        if os.path.exists(shortcut_src):
            print(f"Copying shortcut from {shortcut_src}...")
            for target in targets:
                try:
                    shutil.copy2(shortcut_src, target)
                    print(f"Copied shortcut to: {target}")
                except Exception as e:
                    print(f"Failed to copy to {target}: {e}")
        else:
            print(f"WARNING: Source shortcut not found at {shortcut_src}")

        # 6. Share the FYRTOOLS folder
        try:
            print("Configuring Network Share for C:\\FYRTOOLS...")
            # Shares C:\FYRTOOLS as "FYRTOOLS" with Read access for Everyone
            subprocess.run('net share FYRTOOLS="C:\\FYRTOOLS" /GRANT:Everyone,READ', shell=True)
        except Exception as e:
            print(f"Share configuration warning (requires Admin): {e}")

        # 7. Launch the application
        exe_path = os.path.join(DEST_FOLDER, "WYSIWYG.exe")
        if os.path.exists(exe_path):
            print("Launching WYSIWYG...")
            time.sleep(2)
            os.startfile(exe_path)
       
    except Exception as e:
        print(f"Error during installation: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    install() 