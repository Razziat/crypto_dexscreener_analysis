import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException
import json
from time import sleep, time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the options
options = UiAutomator2Options()
options.platformName = 'Android'
options.deviceName = '4672d93b'
options.appPackage = 'com.dexscreener'
options.appActivity = 'com.dexscreener.MainActivity'
options.noReset = True

# Additional capabilities
additional_caps = {
    'skipUnlock': True,
    'disableWindowAnimation': True,
    'uiautomator2ServerInstallTimeout': 60000,
    'ignoreHiddenApiPolicyError': True
}
options.load_capabilities(additional_caps)

# Initialize the driver and start the timer
logging.info("Initializing the Appium driver")
start_time = time()
driver = webdriver.Remote('http://localhost:4725/wd/hub', options=options)
end_time = time()
logging.info(f"Driver initialized. Time taken: {end_time - start_time:.2f} seconds")

# Wait for the app to load
sleep(10)

# Load existing tokens from JSON file to avoid duplicates
try:
    with open('tokens_data.json', 'r') as f:
        existing_tokens = json.load(f)
        existing_token_names = {token['Token Name'] for token in existing_tokens}
except (FileNotFoundError, json.JSONDecodeError):
    existing_tokens = []
    existing_token_names = set()

# Function to clean and align the extracted data
def clean_and_align_data(token_data):
    cleaned_data = {
        "Token Name": token_data[0],
        "Time": token_data[1],
        "Price": token_data[2],
        "Additional Value": "",
        "Change Indicator": "",
        "Change": "",
        "Project Name": "",
        "Liquidity": "",
        "Volume": "",
        "Market Cap": ""
    }

    if len(token_data) >= 4 and token_data[3].isdigit():
        cleaned_data["Additional Value"] = token_data[3]
        cleaned_data["Change Indicator"] = token_data[4] if len(token_data) > 4 else ""
        cleaned_data["Change"] = token_data[5] if len(token_data) > 5 else ""
        cleaned_data["Project Name"] = token_data[6] if len(token_data) > 6 else ""
        start_index = 7
    else:
        cleaned_data["Change Indicator"] = token_data[3] if len(token_data) > 3 else ""
        cleaned_data["Change"] = token_data[4] if len(token_data) > 4 else ""
        cleaned_data["Project Name"] = token_data[5] if len(token_data) > 5 else ""
        start_index = 6

    if len(token_data) > start_index:
        for i in range(start_index, len(token_data), 2):
            key = token_data[i]
            value = token_data[i + 1] if i + 1 < len(token_data) else ""
            if key == "LIQ":
                cleaned_data["Liquidity"] = value
            elif key == "VOL":
                cleaned_data["Volume"] = value
            elif key == "MCAP":
                cleaned_data["Market Cap"] = value

    return cleaned_data

# Extract the data from the first 8 ViewGroup elements based on the content-desc attribute
def extract_token_data(driver):
    tokens_data = []
    try:
        logging.info("Sending request to locate ViewGroup elements with content-desc attribute")
        elements = driver.find_elements(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc]')[:8]
        
        for element in elements:
            try:
                content_desc = element.get_attribute('content-desc')
                if content_desc and not any(keyword in content_desc for keyword in ["Trending", "Moonshot", "Newest"]):
                    token_data = content_desc.split(', ')
                    cleaned_data = clean_and_align_data(token_data)
                    tokens_data.append(cleaned_data)
            except StaleElementReferenceException:
                logging.warning("Encountered a stale element, skipping...")
                continue

    except StaleElementReferenceException:
        logging.warning("Encountered a stale element reference, retrying...")
        tokens_data = extract_token_data(driver)

    return tokens_data

# Function to display tokens in the console
def display_token_data(token_data):
    for token in token_data:
        print(f"\nToken Name: {token['Token Name']}")
        print(f"Time: {token['Time']}")
        print(f"Price: {token['Price']}")
        print(f"Additional Value: {token['Additional Value']}")
        print(f"Change Indicator: {token['Change Indicator']}")
        print(f"Change: {token['Change']}")
        print(f"Project Name: {token['Project Name']}")
        print(f"Liquidity: {token['Liquidity']}")
        print(f"Volume: {token['Volume']}")
        print(f"Market Cap: {token['Market Cap']}\n")

# Main function to monitor and detect changes in tokens
def monitor_token_changes(driver):
    last_extracted_tokens = []
    while True:
        # Extract the current tokens
        current_tokens = extract_token_data(driver)

        # Filter out already seen tokens
        new_tokens = [token for token in current_tokens if token['Token Name'] not in existing_token_names]

        # Check if there are any new tokens
        if new_tokens:
            logging.info(f"Detected {len(new_tokens)} new tokens.")
            display_token_data(new_tokens)

            # Update the JSON file with new tokens
            existing_tokens.extend(new_tokens)
            with open('tokens_data.json', 'w') as f:
                json.dump(existing_tokens, f, indent=4)
            logging.info(f"Added {len(new_tokens)} new tokens to the JSON file.")

            # Add new token names to the set of existing tokens
            existing_token_names.update(token['Token Name'] for token in new_tokens)

        # Update the last extracted tokens (for full-page changes)
        last_extracted_tokens = current_tokens

        # Wait for a short period before checking again
        sleep(2)

try:
    # Start monitoring for token changes
    monitor_token_changes(driver)

finally:
    # Close the driver and log the time taken for the entire script execution
    driver.quit()
    script_end_time = time()
    logging.info(f"Script execution completed. Total time taken: {script_end_time - start_time:.2f} seconds")
