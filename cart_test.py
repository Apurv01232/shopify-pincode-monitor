from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

# Configuration
VALID_PINCODE = "400001"  # Replace with valid pincode
CART_URL = "https://tugain.in/cart"  # Cart page URL

def test_add_to_cart():
    with open("products.txt", "r") as f:
        product_urls = f.read().splitlines()
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Disable headless for debugging
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"cart_test_{timestamp}.log"
    
    for url in product_urls:
        try:
            print(f"Testing product: {url}")
            driver.get(url)
            product_name = driver.title.split("|")[0].strip()
            print(f"Product Name: {product_name}")
            
            # Step 1: Product viewed
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"[INFO] Product viewed: {product_name} | {url}\n")
            print(f"Product viewed: {product_name}")

            # Step 2: Enter pincode
            pincode_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "pincode"))
            )
            pincode_input.clear()
            pincode_input.send_keys(VALID_PINCODE)
            driver.find_element(By.ID, "pinCode_button").click()
            
            # Verify delivery available
            WebDriverWait(driver, 20).until(
                EC.text_to_be_present_in_element((By.ID, "successMessage"), "Delivery Available")
            )
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"[INFO] Pincode entered and delivery available for: {product_name} | {url}\n")
            print(f"Pincode entered and delivery available for: {product_name}")

            # Step 3: Check if product is sold out
            try:
                sold_out_message = driver.find_element(By.CSS_SELECTOR, ".main-product__form-error-message-wrapper").text
                if "sold out" in sold_out_message.lower():
                    status = "CART EMPTY: Product out of stock"
                    with open(log_file, "a", encoding="utf-8") as log:
                        log.write(f"[INFO] Sold-out message for {product_name} | {url} | Status: {status}\n")
                    print(f"Product {product_name} is out of stock. Cart is empty.")
                    # Still go to the cart page but log that the cart is empty
                else:
                    status = "SUCCESS"  # Product is not sold out, we proceed
            except:
                status = "SUCCESS"  # No sold-out message found, proceed to add to cart

            # Step 4: Add to cart (only if product is not sold out)
            try:
                add_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "disabled_button"))
                )
                add_button.click()
                time.sleep(3)  # Wait for cart to update
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[INFO] Added to cart: {product_name} | {url}\n")
                print(f"Added to cart: {product_name}")
            except:
                print(f"Failed to add product {product_name} to cart. Moving to the next product.")
                status = "CART EMPTY: Product not added to cart"
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[INFO] Failed to add to cart for {product_name} | {url}\n")
                continue  # Skip to the next product if add to cart fails

            # Step 5: Open cart page to check cart items
            driver.get(CART_URL)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-item__content"))
            )

            # Check if cart is empty
            cart_items = driver.find_elements(By.CSS_SELECTOR, ".cart-item__content")
            if not cart_items:
                status = "CART EMPTY: No items in the cart"
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[INFO] Cart empty for {product_name} | {url} | Status: {status}\n")
                print(f"Cart is empty for product {product_name}.")
                continue  # Skip to the next product in the list

            # Get all the cart items
            cart_item_urls = [item.find_element(By.CSS_SELECTOR, "a").get_attribute("href") for item in cart_items]

            # Only check for the current product (without the variant part)
            base_url = url.split("?")[0]  # Base URL without the variant part
            variant_in_url = None
            if "?" in url:
                variant_in_url = url.split("?")[-1]  # Variant parameter part

            # Step 6: Check for matching variant or product URL in the cart
            for cart_item_url in cart_item_urls:
                cart_base_url = cart_item_url.split("?")[0]  # Base URL of the cart item
                if variant_in_url and variant_in_url in cart_item_url:
                    variant_status = "SUCCESS"  # Variant exists in the cart
                    break
                elif variant_in_url is None and cart_base_url == base_url:
                    variant_status = "SUCCESS"  # Product without variant exists in the cart
                    break

            # Step 7: Log results
            if variant_status == "SUCCESS":
                status = "SUCCESS"
            else:
                status = f"FAILURE: Product not found or variant issue. Cart items: {', '.join(cart_item_urls)}"

            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"[INFO] Checking cart for {product_name} | {url} | Status: {status}\n")
            print(f"Checked cart for {product_name}, Status: {status}")

            # Step 8: Remove items from cart for next test
            remove_buttons = driver.find_elements(By.CSS_SELECTOR, "cart-remove-button a.button-link")
            for button in remove_buttons:
                button.click()
                time.sleep(1)  # Wait for item removal
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[INFO] Removed from cart: {product_name} | {url}\n")
                print(f"Removed from cart: {product_name}")

        except Exception as e:
            status = f"ERROR: {str(e)}"
            driver.save_screenshot(f"error_{timestamp}.png")
            print(f"Error occurred: {e}")
        
        # Log results for each product
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"[INFO] Test completed for {product_name} | {url} | Status: {status}\n")
    
    driver.quit()
    print(f"Tests completed! Check {log_file} for results.")

test_add_to_cart()
