import os
import requests
import json
import hashlib

DOWNLOAD_URL = r"https://Arlynnn-stack.github.io/Update-Repo-1/LynnnMenu.dll"
VERSION_URL = r"https://arlynnn-stack.github.io/Update-Repo-1/version.json"

def check_dirs():
    # Check for Lynnn folder
    appdata_folder = os.getenv("APPDATA")
    lynn_folder = os.path.join(appdata_folder, "Lynia")

    if not os.path.exists(lynn_folder):
        os.makedirs(lynn_folder)

    # Check for settings.json
    settings_file = os.path.join(lynn_folder, "settings.json")

    if not os.path.exists(settings_file):
        with open(settings_file, "w") as file:
            json.dump({"hash": "None"}, file, indent=4)

    return lynn_folder, settings_file

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def download_file(save_path, url):
    # This downloads the .dll
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        return True
    return False

def get_latest_version():
    response = requests.get(VERSION_URL)
    if response.status_code == 200:
        data = response.json()
        return data.get("version")
    return None

def download_if_needed():
    download_folder, settings_file = check_dirs()
    download_path = os.path.join(download_folder, "LynnnMenu.dll")

    with open(settings_file, "r") as file:
        data = json.load(file)

    previous_hash = data.get("hash", "None")
    current_version = get_latest_version()

    # If the .dll file does not exist, set the hash to None to force download
    if not os.path.exists(download_path):
        previous_hash = "None"

    # Download the file to a temporary location to check its hash
    temp_download_path = download_path + ".tmp"
    if download_file(temp_download_path, DOWNLOAD_URL):
        new_hash = get_file_hash(temp_download_path)

        # Check if the file has changed or if the .dll file was missing
        if previous_hash != new_hash:
            # Replace the old file with the new one
            if os.path.exists(download_path):
                os.remove(download_path)
            os.rename(temp_download_path, download_path)

            data["hash"] = new_hash
            data["version"] = current_version
            with open(settings_file, "w") as file:
                json.dump(data, file, indent=4)
            return True
        else:
            os.remove(temp_download_path)  # Clean up the temporary file if no change
    return False

if __name__ == "__main__":
    if download_if_needed():
        print("File downloaded and updated.")
    else:
        print("No update needed.")
