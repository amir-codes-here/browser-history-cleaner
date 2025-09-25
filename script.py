import os
import sqlite3
import shutil

def remove_firefox_history(search_str: str):
    appdata = os.getenv("APPDATA")
    profiles_path = os.path.join(appdata, "Mozilla", "Firefox", "Profiles")

    if not os.path.exists(profiles_path):
        print("Firefox profiles directory not found.")
        return

    profile_dirs = [d for d in os.listdir(profiles_path) if os.path.isdir(os.path.join(profiles_path, d))]
    if not profile_dirs:
        print("No Firefox profiles found.")
        return

    print(f"Found {len(profile_dirs)} Firefox profile(s).")

    for profile in profile_dirs:
        db_path = os.path.join(profiles_path, profile, "places.sqlite")
        if not os.path.exists(db_path):
            print(f"Skipping {profile}: no places.sqlite found.")
            continue

        backup_path = db_path + ".backup"
        if not os.path.exists(backup_path):
            shutil.copy2(db_path, backup_path)
            print(f"Backup created for {profile} at {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Find matching place_ids
            cursor.execute("SELECT id FROM moz_places WHERE url LIKE ?", (f"%{search_str}%",))
            place_ids = [row[0] for row in cursor.fetchall()]

            if not place_ids:
                print(f"[{profile}] No matching history found.")
                continue

            # Delete visits linked to those places
            cursor.executemany("DELETE FROM moz_historyvisits WHERE place_id = ?", [(pid,) for pid in place_ids])

            # Remove orphaned moz_places entries (that are not bookmarked)
            cursor.execute("""
                DELETE FROM moz_places
                WHERE id IN ({seq})
                AND id NOT IN (SELECT fk FROM moz_bookmarks)
            """.format(seq=",".join("?"*len(place_ids))), place_ids)

            conn.commit()

            print(f"[{profile}] Removed {len(place_ids)} history entries containing '{search_str}'.")

        except Exception as e:
            print(f"[{profile}] Error: {e}")
        finally:
            conn.close()


def remove_chrome_history(search_str: str):
    localappdata = os.getenv("LOCALAPPDATA")
    profiles_path = os.path.join(localappdata, "Google", "Chrome", "User Data")

    if not os.path.exists(profiles_path):
        print("Chrome profiles directory not found.")
        return

    profile_dirs = [d for d in os.listdir(profiles_path) if os.path.isdir(os.path.join(profiles_path, d))]
    print(f"Found {len(profile_dirs)} Chrome profile(s).")

    for profile in profile_dirs:
        db_path = os.path.join(profiles_path, profile, "History")
        if not os.path.exists(db_path):
            print(f"Skipping {profile}: no History database found.")
            continue

        backup_path = db_path + ".backup"
        if not os.path.exists(backup_path):
            shutil.copy2(db_path, backup_path)
            print(f"Backup created for {profile} at {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Delete visits and urls directly with subqueries
            cursor.execute("""
                DELETE FROM visits
                WHERE url IN (SELECT id FROM urls WHERE url LIKE ?)
            """, (f"%{search_str}%",))

            cursor.execute("DELETE FROM urls WHERE url LIKE ?", (f"%{search_str}%",))

            deleted = cursor.rowcount
            conn.commit()

            if deleted > 0:
                print(f"[{profile}] Removed {deleted} history entries containing '{search_str}'.")
            else:
                print(f"[{profile}] No matching history found.")

        except Exception as e:
            print(f"[{profile}] Error: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    browser = input("Enter the browser (c for chrome, f for firefox and b for both): ").lower()
    assert browser in ('c', 'f', 'b'), "Invalid input"
    term = input("Enter search string to remove from browsing history: ")
    if browser == 'f':
        remove_firefox_history(term)
    elif browser == 'c':
        remove_chrome_history(term)
    else:
        remove_chrome_history(term)
        remove_firefox_history(term)
    input("\n\nPress Enter to exit...")
