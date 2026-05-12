import PyInstaller.__main__
import os
import sys

def build_exe():
    # Ensure we are in the correct directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    script_name = "scanner_server.py"
    exe_name = "WysiScan"
    icon_path = "WysiScan.ico"

    # Define assets to bundle (source, destination inside EXE)
    # We place them in a 'WysiScan' folder inside the EXE to match scanner_server.py's ASSET_DIR logic
    assets = [
        ("scanner_test.html", "WysiScan"),
        ("WysiScan.ico", "WysiScan"),
        ("WysiScan.png", "WysiScan"),
    ]

    params = [
        script_name,
        "--onefile",
        "--noconsole",
        f"--name={exe_name}",
        f"--icon={icon_path}",
        "--clean",
    ]

    # Add assets
    for src, dst in assets:
        if os.path.exists(os.path.join(base_dir, src)):
            params.append(f"--add-data={src}{os.pathsep}{dst}")

    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    build_exe()