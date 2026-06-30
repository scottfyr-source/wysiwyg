import os
import sys
import subprocess

def main():
    try:
        import PyInstaller.__main__
    except ImportError:
        print("PyInstaller is not installed. Attempting to install it using pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            import PyInstaller.__main__
        except Exception as e:
            print(f"Failed to install PyInstaller: {e}")
            sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(base_dir, "apicurl.py")
    parent_dir = os.path.abspath(os.path.join(base_dir, '..'))
    sep = os.pathsep

    # Basic PyInstaller arguments
    args = [
        main_script,
        '--name=WysiWyg',
        '--onefile',
        '--windowed',  # No console window
        '--noconfirm', # Overwrite output directory without confirming
    ]

    # Include common web app asset files if they exist
    for asset in ["index.html", "script.js", "styles.css", "common_ui.js", "menu.html", "progress_bar.html", "log_terminal.html", "notification_center.html"]:
        path = os.path.join(base_dir, asset)
        if os.path.exists(path):
            args.append(f'--add-data={path}{sep}.')

    # Include assets directory if it exists
    assets_dir = os.path.join(base_dir, "assets")
    if os.path.isdir(assets_dir):
        args.append(f'--add-data={assets_dir}{sep}assets')

    # Include shared Xenohead templates/JS directories if they exist
    for folder in [
        os.path.join(parent_dir, "Xeno_ui", "templates"),
        os.path.join(parent_dir, "xeno_ui", "templates")
    ]:
        if os.path.isdir(folder):
            args.append(f'--add-data={folder}{sep}Xeno_ui{os.sep}templates')
            
    for folder in [
        os.path.join(parent_dir, "Xeno_ui", "js"),
        os.path.join(parent_dir, "xeno_ui", "js")
    ]:
        if os.path.isdir(folder):
            args.append(f'--add-data={folder}{sep}Xeno_ui{os.sep}js')

    # Convert local JPG/PNG icon to ICO format and remove solid background if needed
    icon_source = None
    icon_candidates = [
        "apicurl_icon.png",
        "apicurl_icon.jpg",
        "icon.png",
        "icon.jpg",
        "logo.png",
        "logo.jpg"
    ]
    for img_name in icon_candidates:
        path = os.path.join(base_dir, img_name)
        if os.path.exists(path):
            icon_source = path
            break
            
    ico_output = os.path.join(base_dir, "fyr-logo.ico")
    if icon_source and not os.path.exists(ico_output):
        try:
            try:
                from PIL import Image
            except ImportError:
                print("Pillow is not installed. Attempting to install it using pip...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
                from PIL import Image
            print(f"Converting {os.path.basename(icon_source)} to {os.path.basename(ico_output)} and removing solid background...")
            img = Image.open(icon_source).convert("RGBA")
            
            # Simple background removal by keying out the top-left pixel color
            data = img.getdata()
            bg_color = data[0]
            new_data = []
            tolerance = 25  # color distance tolerance
            for item in data:
                # distance to background color
                dist = ((item[0] - bg_color[0])**2 + (item[1] - bg_color[1])**2 + (item[2] - bg_color[2])**2)**0.5
                if dist <= tolerance:
                    new_data.append((item[0], item[1], item[2], 0))  # transparent
                else:
                    new_data.append(item)
            img.putdata(new_data)
            
            img.save(ico_output, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"Icon converted and background removed successfully.")
        except Exception as e:
            print(f"Warning: Failed to convert icon: {e}")

    # Add icon argument if exists
    ico_path = os.path.join(base_dir, "fyr-logo.ico")
    if os.path.exists(ico_path):
        args.append(f'--icon={ico_path}')
        args.append(f'--add-data={ico_path}{sep}.')

    # Include logo file
    logo_path = os.path.join(base_dir, "Capture.PNG")
    if os.path.exists(logo_path):
        args.append(f'--add-data={logo_path}{sep}.')

    # Add parent directory to path resolving if needed
    args.append(f'--paths={parent_dir}')

    # Common hidden imports
    args.extend([
        '--hidden-import=webview',
        '--hidden-import=requests',
        '--hidden-import=Xeno_ui',
        '--hidden-import=xeno_ui',
        '--hidden-import=ipc_server',
        '--hidden-import=tkinter'
    ])

    print("Building WysiWyg with Pyinstaller...")
    PyInstaller.__main__.run(args)
    print("\nBuild complete! Check the 'dist' folder for your executable.")

if __name__ == "__main__":
    main()
