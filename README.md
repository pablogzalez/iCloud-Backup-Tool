<p align="center">
  <h1 align="center" style="color: #5e9ca0;">📱 iCloud Backup Script</h1>
</p>

<p align="center" style="color: #333;">
  This repository contains a script for automatic backups of photos and videos from iCloud to local storage. Optional Telegram notifications and iCloud video deleting.
</p>

---

## 🌟 Features

- 🚀 Automatic backup of photos and videos from **iCloud** to local storage.
- 📲 Optional notifications via **Telegram** about the progress and summary of the backup.
- 📂 Efficient management of iCloud albums, including the option to empty the 'Recently Deleted' album.
- 🛠️ Support for iCloud's two-factor authentication.
- ⚙️ Customizable Telegram notification feature.
- ⚙️ Customizable iCloud video deleting feature.

## 🔧 Configuration

### Prerequisites

- 🐍 Python 3.x.
- 🔐 iCloud credentials. Optional: A Telegram Token for notifications.

### Installation

1. 📥 Clone this repository:
<p>   git clone https://github.com/your-user/iCloud-Backup-Tool.git</p>

2. 📂 Navigate to the project directory:
<p>   cd iCloud-Backup-Tool</p>

3. 🖥️ Install the required dependencies:
<p>   pip install -r requirements.txt</p>

4. ⚙️ Set up your iCloud credentials in the .env file. Optionally, set up Telegram credentials for notifications.

## 📖 Usage
After setting up your credentials, you can run the script to perform backups. Optionally, you can enable Telegram notifications.

🔍 Modify the script's arguments according to your needs to customize the backup process and notification settings.

### Launch Examples
After setting up your credentials, you can run the script with different arguments according to your needs:

- Perform a backup of the 'All Photos' album and save them in the '/backup/icloud' directory:
<p>python icloud_backup.py --album "All Photos" --destination "/backup/icloud"</p>

- Perform a backup of the 'Vacation' album, delete the videos after the backup, and send a Telegram notification:
<p>python icloud_backup.py --album "Vacation" --destination "/backup/icloud" --delete-videos --send-telegram</p>

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

🧐 Make sure to update the tests as appropriate.

<p align="center">
  Created with 💖 by <a href="https://github.com/pablogzalez">Pablo González</a>
</p>