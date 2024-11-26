import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from appium.webdriver.extensions.clipboard import Clipboard
import json
from time import sleep, time

# Map blockchain name to chain ID used by DexScreener API
blockchain_name_to_chain_id = {
                'ETHEREUM': 'ethereum',
                'BASE': 'base',
                'BSC': 'bsc',
                'SOLANA': 'solana',
                'ARBITRUM': 'arbitrum',
                'AVALANCHE': 'avalanche',
                'POLYGON': 'polygon',
                'OPTIMISM': 'optimism',
                'SUI': 'sui',
                'TON': 'ton',
                'CELO': 'celo',
                'PULSECHAIN': 'pulsechain',
                'OSMOSIS': 'osmosis',
                'MANTLE': 'mantle',
                'SEIV2': 'seiv2',
                'FANTOM': 'famtom',
                'BLAST': 'blast',
                'APTOS': 'aptos',
                'LINEA': 'linea',
                'CRONOS': 'cronos',
                'STARKNET': 'starknet',
                'CORE': 'core',
                'TRON': 'tron',
                'HEDERA': 'hedera',
                'MOONBEAM': 'moonbeam',
                'SCROLL': 'scroll',
                'METIS': 'metis',
                'CARDANO': 'cardano',
                'ZKSYNC': 'zksync',
                'GNOSIS CHAIN': 'gnosischain',
                'NEAR': 'near',
                'ALGORAND': 'algorand',
                'MULTIVERSX': 'multiversx',
                'POLYGON ZKEVM': 'polygonzkevm',
                'MANTA': 'manta',
                'HYPER LIQUID': 'hyperliquid',
                'MERLIN CHAIN': 'merlinchain',
                'FLARE': 'flare',
                'WORLD CHAIN': 'worldchain',
                'KAVA': 'kava',
                'WORLD CHAIN': 'worldchain',
                'IOTEX': 'iotex',
                'OPBNB': 'opbnb',
                'AURORA': 'aurora',
                'CONFLUX': 'conflux',
                'CANTO': 'canto',
                'MODE': 'mode',
                'APECHAIN': 'apechain',
                'ICP': 'icp',
                'ASTAR': 'astar',
                'INJECTIVE': 'injective',
                'BEAM': 'beam',
                'BOUNCEBIT': 'bouncebit',
                'MOONDRIVER': 'moondriver',
                'FILECOIN': 'filecoin',
                # Ajoutez d'autres mappages si nécessaire
            }

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the options
options = UiAutomator2Options()
options.platformName = 'Android'
options.deviceName = '4672d93b' #Remplacer par votre numéro de device
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
sleep(8)
# Function to clean and align the extracted data
def clean_and_align_data(token_data):
    # Initialize with default values
    cleaned_data = {
        "Token Name": token_data[0] if len(token_data) > 0 else "N/A",
        "Time": token_data[1] if len(token_data) > 1 else "N/A",
        "Price": token_data[2] if len(token_data) > 2 else "N/A",
        "Price Adjustment": "",
        "Change Indicator": "",
        "Change": "",
        "Project Name": "",
        "Liquidity": "",
        "Volume": "",
        "Market Cap": "",
        "Go+ Security": ""
    }

    index = 3  # Start after the price

    # Check if there's a price adjustment (number after Price)
    if len(token_data) > index and token_data[index].isdigit():
        cleaned_data["Price Adjustment"] = token_data[index]
        index += 1

    # Extract the change indicator and change
    cleaned_data["Change Indicator"] = token_data[index] if len(token_data) > index else ""
    index += 1
    cleaned_data["Change"] = token_data[index] if len(token_data) > index else ""
    index += 1

    # Extract the project name
    cleaned_data["Project Name"] = token_data[index] if len(token_data) > index else ""
    index += 1

    # Handle the liquidity, volume, and market cap values
    while index < len(token_data):
        key = token_data[index]
        value = token_data[index + 1] if index + 1 < len(token_data) else ""
        if key == "LIQ":
            cleaned_data["Liquidity"] = value
        elif key == "VOL":
            cleaned_data["Volume"] = value
        elif key == "MCAP":
            cleaned_data["Market Cap"] = value
        index += 2

    return cleaned_data


# Scroll function
def scroll_down(driver):
    try:
        # Get the screen size
        window_size = driver.get_window_size()
        start_x = window_size["width"] // 2
        start_y = int(window_size["height"] * 0.8)
        end_y = int(window_size["height"] * 0.2)

        driver.swipe(start_x, start_y, start_x, end_y, 600)
    except Exception as e:
        logging.warning(f"Error during scrolling: {e}")

# Scroll function adjusted for the home page to avoid bottom buttons
def scroll_down_home_page(driver):
    try:
        # Get the screen size
        window_size = driver.get_window_size()
        start_x = window_size["width"] // 2
        start_y = int(window_size["height"] * 0.5)  # Start scroll higher on the screen
        end_y = int(window_size["height"] * 0.2)    # End scroll higher to avoid bottom buttons

        driver.swipe(start_x, start_y, start_x, end_y, 600)
    except Exception as e:
        logging.warning(f"Error during scrolling: {e}")

def scroll_up(driver):
    try:
        # Obtenir la taille de l'écran
        window_size = driver.get_window_size()
        start_x = window_size["width"] // 2
        start_y = int(window_size["height"] * 0.2)  # Commence plus bas sur l'écran
        end_y = int(window_size["height"] * 0.8)    # Termine plus haut sur l'écran

        driver.swipe(start_x, start_y, start_x, end_y, 600)
    except Exception as e:
        logging.warning(f"Error during scrolling up: {e}")

def scroll_to_top(driver):
    max_scroll_attempts = 10  # Limiter le nombre de tentatives pour éviter une boucle infinie
    for _ in range(max_scroll_attempts):
        scroll_up(driver)
        sleep(1)  # Attendre que le défilement soit terminé

def extract_price_from_detail_page(driver):
    try:
        # Locate the TextView with text "PRICE USD"
        price_label_element = driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="PRICE USD"]')
        if price_label_element:
            logging.info("Found 'PRICE USD' TextView.")

            # Locate the sibling TextView containing the price value
            price_value_element = driver.find_element(
                AppiumBy.XPATH,
                '//android.widget.TextView[@text="PRICE USD"]/following-sibling::android.widget.TextView'
            )

            if price_value_element:
                price_text = price_value_element.get_attribute('text')
                logging.info(f"Price text found: {price_text}")
                return price_text
            else:
                logging.warning("Price value TextView not found after 'PRICE USD'.")
                return None
        else:
            logging.warning("TextView with text 'PRICE USD' not found.")
            return None
    except NoSuchElementException as e:
        logging.warning(f"Exception locating price elements: {e}")
        return None


# Extract the last 8 tokens from the visible elements on the screen
def extract_basic_token_data(driver):
    tokens_data = []
    try:
        logging.info("Sending request to locate ViewGroup elements with content-desc attribute")
        request_time = datetime.now()
        elements = driver.find_elements(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc]')
        response_time = datetime.now()
        logging.info(f"Response received. Request sent at: {request_time}, Response received at: {response_time}")

        screen_bottom_y = 2040  # Start of the button area at the bottom of the screen
        for element in elements:
            try:
                # Get the element's coordinates to ensure it is not in the button area
                element_location = element.rect
                if element_location['y'] >= screen_bottom_y:
                    logging.info(f"Skipping element in button area: {element.get_attribute('content-desc')}")
                    continue  # Skip this element as it is in the button area

                content_desc = element.get_attribute('content-desc')
                if content_desc and not any(keyword in content_desc for keyword in ["Trending", "Moonshot", "Newest"]):
                    token_data = content_desc.split(', ')
                    print(token_data)
                    cleaned_data = clean_and_align_data(token_data)
                    print(cleaned_data)
                    tokens_data.append((element, cleaned_data))
                    if len(tokens_data) >= 8:  # Stop after collecting 8 tokens
                        break

            except StaleElementReferenceException:
                logging.warning("Encountered a stale element, skipping...")
                continue

    except StaleElementReferenceException:
        logging.warning("Encountered a stale element reference, retrying...")
        tokens_data = extract_basic_token_data(driver)

    return tokens_data


# Function to ensure a token is visible by scrolling down until it's found
def ensure_token_is_visible(driver, token_name):
    max_scroll_attempts = 5  # Number of scroll attempts before giving up
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        elements = driver.find_elements(AppiumBy.XPATH, '//android.view.ViewGroup[@content-desc]')
        for element in elements:
            try:
                content_desc = element.get_attribute('content-desc')
                if token_name in content_desc:
                    logging.info(f"Token '{token_name}' found on attempt {scroll_attempts + 1}.")
                    return element  # Token is found and returned

            except StaleElementReferenceException:
                logging.warning("Stale element encountered while searching for token, retrying...")

        # If token is not found in the current view, scroll down and try again
        logging.info(f"Token '{token_name}' not found, scrolling down (Attempt {scroll_attempts + 1})...")
        scroll_down_home_page(driver)
        sleep(3)  # Wait for new elements to load

        scroll_attempts += 1

    logging.warning(f"Token '{token_name}' not found after {max_scroll_attempts} attempts.")
    return None  # Token wasn't found after the maximum number of scrolls


# Function to check if the element is clearly visible and not obstructed by buttons
def is_token_fully_visible(driver, element):
    try:
        # Get the element's location on the screen
        element_location = element.location
        element_size = element.size
        
        # Coordinates of the buttons that may obstruct elements
        button_coords = {"left_x": 0, "top_y": 2040, "right_x": 1080, "bottom_y": 2187}

        # Check if the element is within the obstructed area
        if (
            element_location["x"] >= button_coords["left_x"]
            and element_location["x"] + element_size["width"] <= button_coords["right_x"]
            and element_location["y"] + element_size["height"] > button_coords["top_y"]
        ):
            return False  # The element is obstructed
        return True  # The element is not obstructed
    except Exception as e:
        logging.warning(f"Error while checking token visibility: {e}")
        return False

# Function to clear the clipboard before copying
def clear_clipboard(driver):
    try:
        driver.set_clipboard_text("")  # Clear the clipboard by setting it to an empty string
        logging.info("Clipboard cleared.")
    except Exception as e:
        logging.warning(f"Error while clearing clipboard: {e}")

def extract_full_hashes_via_clipboard(driver, token_name, blockchain_name):
    try:
        scroll_down(driver)
        sleep(2)
        # Clear the clipboard before starting
        clear_clipboard(driver)

        # --- First Hash Extraction ---
        try:
            # Locate the TextView with text "Pair"
            pair_text_element = driver.find_element(AppiumBy.XPATH, '//android.widget.TextView[@text="Pair"]')
            if pair_text_element:
                logging.info("Found 'Pair' TextView.")

                # Locate the sibling ViewGroup containing the copy button after 'Pair'
                pair_copy_button = driver.find_element(
                    AppiumBy.XPATH,
                    '//android.widget.TextView[@text="Pair"]/following-sibling::android.view.ViewGroup//android.widget.TextView[@text=""]'
                )

                if pair_copy_button:
                    pair_copy_button.click()
                    logging.info("Clicked the first copy button after 'Pair'.")
                    sleep(1)  # Wait for the hash to be copied to the clipboard

                    # Retrieve the first hash from the clipboard
                    first_hash = driver.get_clipboard_text()
                    logging.info(f"First hash retrieved from clipboard: {first_hash}")
                else:
                    logging.warning("First copy button not found after 'Pair'.")
                    first_hash = "First hash not available"
            else:
                logging.warning("TextView with text 'Pair' not found.")
                first_hash = "First hash not available"
        except NoSuchElementException as e:
            logging.warning(f"Exception locating first hash: {e}")
            first_hash = "First hash not available"

        # Clear the clipboard before copying the second hash
        clear_clipboard(driver)

        # --- Second Hash Extraction ---
        try:
            # Locate the TextView with the token name
            token_text_element = driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{token_name}"]')
            if token_text_element:
                logging.info(f"Found token name TextView: '{token_name}'.")

                # Locate the sibling ViewGroup containing the copy button after the token name
                token_copy_button = driver.find_element(
                    AppiumBy.XPATH,
                    f'//android.widget.TextView[@text="{token_name}"]/following-sibling::android.view.ViewGroup//android.widget.TextView[@text=""]'
                )

                if token_copy_button:
                    token_copy_button.click()
                    logging.info("Clicked the second copy button after token name.")
                    sleep(1)  # Wait for the hash to be copied to the clipboard

                    # Retrieve the second hash from the clipboard
                    second_hash = driver.get_clipboard_text()
                    logging.info(f"Second hash retrieved from clipboard: {second_hash}")
                else:
                    logging.warning("Second copy button not found after token name.")
                    second_hash = "Second hash not available"
            else:
                logging.warning(f"TextView with token name '{token_name}' not found.")
                second_hash = "Second hash not available"
        except NoSuchElementException as e:
            logging.warning(f"Exception locating second hash: {e}")
            second_hash = "Second hash not available"

        return first_hash, second_hash

    except Exception as e:
        logging.warning(f"Error while extracting hashes via clipboard: {e}")
        return "Error retrieving hash", "Error retrieving hash"

def get_blockchain_name(driver, token_info):
    try:
        # Obtenir tous les éléments android.view.ViewGroup avec un content-desc non vide et cliquable
        elements = driver.find_elements(AppiumBy.XPATH, "//android.view.ViewGroup[@content-desc!='' and @clickable='true']")
        logging.info(f"Found {len(elements)} elements with non-empty content-desc and clickable.")
        blockchain_name = ""
        for element in elements:
            content_desc = element.get_attribute('content-desc')
            logging.info(f"Found element with content-desc: '{content_desc}'")
            # Vérifier si le content_desc correspond à un nom de blockchain connu
            if content_desc.upper() in blockchain_name_to_chain_id:
                blockchain_name = content_desc
                logging.info(f"Blockchain name found: '{blockchain_name}'")
                token_info["Blockchain Name"] = blockchain_name
                break  # Quitter la boucle une fois le nom de la blockchain trouvé
        if blockchain_name == "":
            logging.warning("Blockchain name not found among elements with content-desc.")
        return blockchain_name
    except Exception as e:
        logging.warning(f"Error retrieving blockchain name: {e}")
        return ""

def process_tokens(driver, tokens_data):
    simulated_purchases = []
    for _, token_info in tokens_data:
        try:
            # Get the token name
            token_name = token_info.get("Token Name", "Unknown")
            logging.info(f"Processing token: {token_name}")

            # Ensure the token is visible on the screen and get a fresh element reference
            element = ensure_token_is_visible(driver, token_name)
            if element is None:
                logging.warning(f"Token '{token_name}' not found after scrolling. Skipping.")
                logging.info("Scrolling back to the top before proceeding to the next token.")
                scroll_to_top(driver)
                continue  # Skip to the next token

            # Click on the token element
            element.click()
            sleep(5)  # Wait for the detail page to load


            # --- Retrieve Blockchain Name ---
            blockchain_name = get_blockchain_name(driver, token_info)
            print(blockchain_name)

            # Get the chain_id from the mapping
            chain_id = blockchain_name_to_chain_id.get(blockchain_name.upper(), '')
            if chain_id:
                logging.info(f"Mapped blockchain name '{blockchain_name}' to chain ID '{chain_id}'")
            else:
                logging.warning(f"Could not map blockchain name '{blockchain_name}' to a chain ID")
            token_info['Chain ID'] = chain_id

            # Extract the hashes using the updated function
            first_hash, second_hash = extract_full_hashes_via_clipboard(driver, token_name, blockchain_name)
            token_info["Full Hash 1"] = first_hash
            token_info["Full Hash 2"] = second_hash

            # Simulate the purchase
            try:
                # Get the price from token_info
                price_str = token_info.get("Price", "0")
                # Remove any currency symbols or commas
                price_str = price_str.replace('$', '').replace(',', '').strip()

                if price_str == '':
                    price = 0.0
                else:
                    price = float(price_str)

                # Check if there's a price adjustment
                price_adjustment_str = token_info.get("Price Adjustment", "")
                if price_adjustment_str.isdigit():
                    zeros_missing = int(price_adjustment_str)
                    price *= 10 ** (1 - zeros_missing + 1)
                    logging.info(f"Adjusted price for '{token_name}' with {zeros_missing} missing zeros: {price}")
                else:
                    logging.info(f"No price adjustment needed for '{token_name}'.")

                if price > 0:
                    # Calculate the amount of tokens purchased with $1
                    amount_tokens = 1 / price
                else:
                    amount_tokens = 0.0

                # Obtenir la date et l'heure actuelles
                purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Create a dictionary with the purchase data
                purchase_data = {
                    "Token Name": token_name,
                    "Full Hash 1": first_hash,
                    "Full Hash 2": second_hash,
                    "Purchase Price": price,
                    "Purchase Amount ($)": 1,
                    "Amount of Tokens Purchased": amount_tokens,
                    "Chain ID": chain_id,
                    "Purchase Date": purchase_date
                }
                simulated_purchases.append(purchase_data)
                logging.info(f"Simulated purchase for token '{token_name}': {purchase_data}")
            except Exception as e:
                logging.warning(f"Error simulating purchase for token '{token_name}': {e}")
            # Navigate back to the previous page
            driver.back()
            sleep(3)  # Wait for the page to load

        except Exception as e:
            logging.warning(f"Error processing token '{token_name}': {e}")
            continue

    return tokens_data, simulated_purchases


try:
    # Record the start time for the extraction process
    extraction_start_time = time()

    # Step 1: Extract basic token data
    basic_token_data = extract_basic_token_data(driver)

    # Step 2: Process each token and retrieve both full hashes
    full_token_data, simulated_purchases = process_tokens(driver, basic_token_data)

    extraction_end_time = time()
    logging.info(f"Data extraction completed. Time taken: {extraction_end_time - extraction_start_time:.2f} seconds")

    # Save the token data to a JSON file
    with open('pair_hash.json', 'w') as f:
        json.dump([info for _, info in full_token_data], f, indent=4)
    logging.info("Token data successfully saved to pair_hash.json")

    # Save the simulated purchases to a JSON file
    with open('simulated_purchases.json', 'w') as f:
        json.dump(simulated_purchases, f, indent=4)
    logging.info("Simulated purchase data successfully saved to simulated_purchases.json")

finally:
    # Close the driver and log the time taken for the entire script execution
    driver.quit()
    script_end_time = time()
    logging.info(f"Script execution completed. Total time taken: {script_end_time - start_time:.2f} seconds")
