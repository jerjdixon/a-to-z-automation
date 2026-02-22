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
        '--hidden-import=flet_desktop', 
        '--collect-all=flet_desktop',
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
         args.append('--windowed')
         
    try:
        PyInstaller.__main__.run(args)
        print("\n=== BUILD SUCCESSFUL ===")
        print("Your standalone executable is located in the 'dist' folder.")
    except Exception as e:
        print(f"\n=== BUILD FAILED ===")
        print(f"Error: {e}")

if __name__ == "__main__":
    build_executable()
