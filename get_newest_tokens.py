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

# Configure Appium options
options = UiAutomator2Options()
options.platformName = 'Android'
options.deviceName = '4672d93b'  # Replace by your device ID
options.appPackage = 'com.dexscreener'
options.appActivity = 'com.dexscreener.MainActivity'
options.noReset = True

# Add additional Appium capabilities
additional_caps = {
    'skipUnlock': True,
    'disableWindowAnimation': True,
    'uiautomator2ServerInstallTimeout': 60000,
    'ignoreHiddenApiPolicyError': True
}
options.load_capabilities(additional_caps)

# Initialize the Appium driver and measure start-up time
logging.info("Initializing the Appium driver")
start_time = time()
driver = webdriver.Remote('http://localhost:4725/wd/hub', options=options)
end_time = time()
logging.info(f"Driver initialized. Time taken: {end_time - start_time:.2f} seconds")

# Allow time for the app to fully load
sleep(10)

# Load already saved tokens from JSON to avoid duplicates
try:
    with open('tokens_data.json', 'r') as f:
        existing_tokens = json.load(f)
        existing_token_names = {token['Token Name'] for token in existing_tokens}
except (FileNotFoundError, json.JSONDecodeError):
    existing_tokens = []
    existing_token_names = set()

# Clean and align raw token data into a structured format
def clean_and_align_data(token_data):
    # Remove junk items like empty strings or question marks
    filtered_data = [d for d in token_data if d.strip() and d.strip() != "?"]

    cleaned_data = {
        "Token Name": filtered_data[0] if len(filtered_data) > 0 else "N/A",
        "Time": filtered_data[1] if len(filtered_data) > 1 else "N/A",
        "Price": filtered_data[2] if len(filtered_data) > 2 else "N/A",
        "Additional Value": "",
        "Change Indicator": "",
        "Change": "",
        "Project Name": "",
        "Liquidity": "",
        "Volume": "",
        "Market Cap": ""
    }

    index = 3

    # Parse optional additional fields
    if len(filtered_data) > index and filtered_data[index].isdigit():
        cleaned_data["Additional Value"] = filtered_data[index]
        index += 1

    cleaned_data["Change Indicator"] = filtered_data[index] if len(filtered_data) > index else ""
    index += 1
    cleaned_data["Change"] = filtered_data[index] if len(filtered_data) > index else ""
    index += 1
    cleaned_data["Project Name"] = filtered_data[index] if len(filtered_data) > index else ""
    index += 1

    # Loop through remaining key-value pairs
    while index < len(filtered_data):
        key = filtered_data[index]
        value = filtered_data[index + 1] if index + 1 < len(filtered_data) else ""
        if key == "LIQ":
            cleaned_data["Liquidity"] = value
        elif key == "VOL":
            cleaned_data["Volume"] = value
        elif key == "MCAP":
            cleaned_data["Market Cap"] = value
        index += 2

    return cleaned_data

# Extract token information from up to 8 visible ViewGroup elements
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
                    # Append timestamp of when data was extracted
                    cleaned_data["Analyzed Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Parse liquidity and ensure it's >= $1
                    liquidity_str = cleaned_data.get("Liquidity", "")
                    liquidity_value = parse_liquidity(liquidity_str)

                    if liquidity_value >= 1.0:
                        tokens_data.append(cleaned_data)
                    else:
                        logging.info(f"Skipping token '{cleaned_data['Token Name']}' due to liquidity < $1")
            except StaleElementReferenceException:
                logging.warning("Encountered a stale element, skipping...")
                continue

    except StaleElementReferenceException:
        logging.warning("Encountered a stale element reference, retrying...")
        tokens_data = extract_token_data(driver)

    return tokens_data

# Convert liquidity strings to floats, handling K/M/B suffixes
def parse_liquidity(liquidity_str):
    if not liquidity_str:
        return 0.0

    liquidity_str = liquidity_str.strip().upper()
    if '<' in liquidity_str:
        return 0.0

    liquidity_str = liquidity_str.replace('$', '').replace(',', '')
    multiplier = 1
    if 'K' in liquidity_str:
        multiplier = 1_000
        liquidity_str = liquidity_str.replace('K', '')
    elif 'M' in liquidity_str:
        multiplier = 1_000_000
        liquidity_str = liquidity_str.replace('M', '')
    elif 'B' in liquidity_str:
        multiplier = 1_000_000_000
        liquidity_str = liquidity_str.replace('B', '')

    try:
        return float(liquidity_str) * multiplier
    except ValueError:
        logging.warning(f"Could not parse liquidity value: '{liquidity_str}'")
        return 0.0

# Print token data to the console
def display_token_data(token_data):
    for token in token_data:
        print(f"\nToken Name: {token['Token Name']}")
        print(f"Analyzed Date: {token['Analyzed Date']}")
        print(f"Time: {token['Time']}")
        print(f"Price: {token['Price']}")
        print(f"Additional Value: {token['Additional Value']}")
        print(f"Change Indicator: {token['Change Indicator']}")
        print(f"Change: {token['Change']}")
        print(f"Project Name: {token['Project Name']}")
        print(f"Liquidity: {token['Liquidity']}")
        print(f"Volume: {token['Volume']}")
        print(f"Market Cap: {token['Market Cap']}\n")

# Monitor for new token entries and update stored data
def monitor_token_changes(driver):
    last_extracted_tokens = []
    while True:
        # Get currently visible tokens
        current_tokens = extract_token_data(driver)

        # Identify new tokens not previously seen
        new_tokens = [token for token in current_tokens if token['Token Name'] not in existing_token_names]

        if new_tokens:
            logging.info(f"Detected {len(new_tokens)} new tokens.")
            display_token_data(new_tokens)

            # Save new tokens to JSON file
            existing_tokens.extend(new_tokens)
            with open('tokens_data.json', 'w') as f:
                json.dump(existing_tokens, f, indent=4)
            logging.info(f"Added {len(new_tokens)} new tokens to the JSON file.")

            # Update set of known token names
            existing_token_names.update(token['Token Name'] for token in new_tokens)

        # Save snapshot of last extracted tokens
        last_extracted_tokens = current_tokens

        # Wait before scanning again
        sleep(2)

try:
    # Start the monitoring loop
    monitor_token_changes(driver)

finally:
    # Clean up and log total script runtime
    driver.quit()
    script_end_time = time()
    logging.info(f"Script execution completed. Total time taken: {script_end_time - start_time:.2f} seconds")