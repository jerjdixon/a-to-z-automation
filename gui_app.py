import flet as ft
import json
import os
import subprocess
import threading
import sys
import traceback

def get_base_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

# config.json should ideally sit NEXT TO the executable, so users can edit it manually if they want,
# but we bundle the default one inside _MEIPASS.
# Actually, for settings that save, writing into the read-only _MEIPASS temp dir is bad practice.
# We should try to read/write config.json to the directory the executable actually sits in,
# or user's appdata, but the simplest cross-platform way for a portable app is next to the exe.
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    EXECUTABLE_DIR = os.path.dirname(sys.executable)
    CONFIG_FILE = os.path.join(EXECUTABLE_DIR, "config.json")
    
    # If a config doesn't exist next to the .exe yet, copy the bundled default one over
    if not os.path.exists(CONFIG_FILE):
        import shutil
        bundled_config = os.path.join(sys._MEIPASS, "config.json")
        if os.path.exists(bundled_config):
            shutil.copy(bundled_config, CONFIG_FILE)
            
    BOT_SCRIPT = os.path.join(sys._MEIPASS, "AtoZ-Bot.py") # Bot script is bundled inside
else:
    # Running normally from python script
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    BOT_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AtoZ-Bot.py")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {CONFIG_FILE}: {e}")
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def main(page: ft.Page):
    page.title = "Amazon Shift Picker Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 850
    page.window_height = 800
    page.padding = 0
    page.bgcolor = "#121212"
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    }
    
    page.theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(
            primary="#FF9900",       # Amazon Orange
            secondary="#146eb4",     # Amazon Blue
            background="#121212", 
            surface="#1E1E1E",
            on_surface="#E0E0E0"
        )
    )

    config = load_config()

    # Form Fields Styling
    input_style = {"border_color": "transparent", "bgcolor": "#2c2c2c", "border_radius": 8, "filled": True, "expand": True, "on_change": lambda e: handle_save()}

    login_input = ft.TextField(label="Amazon Login", value=config.get("Amazon_Login", ""), **input_style)
    earliest_time_input = ft.TextField(label="Earliest Time (HH:MM)", value=config.get("EARLIEST_TIME", "00:00"), **input_style)
    latest_time_input = ft.TextField(label="Latest Time (HH:MM)", value=config.get("LATEST_TIME", "23:59"), **input_style)
    longest_shift_input = ft.TextField(label="Max Shift Length (Hours)", value=str(config.get("LONGEST_SHIFT", 10)), **input_style)
    hours_to_run_input = ft.TextField(label="Hours to Run", value=str(config.get("HOURS_TO_RUN", 48)), **input_style)
    seconds_between_checks_input = ft.TextField(label="Seconds Between Checks", value=str(config.get("SECONDS_BETWEEN_CHECKS", 15)), **input_style)
    
    weekdays_controls = []
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_days = config.get("WEEKDAYS", [])
    for day in days_of_week:
        cb = ft.Checkbox(label=day, value=(day in selected_days), fill_color=ft.colors.PRIMARY, on_change=lambda e: handle_save())
        weekdays_controls.append(cb)

    bot_process = None

    log_output = ft.ListView(expand=True, spacing=5, auto_scroll=True)
    
    def log_message(msg):
        log_output.controls.append(ft.Text(msg, selectable=True, font_family="Consolas"))
        page.update()

    def read_output(proc):
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            # Use call_soon to safely update UI from background thread (optional, but good practice in flet)
            log_message(line.strip())
        proc.wait()
        log_message("--- Bot process terminated ---")
        page.update()

    def start_bot(e):
        nonlocal bot_process
        if bot_process is not None and bot_process.poll() is None:
            log_message("Bot is already running.")
            return

        try:
            bot_process = subprocess.Popen(
                [sys.executable, "-u", BOT_SCRIPT],  # '-u' forces unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            # Daemon thread to read stdout
            threading.Thread(target=read_output, args=(bot_process,), daemon=True).start()
            
            start_btn.disabled = True
            stop_btn.disabled = False
            log_message("--- Bot Started ---")
        except Exception as ex:
            log_message(f"Failed to start bot: {ex}")
            log_message(traceback.format_exc())
            
        page.update()

    def stop_bot(e):
        nonlocal bot_process
        if bot_process is not None and bot_process.poll() is None:
            bot_process.terminate()
            log_message("--- Stop signal sent to bot ---")
        
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    def handle_save(e=None):
        try:
            config["Amazon_Login"] = login_input.value
            config["EARLIEST_TIME"] = earliest_time_input.value
            config["LATEST_TIME"] = latest_time_input.value
            try:
                config["LONGEST_SHIFT"] = float(longest_shift_input.value)
            except ValueError:
                pass # Ignore incomplete typing errors for numbers
            
            try:
                config["HOURS_TO_RUN"] = float(hours_to_run_input.value)
            except ValueError:
                pass
                
            try:
                config["SECONDS_BETWEEN_CHECKS"] = int(seconds_between_checks_input.value)
            except ValueError:
                pass

            selected = [cb.label for cb in weekdays_controls if cb.value]
            config["WEEKDAYS"] = selected
            
            save_config(config)
        except Exception as ex:
            snack = ft.SnackBar(ft.Text(f"Error saving settings: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar = snack
            snack.open = True
            page.update()

    # Modern Buttons
    start_btn = ft.ElevatedButton(
        "Start Automation", 
        on_click=start_bot, 
        icon=ft.icons.PLAY_ARROW_ROUNDED, 
        style=ft.ButtonStyle(
            color=ft.colors.WHITE, 
            bgcolor=ft.colors.PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20
        ),
        expand=True
    )
    stop_btn = ft.ElevatedButton(
        "Stop Bot", 
        on_click=stop_bot, 
        icon=ft.icons.STOP_ROUNDED, 
        disabled=True, 
        style=ft.ButtonStyle(
            color=ft.colors.WHITE, 
            bgcolor=ft.colors.ERROR,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=20
        ),
        expand=True
    )

    def create_card(title, content_controls):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Container(height=5),
                *content_controls
            ]),
            bgcolor=ft.colors.SURFACE,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, "#333333"),
            margin=ft.margin.only(bottom=15)
        )

    # Main Layout Assembly
    dashboard = ft.Row([
        # Left Side: Settings
        ft.Container(
            expand=4,
            padding=25,
            content=ft.Column([
                ft.Text("Configuration", size=24, weight=ft.FontWeight.W_800, color=ft.colors.PRIMARY),
                ft.Container(height=10),
                create_card("Execution Settings", [
                    ft.Row([hours_to_run_input, seconds_between_checks_input])
                ]),
                create_card("Login Information", [login_input]),
                create_card("Shift Preferences", [
                    ft.Row([earliest_time_input, latest_time_input]),
                    ft.Container(height=5),
                    longest_shift_input,
                    ft.Container(height=10),
                    ft.Text("Active Days:", size=14, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE),
                    ft.Row(weekdays_controls, wrap=True)
                ])
            ], scroll=ft.ScrollMode.AUTO)
        ),
        
        # Right Side: Console and Controls
        ft.Container(
            expand=5,
            padding=25,
            bgcolor="#171717",
            border=ft.border.only(left=ft.border.BorderSide(1, "#333333")),
            content=ft.Column([
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.W_800, color=ft.colors.WHITE),
                ft.Container(height=10),
                ft.Row([start_btn, stop_btn]),
                ft.Container(height=20),
                ft.Text("Live Protocol Console", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                ft.Container(
                    content=log_output,
                    expand=True,
                    bgcolor="#0A0A0A",
                    border_radius=12,
                    padding=15,
                    border=ft.border.all(1, "#222222")
                )
            ])
        )
    ], expand=True, spacing=0)

    page.add(dashboard)

    # Clean up on exit
    def window_event(e):
        if e.data == "close":
            if bot_process is not None and bot_process.poll() is None:
                bot_process.terminate()
            page.window_destroy()

    page.on_window_event = window_event
    page.window_prevent_close = True

if __name__ == "__main__":
    ft.app(target=main)
