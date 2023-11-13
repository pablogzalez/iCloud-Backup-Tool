📱 iCloud Photo & Video Backup Tool
This Python script automates the backup of photos and videos from your iCloud account to a local directory and sends updates via Telegram.

Features
🔄 Automatic Backup: Effortlessly backs up photos and videos from iCloud.
📥 Local Storage: Saves your memories securely in a specified local directory.
📹 Video Support: Identifies and handles video files specifically.
🤖 Telegram Notifications: Sends status updates and summaries through Telegram.
🛡️ Two-Factor Authentication Support: Seamlessly handles iCloud's two-factor authentication.
🧹 Clean Up: Empties the 'Recently Deleted' album in iCloud.
Requirements
🐍 Python 3: Ensure you have Python 3 installed.
🔒 External Libraries: pyicloud, termcolor, requests.
📑 Config File: A configuration file with iCloud credentials.
🌐 Telegram Bot Token & Chat ID: Required for sending Telegram notifications.
Setup & Usage
📁 Clone the Repository: Download or clone this repository to your local machine.
⚙️ Install Dependencies: Run pip install -r requirements.txt to install necessary libraries.
🖊️ Configure: Fill in your iCloud credentials and Telegram Bot info in the config file.
🚀 Run the Script: Execute the script with python backup_script.py.
📲 Receive Updates: Get progress and summary reports directly on your Telegram.
Configuration
iCloud Credentials: Store your iCloud username and password in the config file.
Telegram Bot: Set your Telegram Bot token and chat ID for receiving notifications.
Command-Line Arguments
--config: Path to your configuration file.
--album: Name of the iCloud album to backup.
--destination: Local directory for storing the backups.
--delete-videos: Option to delete videos from iCloud after backup.
Contributing
Feel free to fork, modify, and send pull requests. For major changes, please open an issue first to discuss what you would like to change.

🌟 Star this repository if you found it helpful! 🌟
