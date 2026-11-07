import json
import os
import requests
import sys
import subprocess
import time

from packaging import version

PROJECT_ID = '4H6sumDB'
INFO_PATH = '.github/data/info.json'
MAIN_BRANCH = 'main'
RELEASE_BRANCH = 'release'

MAX_RETRIES = 10
RETRY_DELAYS = [60, 120, 300, 600, 900, 1200, 1500, 1800, 2100, 2400]  # in seconds

def extract_main_version(version_string):
    return version_string.split('-')[0]

def fetch_latest_version_with_retry():
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} to fetch Modrinth version information")
            url = f"https://api.modrinth.com/v2/project/{PROJECT_ID}/version"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            versions = response.json()
            latest = versions[0]
            return extract_main_version(latest['version_number'])
        except Exception as e:
            last_exception = e
            delay = RETRY_DELAYS[attempt]
            print(f"Error accessing Modrinth API: {e}")
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

    print(f"CRITICAL ERROR: Modrinth API is down or unreachable after {MAX_RETRIES} attempts")
    print(f"Last error: {last_exception}")
    print("Exiting with success status to avoid failing the workflow")
    sys.exit(0)

def read_stored_info():
    """Read stored version info, or return empty dict if file doesn't exist"""
    if not os.path.exists(INFO_PATH):
        return {"version": "0.0.0", "versionsToSkip": []}

    with open(INFO_PATH, 'r') as f:
        return json.load(f)

def save_info(info):
    """Save version info to file"""
    os.makedirs(os.path.dirname(INFO_PATH), exist_ok=True)

    with open(INFO_PATH, 'w') as f:
        json.dump(info, f, indent=2)

    print(f"File saved to {os.path.abspath(INFO_PATH)}")
    print(f"Files in directory: {os.listdir(os.path.dirname(INFO_PATH))}")

def verify_version_needs_merge():
    """Check if version has increased and needs merging"""
    print("Fetching latest version from Modrinth...")
    latest_version = fetch_latest_version_with_retry()
    print(f"Latest version: {latest_version}")

    print("Reading stored version info...")
    stored_info = read_stored_info()
    stored_version = stored_info.get("version", "0.0.0")
    versions_to_skip = stored_info.get("versionsToSkip", [])
    print(f"Stored version: {stored_version}")
    print(f"Versions to skip: {versions_to_skip}")

    first_run = not os.path.exists(INFO_PATH)
    if first_run:
        print(f"First run detected. Creating new info.json at {INFO_PATH}")
        if "versionsToSkip" not in stored_info:
            stored_info["versionsToSkip"] = []

    if latest_version in versions_to_skip:
        print(f"Version {latest_version} is in the skip list. Keeping current version and skipping merge.")
        # Don't update the stored version if this version should be skipped
        return False, latest_version

    stored_info["version"] = latest_version
    save_info(stored_info)
    print(f"Updated version info saved to {INFO_PATH}")

    if first_run:
        print("First run detected. Created info.json but skipping merge.")
        return False, latest_version

    if version.parse(latest_version) > version.parse(stored_version):
        print(f"Version increased from {stored_version} to {latest_version}")
        return True, latest_version
    else:
        print("No version increase detected, skipping merge")
        return False, latest_version

def main():
    needs_merge, latest_version = verify_version_needs_merge()

    if not needs_merge:
        with open(".version_change_needed", "w") as f:
            f.write("false")
        return 0

    print("Version increased. Merge is needed.")
    with open(".version_change_needed", "w") as f:
        f.write("true")
    return 0  # Always return success

if __name__ == "__main__":
    sys.exit(main())
