# Browser History Cleaner

A Python script to safely remove browsing history entries from **Chrome** and **Firefox** based on a search string in their URLs (**for windows 10 and 11**).  
The script **only deletes history records** — bookmarks, cookies, saved passwords, and other data remain untouched.

---

## Features
- Works with **Google Chrome** and **Mozilla Firefox**
- Searches for a keyword/substring in history URLs
- Deletes only matching history records
- Creates a **backup** of the history database before making changes
- Supports multiple browser profiles
- Compatible with **Windows 10 & 11**

---

## Important Notes
- **Close your browser** before running the script, otherwise the database may be locked  
- Backups (`.backup` files) are created in the same directory as the original database  
- Use carefully — once committed, deleted history cannot be recovered without backups  

---

## Requirements
- Python 3.7+  
- No external dependencies (uses only standard libraries: `os`, `sqlite3`, `shutil`)  

---

## Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/browser-history-cleaner.git
   cd browser-history-cleaner
   ```
2. Run `script.py`
    ```bash
    python script.py
    ```
3. Follow the prompts:
    - Choose browser
    - Enter a search string (e.g., `youtube` or `example.com`)
    - The script removes all history entries containing that string

---

## Restoring Backups
1. Navigate to your browser's profile folder
    - for chrome
        `C:\Users\<YourName>\AppData\Local\Google\Chrome\User Data\Default`
    - for Firefox
        `C:\Users\<YourName>\AppData\Roaming\Mozilla\Firefox\Profiles\<ProfileName>`
2. Delete the modified file
    - for Chrome -> `History`
    - for Firefox -> `places.sqlite`
3. Rename the corresponding `.backup` file back to the original name