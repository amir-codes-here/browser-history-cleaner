import os
import sqlite3
import shutil

def remove_firefox_history(search_str: str):
    # Locate Firefox profile directory
    appdata = os.getenv("APPDATA")  # C:\Users\<User>\AppData\Roaming
    profiles_path = os.path.join(appdata, "Mozilla", "Firefox", "Profiles")

    if not os.path.exists(profiles_path):
        print("Firefox profiles directory not found.")
        return

    # Find all profile folders
    profile_dirs = [d for d in os.listdir(profiles_path) if os.path.isdir(os.path.join(profiles_path, d))]
    if not profile_dirs:
        print("No Firefox profiles found.")
        return

    print(f"Found {len(profile_dirs)} profile(s).")

    for profile in profile_dirs:
        profile_path = os.path.join(profiles_path, profile)
        db_path = os.path.join(profile_path, "places.sqlite")

        if not os.path.exists(db_path):
            print(f"Skipping {profile}: no places.sqlite found.")
            continue

        # Backup database for safety
        backup_path = db_path + ".backup"
        if not os.path.exists(backup_path):  # only make one backup
            shutil.copy2(db_path, backup_path)
            print(f"Backup created for {profile} at {backup_path}")

        # Connect to DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Delete only history visits with matching URLs
            cursor.execute("""
                DELETE FROM moz_places
                WHERE url LIKE ?
            """, (f"%{search_str}%",))

            deleted_rows = conn.total_changes
            conn.commit()

            if deleted_rows > 0:
                print(f"[{profile}] Removed {deleted_rows} history entries containing '{search_str}'.")
            else:
                print(f"[{profile}] No matching history found.")

        except Exception as e:
            print(f"[{profile}] Error: {e}")
        finally:
            conn.close()


def remove_chrome_history(search_str: str):
    # Locate Chrome profile directory
    localappdata = os.getenv("LOCALAPPDATA")  # C:\Users\<User>\AppData\Local
    profiles_path = os.path.join(localappdata, "Google", "Chrome", "User Data")

    if not os.path.exists(profiles_path):
        print("Chrome profiles directory not found.")
        return

    # Profile folders (Default, Profile 1, Profile 2, etc.)
    profile_dirs = [d for d in os.listdir(profiles_path) if os.path.isdir(os.path.join(profiles_path, d))]
    print(f"Found {len(profile_dirs)} Chrome profile(s).")

    for profile in profile_dirs:
        profile_path = os.path.join(profiles_path, profile)
        db_path = os.path.join(profile_path, "History")

        if not os.path.exists(db_path):
            print(f"Skipping {profile}: no History database found.")
            continue

        # Backup database
        backup_path = db_path + ".backup"
        if not os.path.exists(backup_path):
            shutil.copy2(db_path, backup_path)
            print(f"Backup created for {profile} at {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Find all url_ids for matching URLs
            cursor.execute("SELECT id FROM urls WHERE url LIKE ?", (f"%{search_str}%",))
            url_ids = [row[0] for row in cursor.fetchall()]

            if not url_ids:
                print(f"[{profile}] No matching history found.")
                conn.close()
                continue

            # Delete visits first (to avoid dangling references)
            cursor.executemany("DELETE FROM visits WHERE url = ?", [(uid,) for uid in url_ids])

            # Delete from urls
            cursor.execute("DELETE FROM urls WHERE url LIKE ?", (f"%{search_str}%",))

            conn.commit()

            print(f"[{profile}] Removed {len(url_ids)} URLs and their associated visits containing '{search_str}'.")

        except Exception as e:
            print(f"[{profile}] Error: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    browser = input("Enter the browser (c for chrome, f for firefox and b for both): ").lower()
    assert browser in ('c', 'f', 'b'), "Invalid input"
    term = input("Enter search string to remove from browsing history: ")
    match browser:
        case 'f':
            remove_firefox_history(term)
        case 'c':
            remove_chrome_history(term)
        case 'b':
            remove_chrome_history(term)
            remove_firefox_history(term)
    print("\n\nPress enter to exit ")
    input()