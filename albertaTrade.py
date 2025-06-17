import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Today's date format
today_str = datetime.now().strftime("%d%m%Y")

# Linux-compatible download path for GitHub runner
download_dir = "/home/runner/work/_temp/downloads"
os.makedirs(download_dir, exist_ok=True)

# Chrome options for headless + download setup
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# Use built-in chromedriver on GitHub runner
service = Service("/usr/bin/chromedriver")

# Start driver
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

def wait_and_rename_file(old_files, prefix):
    timeout = 60
    start_time = time.time()
    while True:
        current_files = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
        new_files = current_files - old_files
        if new_files:
            new_file = list(new_files)[0]
            old_path = os.path.join(download_dir, new_file)
            new_path = os.path.join(download_dir, f"{prefix}_today_{today_str}.xlsx")
            os.rename(old_path, new_path)
            print(f"Renamed {new_file} to {new_path}")
            return
        if time.time() - start_time > timeout:
            raise TimeoutError(f"{prefix} download not detected in {timeout} seconds.")
        time.sleep(1)

# Step 1: AEOR page
driver.get('https://alberta.csaregistries.ca/GHGR_Listing/AEOR_Listing.aspx')

# Step 2: Click Export AEOR
aeor_export_btn = wait.until(EC.element_to_be_clickable(
    (By.ID, 'Alberta_GHGR_Theme_wt178_block_OutSystemsUIWeb_wt16_block_wtContent_wtMainContent_wt111')))
existing_files_aeor = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
aeor_export_btn.click()

# Step 3: Rename AEOR
wait_and_rename_file(existing_files_aeor, "AEOR")

# Step 4: Click EPC tab
epc_tab = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Alberta Emission Performance Credit Registry")))
driver.execute_script("arguments[0].click();", epc_tab)

registry_listing = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Registry Listing")))
driver.execute_script("arguments[0].click();", registry_listing)

# Step 5: Click Export EPC
export_registry_btn = wait.until(EC.presence_of_element_located(
    (By.ID, "Alberta_GHGR_Theme_wt93_block_OutSystemsUIWeb_wt16_block_wtContent_wtMainContent_wt108")))
existing_files_epc = set(f for f in os.listdir(download_dir) if f.endswith('.xlsx'))
export_registry_btn.click()

# Step 6: Rename EPC
wait_and_rename_file(existing_files_epc, "EPC")

driver.quit()
