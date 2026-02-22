import PyInstaller.__main__
import os
import sys
import platform

# Automatically build the Pyinstaller executable commands based on OS

def build_executable():
    print(f"--- Starting Build Process for Amazon Auto-Shift Picker ---")
    
    # Base Pyinstaller Arguments
    args = [
        'gui_app.py', # The main entry point 
        '--name=Amazon_Shift_Picker', 
        '--noconsole', # Do not show the terminal window behind the GUI
        '--clean',
        '--noconfirm',
        '--add-data=config.json;.', # Default Config
        '--add-data=AtoZ-Bot.py;.', # Bot Script itself
        '--collect-all=selenium',
        '--collect-all=undetected_chromedriver',
        '--hidden-import=requests',
        '--collect-all=certifi',
        '--hidden-import=flet_desktop', 
        '--collect-all=flet_desktop',
        '--collect-all=flet',
    ]
    
    # OS Specific adjustments
    if platform.system() == "Windows":
        print("Detected Windows OS. Building .exe")
        # Ensure we add a semicolon for windows, colon for mac
        args = [arg.replace(';.', ';.') for arg in args]
        # Optional: Add an icon here if requested later
        # args.append('--icon=app_icon.ico') 
    elif platform.system() == "Darwin":
         print("Detected macOS. Building .app")
         # macOS requires colon separator for add-data
         args = [arg.replace(';.', ':.') for arg in args]
         
         # Note: We do NOT use --windowed for Flet apps on macOS that spawn subprocesses or need stdout visibility. 
         # Flet natively runs in its own window anyway. `--windowed` (which implies `--noconsole`) 
         # often causes instant crashes on macOS for complex GUI wrappers. 
         
         # Ad-hoc codesign the .app bundle to prevent macOS Gatekeeper from killing it instantly
         args.append('--codesign-identity=-')
         
    try:
        PyInstaller.__main__.run(args)
        print("\n=== BUILD SUCCESSFUL ===")
        print("Your standalone executable is located in the 'dist' folder.")
    except Exception as e:
        print(f"\n=== BUILD FAILED ===")
        print(f"Error: {e}")

if __name__ == "__main__":
    build_executable()
