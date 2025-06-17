import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Today's date format
today_str = datetime.now().strftime("%d%m%Y")

custom_download_dir = r"C:\Users\Mohit Pandey\cKinetics Consulting Services Pvt. Ltd\Analysts Team - Alberta Trades"
# os.makedirs(custom_download_dir, exist_ok=True)  # Create the folder if it doesn't exist

download_dir = custom_download_dir

# Download directory
# download_dir = os.path.join(os.path.expanduser("~"), "Downloads")

# Chrome options for automatic downloads
options = Options()
# prefs = {
#     "download.default_directory": download_dir,
#     "download.prompt_for_download": False,
#     "safebrowsing.enabled": True
# }

prefs = {
    "download.default_directory": custom_download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}

options.add_experimental_option("prefs", prefs)

# ChromeDriver path
service = Service(r'C:\Users\Mohit Pandey\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')

# Start WebDriver
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)


def wait_and_rename_file(old_files, prefix):
    timeout = 60
    start_time = time.time()

    while True:
        # New .xlsx files not present in old_files
        current_files = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
        new_files = current_files - old_files

        # Only proceed if new file appears
        if new_files:
            new_file = list(new_files)[0]
            old_path = os.path.join(download_dir, new_file)
            new_path = os.path.join(download_dir, f"{prefix}today{today_str}.xlsx")
            os.rename(old_path, new_path)
            print(f"Renamed {new_file} to {new_path}")
            return

        # Timeout safeguard
        if time.time() - start_time > timeout:
            raise TimeoutError(f"{prefix} file download not detected in {timeout} seconds.")

        time.sleep(1)


# Step 1: Navigate to AEOR page
driver.get('https://alberta.csaregistries.ca/GHGR_Listing/AEOR_Listing.aspx')

# Step 2: Click Export AEOR
aeor_export_btn = wait.until(EC.element_to_be_clickable(
    (By.ID, 'Alberta_GHGR_Theme_wt178_block_OutSystemsUIWeb_wt16_block_wtContent_wtMainContent_wt111')))
existing_files_aeor = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
aeor_export_btn.click()

# Step 3: Wait and rename AEOR file
wait_and_rename_file(existing_files_aeor, "AEOR")

# Step 4–5: Navigate to EPC Export
epc_tab = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Alberta Emission Performance Credit Registry")))
driver.execute_script("arguments[0].click();", epc_tab)

registry_listing = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Registry Listing")))
driver.execute_script("arguments[0].click();", registry_listing)

# Step 6: Export EPC
export_registry_btn = wait.until(EC.presence_of_element_located(
    (By.ID, "Alberta_GHGR_Theme_wt93_block_OutSystemsUIWeb_wt16_block_wtContent_wtMainContent_wt108")))
existing_files_epc = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
export_registry_btn.click()

# Step 7: Wait and rename EPC file
wait_and_rename_file(existing_files_epc, "EPC")

driver.quit()
