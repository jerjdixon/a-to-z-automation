import time
import random
import json
import ctypes
import os
import sys
import subprocess
import ssl
import certifi
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SSL_CERT_DIR'] = os.path.dirname(certifi.where())
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def get_base_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

if getattr(sys, 'frozen', False):
    EXECUTABLE_DIR = os.path.dirname(sys.executable)
    CONFIG_FILE = os.path.join(EXECUTABLE_DIR, "config.json")
    # Chrome profile should sit next to executable so it persists across runs!
    CHROME_PROFILE_DIRECTORY_PATH = os.path.join(EXECUTABLE_DIR, "ChromeBotProfile")
else:
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    CHROME_PROFILE_DIRECTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ChromeBotProfile")

def load_config():
    default_config = {
        "STALL_AFTER_LOGIN": 2,
        "EARLIEST_TIME": "18:15",
        "LATEST_TIME": "18:30",
        "LONGEST_SHIFT": 10,
        "WEEKDAYS": [
            "Monday",
            "Tuesday",
            "Sunday"
        ],
        "Amazon_Login": "jerdix",
        "HOURS_TO_RUN": 48,
        "SECONDS_BETWEEN_CHECKS": 15
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

app_config = load_config()

STALL_AFTER_LOGIN = app_config.get("STALL_AFTER_LOGIN", 2)
EARLIEST_TIME = app_config.get("EARLIEST_TIME", "18:15")
LATEST_TIME = app_config.get("LATEST_TIME", "18:30")
LONGEST_SHIFT = app_config.get("LONGEST_SHIFT", 10)
WEEKDAYS = app_config.get("WEEKDAYS", [])
Amazon_Login = app_config.get("Amazon_Login", "jerdix")
HOURS_TO_RUN = app_config.get("HOURS_TO_RUN", 48)
SECONDS_BETWEEN_CHECKS = app_config.get("SECONDS_BETWEEN_CHECKS", 15)

# Automatically set the search window from today to 30 days in the future
today = datetime.now()
START_DATE = today.strftime("%b %d") 
END_DATE = (today + timedelta(days=30)).strftime("%b %d") 

LOGIN_URL = "https://atoz-login.amazon.work"

HOMEPAGE_IDENTIFIER = "//*[@id='atoz-app-root']/div[2]/div[1]/div[3]/h2"
MENU_BURGER = "//*[@id='atoz-global-nav-header']/div/div/header/div/div/nav/ul/li[1]/button"

# Windows API Constants for preventing sleep
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

mac_caffeinate_process = None

def prevent_sleep():
    """Prevent the computer and display from going to sleep on Windows and Mac."""
    global mac_caffeinate_process
    try:
        if sys.platform == "win32":
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            print("System & Display sleep prevention enabled (Windows).")
        elif sys.platform == "darwin":
            mac_caffeinate_process = subprocess.Popen(["caffeinate", "-d"])
            print("System & Display sleep prevention enabled (macOS).")
    except Exception as e:
        print(f"Could not prevent sleep: {e}")

def allow_sleep():
    """Allow the computer to go to sleep again."""
    global mac_caffeinate_process
    try:
        if sys.platform == "win32":
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            print("System sleep prevention disabled (Windows).")
        elif sys.platform == "darwin" and mac_caffeinate_process:
            mac_caffeinate_process.terminate()
            mac_caffeinate_process = None
            print("System sleep prevention disabled (macOS).")
    except Exception as e:
        pass

def get_date_object(date_str):
    try:
        # Appending a leap-year-safe dummy year (2024) bypasses the Python deprecation warning
        dt = datetime.strptime(f"{date_str} 2024", "%b %d %Y")
        now = datetime.now()
        year = now.year
        
        if now.month == 12 and dt.month == 1:
            year += 1
        elif now.month == 1 and dt.month == 12:
            year -= 1
            
        return dt.replace(year=year)
    except ValueError:
        return None

class Browser:
    def __init__(self):
        self.options = ChromeOptions()
        
        if CHROME_PROFILE_DIRECTORY_PATH:
            self.options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIRECTORY_PATH}")
            
        self.driver = uc.Chrome(options=self.options)
        self.driver.get(LOGIN_URL)
        self.wait = WebDriverWait(self.driver, 10)
        
    def wait_and_click(self, element):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(element))
        time.sleep(random.uniform(0.3, 0.7))
        element.click()

    def delay_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0, 0.1))

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, HOMEPAGE_IDENTIFIER))
            )
            return True 
        except Exception as error:
            return False

    def login(self):
        print("Checking for existing session...")

        if self.is_logged_in():
            print("Already logged in! Skipping login sequence.")
            return  

        print("Session not found. Attempting login...")

        try:
            uname = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='associate-login-input']"))
            )
            self.delay_typing(uname, Amazon_Login)

            login_button = self.driver.find_element(By.XPATH, "//*[@id='login-form-login-btn']")
            self.wait_and_click(login_button)
            
            try:
                short_wait = WebDriverWait(self.driver, 5) 
                short_wait.until(EC.presence_of_element_located((By.XPATH, HOMEPAGE_IDENTIFIER)))
                print("Login successful after first step! bypassing secondary steps.")
                return 
            except:
                print("Homepage not detected immediately. Proceeding to secondary login...")

        except Exception as error:
            print(f"Error during Step 1 | {error}")

        try:
            uname2 = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='input-id-4']"))
            )
            self.delay_typing(uname2, Amazon_Login)

            login_button2 = self.driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/div/div[2]/div/button")
            self.wait_and_click(login_button2)

        except Exception as error:
            pass 

        try:
            passkey_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div[1]/div[2]/div/div[2]/div[2]/div[1]/button"))
            )
            self.wait_and_click(passkey_element)
            
            print("--- MANUAL INTERACTION REQUIRED ---")
            print("Please complete the Windows Hello/Security Key prompt in the browser.")
            
        except Exception as error:
            pass

        print(f"Waiting for homepage element: {HOMEPAGE_IDENTIFIER}")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, HOMEPAGE_IDENTIFIER))
            )
            print("Login Successful! Homepage detected. Resuming script...")

        except TimeoutException: 
            print("Timed out waiting for login. Exiting.")
            self.driver.quit()
            exit()
    
    def save_cookies(self):
        cookies = self.driver.get_cookies()
        json.dump(cookies, open("cookies", "wt", encoding="utf8"))

    def exit(self):
        self.driver.quit()

    def back_home(self):
        try:
            menu_burger = self.wait.until(
                EC.presence_of_element_located((By.XPATH, MENU_BURGER))
            )
            menu_burger.click()
            
            # Fixed the slide-out menu crash by waiting for the element to become clickable
            home_nav_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='side-nav-item-top-level-home_nav_item_0']"))
            )
            time.sleep(0.5)
            home_nav_button.click()
        except Exception as e:
            print(f"Error returning home: {e}")

    def find_shifts(self):
        print("Attempting to navigate to shifts...")
        
        try:
            burger_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='atoz-global-nav-header']/div/div/header/div/div/nav/ul/li[1]/button"))) 
            burger_menu.click()

            schedule_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/nav/div[2]/div/ul/li[2]/button")))
            schedule_button.click()

            find_shifts_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/div/nav/div[2]/div/ul/li[2]/div/ul/li[4]/div/a"))) 
            find_shifts_button.click()
            print("Navigated to Find Shifts.")

        except Exception as e:
            print(f"Navigation failed: {e}")
            return 
        
        print(f"Checking schedule from {START_DATE} to {END_DATE}...")

        start_dt = get_date_object(START_DATE)
        end_dt = get_date_object(END_DATE)

        if not start_dt or not end_dt:
            print("ERROR: START_DATE or END_DATE is invalid or empty. Please check config.")
            return

        for i in range(1, 60):
            current_config = load_config()
            current_weekdays = current_config.get("WEEKDAYS", [])
            current_longest_shift = current_config.get("LONGEST_SHIFT", 10)
            current_earliest_time = current_config.get("EARLIEST_TIME", "18:15")
            current_latest_time = current_config.get("LATEST_TIME", "18:30")

            day_container_xpath = f"//*[@id='atoz-app-root']/div[1]/div/div[2]/div/div[{i}]"
            day_name_xpath = f"{day_container_xpath}/div/div[1]"
            day_date_xpath = f"{day_container_xpath}/div/div[2]"
            
            try:
                day_date_element = self.wait.until(EC.presence_of_element_located((By.XPATH, day_date_xpath)))
                date_text = day_date_element.text.strip().replace("\n", " ") 
                
                current_dt = get_date_object(date_text)
                
                if current_dt is None:
                    print(f"Could not parse date '{date_text}' for Day {i}. Skipping.")
                    continue

                if current_dt > end_dt:
                    print(f"--- Reached {date_text}. This is after {END_DATE}. Stopping check. ---")
                    break 
                
                if current_dt < start_dt:
                    print(f"Day {i} ({date_text}) is before {START_DATE}. Skipping.")
                    continue 
                
                day_name_element = self.driver.find_element(By.XPATH, day_name_xpath)
                full_day_text = day_name_element.text.strip()
                
                is_allowed_weekday = False
                for allowed_day in current_weekdays:
                    if allowed_day in full_day_text:
                        is_allowed_weekday = True
                        break
                
                if not is_allowed_weekday:
                    print(f"--- Day {i} ({full_day_text}, {date_text}) is excluded by Weekday filter. Skipping. ---")
                    continue

                print(f"--- Checking Day {i}: {full_day_text}, {date_text} ---")
                
                day_button = self.driver.find_element(By.XPATH, day_container_xpath)
                day_button.click()
                time.sleep(2) 

                shift_container_xpath = "//*[@id='atoz-app-root']/div[1]/div/div[3]/div[1]/div/div[3]/div[2]/div"
                shift_rows = self.driver.find_elements(By.XPATH, shift_container_xpath)
                
                if len(shift_rows) == 0:
                    print("  No shifts found.")

                for j, row in enumerate(shift_rows, start=1):
                    try:
                        time_xpath = f"//*[@id='atoz-app-root']/div[1]/div/div[3]/div[1]/div/div[3]/div[2]/div[{j}]/div/div[1]/div[1]/div[1]/div[1]/div/strong"
                        button_xpath = f"//*[@id='atoz-app-root']/div[1]/div/div[3]/div[1]/div/div[3]/div[2]/div[{j}]/div/div[2]/div/button"

                        time_element = row.find_element(By.XPATH, time_xpath)
                        time_text = time_element.text 
                        
                        if "-" in time_text:
                            start_str, end_str = time_text.split("-")
                            start_parsed = parse_hour(start_str.strip())
                            
                            if parse_hour(current_earliest_time) <= start_parsed <= parse_hour(current_latest_time):
                                end_parsed = parse_hour(end_str.strip())
                                duration = time_diff(end_parsed, start_parsed)
                                
                                if duration <= current_longest_shift:
                                    print(f"    MATCH! Found {duration}hr shift: {time_text}")
                                    add_button = row.find_element(By.XPATH, button_xpath)
                                    
                                    if "Add" in add_button.get_attribute("aria-label") or "Add" in add_button.text:
                                        self.wait_and_click(add_button)
                                        try:
                                            done_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-test-id='AddOpportunityModalSuccessDoneButton']")))
                                            done_button.click()
                                            print("    Shift Added Successfully!")
                                        except:
                                            pass
                    except:
                        continue

            except Exception as e:
                print(f"End of schedule slider reached or error at Day {i}. Stopping.")
                break

def parse_hour(hora):
    hour, mint = hora.split(":")
    minute = "".join([i for i in mint if i.isdigit()])
    section = mint[len(minute):]
    hour, minute = int(hour), int(minute)
    if section.lower() == "pm" and hour != 12:
        hour += 12
    return (hour, minute)

def earlier_time(time1, time2):
    if time1[0] > time2[0]:
        return time2
    elif time1[0] < time2[0]:
        return time1
    elif time1[1] > time2[1]:
        return time2
    else:
        return time1

def time_diff(time1, time2):
    if time1[0] < time2[0]:
        midnight_offset = 24 - time2[0]
        time2 = list(time2)
        time2[0] = - midnight_offset
    diff = time1[0] - time2[0]
    diff -= time1[1] / 60
    diff += time2[1] / 60
    return diff

def main():
    prevent_sleep()
    start = time.time()
    try:
        browser = Browser()
        browser.login()
        while True:
            current_config = load_config()
            hours_to_run = current_config.get("HOURS_TO_RUN", 48)
            if time.time() - start >= hours_to_run * 60 * 60:
                break
                
            browser.find_shifts()
            browser.back_home()
            done = time.time()
            
            while True:
                current_config = load_config()
                seconds_between = current_config.get("SECONDS_BETWEEN_CHECKS", 15)
                if time.time() - done >= seconds_between:
                    break
                time.sleep(5) 
                
        browser.exit()
    except KeyboardInterrupt:
        print("\nScript manually stopped by user.")
        try:
            browser.exit()
        except:
            pass
    finally:
        allow_sleep()

if __name__ == "__main__":
    main()