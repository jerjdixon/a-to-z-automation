# **Amazon A to Z Shift Finder**

## **Overview**

This Python script automates the proceess of finding shifts on the Amazon A to Z portal. It acts as a smart assistant that constantly monitors the schedule based on your personal preferences—such as specific days of the week, shift times, and shift lengths—and attempts to claim them the moment they become available.

**Key Features:**

* **Auto-Login:** Automatically handles the login process after the initial setup.  
* **Smart Filtering:** Only claims shifts that match your exact criteria (e.g., "Only Tuesday mornings under 5 hours").  
* **Persistent Session:** Uses a dedicated Chrome profile to save your cookies, meaning you do not have to enter your password or 2FA code every time the script runs.  
* **Human-Like Interaction:** Navigates the schedule slider and buttons in a way that mimics human behavior to maintain safety and stability.

## ---

**Prerequisites**

Before running the script, ensure you have the following installed on your computer:

1. **Google Chrome:** The script requires the Google Chrome browser to interact with the website.  
2. **Python 3.7+:** This is the programming language the script is written in.

## ---

**Installation Guide**

### **Step 1: Install Python**

If you do not have Python installed:

1. Go to [python.org/downloads](https://www.python.org/downloads/).  
2. Download the latest version for your operating system.  
3. **Critical Step:** When the installer opens, check the box that says **"Add Python to PATH"** at the bottom of the window before clicking "Install Now". This ensures your computer knows where to find Python.

### **Step 2: Install Required Libraries**

The script relies on a few external tools (libraries) to control the browser.

1. Open your Command Prompt (Windows) or Terminal (Mac/Linux).  
2. Run the following commands one by one (press Enter after each):

```bash
pip install selenium
pip install undetected-chromedriver
pip install setuptools
```

### **Step 3: Create a Dedicated Chrome Folder**

To keep your personal browsing data separate from the bot, and to save your login session, you need a specific folder for the script.

1. Create a new empty folder anywhere on your computer (e.g., on your Desktop).  
2. Name it something simple, like ChromeBotProfile.  
3. **Copy the file path** of this folder. You will need it for the configuration step below.  
   * *Windows Tip:* Shift \+ Right-click the folder and select "Copy as path".

## ---

**Configuration Guide**

This is the most important part of the setup. Open the script file (e.g., main.py) in a text editor like Notepad, VS Code, or Python IDLE.

Locate the configuration section near the top of the file. Here is a detailed explanation of what each setting controls and how to customize it for your needs.

### **1\. Timing and Delays**

**STALL\_AFTER\_LOGIN \= 2**

* **What it does:** This sets a pause (in seconds) immediately after the script detects a successful login but before it starts clicking buttons.  
* **Why change it?** If your computer is slower or your internet connection lags, the website might need a few extra seconds to fully load the dashboard. Increasing this helps prevent errors where the script tries to click a menu that hasn't appeared yet.  
* **Example:** Set to 5 if you notice the script trying to click too early.

**SECONDS\_BETWEEN\_CHECKS \= 5**

* **What it does:** Once the script has finished checking all 5 days (or however many you set), it will wait this many seconds before starting the process over again.  
* **Why change it?** A lower number checks more frequently (good for high-competition shifts) but increases the risk of the website temporarily blocking you for "spamming." A safe range is usually 5 to 60 seconds.

**HOURS\_TO\_RUN \= 3**

* **What it does:** The script will automatically stop running after this many hours.  
* **Why change it?** This prevents the script from running indefinitely if you forget about it.  
* **Example:** Set to 0.5 to run for just 30 minutes.

### **2\. Shift Preferences (Smart Filtering)**

**START\_DATE \= "Dec 22"**  
**END\_DATE \= "Dec 27"**

* **What it does:** These two settings create a specific "window" of time for the bot to operate in.  
* **How it works:**  
  * **Start Date:** When the bot looks at the schedule slider, it checks the date of each day. If the date is *before* your START\_DATE, it skips that day entirely without clicking it.  
  * **End Date:** As soon as the bot encounters a date that is *after* your END\_DATE, it stops checking the schedule completely and finishes its run.  
* **Format:** You must use the "Month Day" format with the first 3 letters of the month capitalized (e.g., "Jan 01", "Dec 25", "Nov 05").  
* **Optional:** If you want the bot to run indefinitely (or just based on days of the week), leave these blank (e.g., START\_DATE \= "").

Example Scenario:  
You are going on vacation and only want to pick up shifts for the week you return.

```python

START\_DATE \= "Jan 05"  
END\_DATE \= "Jan 12" 

```

*Result:* The bot will ignore today's shifts. It will fast-forward through the schedule until it finds Jan 5th, check shifts for Jan 5th through Jan 12th, and then turn itself off.

EARLIEST\_TIME \= "07:00"  
LATEST\_TIME \= "11:00"

* **What it does:** These define your "Start Time Window." The script will *only* accept a shift if it starts between these two times.  
* **Format:** You must use 24-hour format (HH:MM).  
* **Example:**  
  * To accept shifts starting between 7:00 AM and 11:00 AM, use "07:00" and "11:00".  
  * To accept shifts starting between 1:00 PM and 5:00 PM, use "13:00" and "17:00".  
* **Note:** This filters based on the *start time* only.

**LONGEST\_SHIFT \= 8**

* **What it does:** This sets the maximum duration (in hours) you are willing to work.  
* **How it works:** If a shift is available from 8:00 AM to 6:00 PM (10 hours), but this is set to 8, the script will skip it.  
* **Example:** Set to 4 if you only want half-shifts.

**WEEKDAYS**

* **What it does:** This list controls exactly which days of the week the script is allowed to click on.  
* **How to customize:** The script checks the name of the day on the slider. If that name is in this list, it proceeds. If the name is missing (or commented out), it skips that day entirely.  
* **How to disable a day:** You do not need to delete the line. simply add a \# symbol in front of it. This "comments it out," telling the code to ignore it.  
* **Example:** To strictly work only on weekends:  

```python
WEEKDAYS = [
      # "Monday",
      # "Tuesday",
      # "Wednesday",
      # "Thursday",
      # "Friday",
      "Saturday",
      "Sunday",
]
```

### **3\. Login and System Settings**

**CHROME\_PROFILE\_DIRECTORY\_PATH \= r"C:\\Users\\Name\\Desktop\\ChromeBotProfile"**

* **What it does:** This points the script to the folder you created in **Installation Step 3**.  
* **Important:** The r before the quote is necessary for Windows file paths. Ensure you paste the full path between the quotation marks.

**Amazon\_Login \= "your\_username"**

* **What it does:** This is the username the script will type into the first login field.  
* **Usage:** Replace "your\_username" with your actual Amazon login ID.

**LOGIN\_URL**

* **Status:** Generally, do not change this. It points to the standard A to Z login page.

## ---

**Running the Script**

1. **First Run (Manual Setup):**  
   * Double-click the Python file to run it.  
   * Chrome will open and navigate to the login page.  
   * The script will type your username but may pause for Two-Factor Authentication (2FA) or a One-Time Password (OTP).  
   * **Action Required:** Manually enter your code or use your security key. **Make sure to check the "Remember this device" box.**  
   * Once you reach the homepage, the script will detect it and begin the automation.  
2. **Subsequent Runs:**  
   * Because you used a dedicated Chrome Profile and clicked "Remember this device," the next time you run the script, it should bypass the login screen and go straight to finding shifts.

## **Troubleshooting**

* **Script closes immediately:** This often means undetected-chromedriver is not compatible with your current Chrome version. Run pip install \--upgrade undetected-chromedriver to fix this.  
* **Script loops on login:** If the script keeps trying to login even though you are logged in, increase the STALL\_AFTER\_LOGIN timer to give the homepage detection more time to work.  
* **Not clicking days:** Ensure your WEEKDAYS list matches the spelling of the days on the website exactly (e.g., "Wednesday").

## **Support and Contributions**

If you encounter bugs or have ideas for improvements, please use the **Issues** tab in the GitHub repository. When filing an issue, please include specific details about where the script is getting stuck or any error messages displayed in the console.
