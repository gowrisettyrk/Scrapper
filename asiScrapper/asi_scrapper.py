import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

def select_date(driver, target_day, monument_id,monument_name):
    """ Selects a specific date from the calendar for the given monument. """
    wait = WebDriverWait(driver, 10)

    try:
        # Find the date input field for the specific monument based on its name
        visit_date_input = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@class='visitcalendar' and @id='{monument_id}']")))
        driver.execute_script("arguments[0].click();", visit_date_input)
        time.sleep(1)

        # Find all active days and click on the correct one
        available_days = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'day') and not(contains(@class, 'disabled'))]")))

        for day_element in available_days:
            if day_element.text.strip() == str(target_day):
                day_element.click()
                time.sleep(1)
                break
    except Exception as e:
        print(f"Error while selecting date for {monument_name}")
        # Close the monument by clicking the close button
        close_button = driver.find_element(By.XPATH, f"//input[@id='{monument_id}']/ancestor::div[@class='item setMargin']//img[@src='assets/images/icons/cancel.png']")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(1)  # Wait after closing
        

def select_time_slot(driver, time_slot="forenoon", monument_id=0,monument_name=""):
    """ Selects the visiting time from the dropdown for the specific monument. """
    wait = WebDriverWait(driver, 10)

    try:
        # Locate the time dropdown for the specific monument based on its name
        time_dropdown = wait.until(EC.visibility_of_element_located((By.XPATH, f"//input[@id='{monument_id}']/ancestor::div[@class='item setMargin']//select[contains(@class, 'selectTimeSlot')]")))

        # Create Select object
        select = Select(time_dropdown)

        # Select "forenoon" or "afternoon"
        if time_slot.lower() == "forenoon":
            select.select_by_visible_text("forenoon")
        elif time_slot.lower() == "afternoon":
            select.select_by_visible_text("afternoon")

        time.sleep(1)
    except Exception as e:
        print(f"Error while selecting time slot for {monument_name} : {e}")
        # Close the monument by clicking the close button
        close_button = driver.find_element(By.XPATH, f"//input[@id='{monument_id}']/ancestor::div[@class='item setMargin']//img[@src='assets/images/icons/cancel.png']")
        driver.execute_script("arguments[0].click();", close_button)
        time.sleep(1)  # Wait after closing


def click_right_arrow(driver):
    """ Clicks the right arrow button to proceed. """
    wait = WebDriverWait(driver, 10)

    # Locate the right arrow button
    right_arrow = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@class, 'rightArrow')]")))

    # Click on the arrow to navigate to the next page
    right_arrow.click()
    time.sleep(2)

def click_left_arrow(driver):
    """ Clicks the right arrow button to proceed. """
    wait = WebDriverWait(driver, 10)

    # Locate the right arrow button
    left_arrow = wait.until(EC.element_to_be_clickable((By.XPATH, "//img[contains(@class, 'leftArrow hidden-xs')]")))

    # Click on the arrow to navigate to the next page
    left_arrow.click()

    time.sleep(2)

def select_nationality(driver, nationality="Indian"):
    try:
        """ Selects the nationality radio button. """
        wait = WebDriverWait(driver, 10)

        # Find the nationality radio button by its ID and click it
        nationality_xpath = f"//input[@id='{nationality}']"
        nationality_button = wait.until(EC.element_to_be_clickable((By.XPATH, nationality_xpath)))
        nationality_button.click()
        time.sleep(1)
    except Exception as e:
        print(f"Error selecting Nationality: {str(e)}")

def add_adult_visitor(driver):
    """ Clicks the 'Add Adult' button. """
    wait = WebDriverWait(driver, 10)

    # Locate the 'Add Adult' button and click it
    add_adult_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Adult')]")))
    add_adult_button.click()
    time.sleep(1)

def get_ticket_price(driver):
    """ Extracts the ticket price. """
    wait = WebDriverWait(driver, 10)

    # Locate all <h4> elements inside div with class 'upperBorder'
    price_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'upperBorder')]/h4")))

    # Find the first element that contains "₹" to ensure it's a price
    ticket_price = next((elem.text.strip() for elem in price_elements if "₹" in elem.text), "Price Not Found")

    return ticket_price

def get_monument_prices(driver):
    """Extract monument prices from the payment page."""
    monument_prices = []

    wait = WebDriverWait(driver, 10)
    summary_rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='srollDiv text-center']//div[@class='item row']")))
    for row in summary_rows:
        try:
            # Get the monument name
            monument_name = row.find_element(By.XPATH, ".//div[@class='col-xs-12 col-sm-3 col-md-3 col-lg-3 rightBorder']//h6").text.strip()
            # Get the price from the last <h6> element
            price_text = row.find_element(By.XPATH, ".//div[@class='col-xs-6 col-sm-3 col-md-3 col-lg-3 ']//h6").text.strip()
            
            # Extract the numeric price from the text
            price = price_text.split('=')[-1].strip()
            # Add the monument and price to the list
            monument_prices.append(f"{monument_name}|{price}")
            
        except Exception as e:
            print(f"Error extracting price for monument: {str(e)}")
    
    return monument_prices


def process_ticket_booking(driver):
    """Handles selecting nationality, adding an adult, and extracting the price."""
    try:
        select_nationality(driver, "Indian")
        time.sleep(2)

        monument_prices_ind = get_monument_prices(driver)
        if not monument_prices_ind:
            print("No prices found for Indian nationality.")
            return []

        select_nationality(driver, "Foreigner")
        time.sleep(2)

        monument_prices_frgn = get_monument_prices(driver)
        if not monument_prices_frgn:
            print("No prices found for Foreigner nationality.")
            return []

        # Combine prices for each monument and store structured results
        combined_prices = []
        for ind_price, frgn_price in zip(monument_prices_ind, monument_prices_frgn):
            try:
                monument_and_indian_price = ind_price.rsplit('|', 1)  # Ensure only the last occurrence is split
                monument, indian_price = monument_and_indian_price
                _, foreigner_price = frgn_price.rsplit('|', 1)
                combined_prices.append(f"{monument.strip()}|{indian_price.strip()}|{foreigner_price.strip()}")
            except ValueError as ve:
                print(f"Error combining prices: {ve}")

        # Print all combined monument prices
        for price_entry in combined_prices:
            print(price_entry)

        return combined_prices

    except Exception as e:
        print(f"Error in process_ticket_booking: {e}")
        return []


def close_all_selected_monuments(driver):
    """Closes all selected monuments by clicking their close buttons."""
    wait = WebDriverWait(driver, 5)

    try:
        close_buttons = driver.find_elements(By.XPATH, "//img[@src='assets/images/icons/cancel.png']")
        for button in close_buttons:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)  # Wait a bit after each close action
    except Exception as e:
        print("No selected monuments found to close.")

def scrape_asi_data():
    driver = webdriver.Chrome()
    driver.get("https://asi.payumoney.com/select/1")
    
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)

    # Locate all city radio buttons
    city_radio_buttons = wait.until(EC.presence_of_all_elements_located((By.NAME, "stategroup")))
    print(f"Found {len(city_radio_buttons)} cities.")
    
    # Store all city and monument details in this list
    all_data = []

    for city_index in range(len(city_radio_buttons)):
        try:
            city_radio_buttons = wait.until(EC.presence_of_all_elements_located((By.NAME, "stategroup")))
            city_element = city_radio_buttons[city_index]

            city_name = city_element.get_attribute("value").strip()
            print(f"Selecting city: {city_name}")
            actions.move_to_element(city_element).click().perform()

            # Select the city radio button
            actions.move_to_element(city_element).click().perform()
            time.sleep(2)  # Allow time for the page to refresh

            # Wait for the monument section to appear
            monument_checkboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']")))

            print(f"Found {len(monument_checkboxes)} monuments in {city_name}.")

            for monument_checkbox in monument_checkboxes:
                try:
                    monument_id = monument_checkbox.get_attribute("value").strip()
                    monument_name = monument_checkbox.get_attribute("name").strip()
                    monument_checkbox.click()
                    time.sleep(1)

                    # Select the visit date
                    select_date(driver, 18, monument_id,monument_name) 

                    select_time_slot(driver, "forenoon", monument_id,monument_name)
    
                except Exception as e:
                    print(f"Error processing monument {monument_name}")
                    continue
            
            click_right_arrow(driver)

            monument_and_price = process_ticket_booking(driver)

            click_left_arrow(driver)

            close_all_selected_monuments(driver)

            data = []
            for monument in monument_and_price:
                # Ensure correct splitting into city, monument, and prices
                parts = monument.split('|')
                monument_name, ind_price, frgn_price = parts[0].strip(), parts[1].strip(), parts[2].strip()
                # Trim spaces

                data.append({
                    "City": city_name,
                    "Monument": monument_name,
                    "Ind_Price": ind_price,
                    "Frgn_price": frgn_price
                })
            all_data.extend(data)
            print(all_data)
            time.sleep(2)            

        except Exception as e:
            print(f"Error while processing city {city_name}:{e}")
            continue
    
    #Save data to CSV
    file_exists = os.path.isfile("asi_monuments_pricing1.csv")

    with open("asi_monuments_pricing1.csv", "a", newline="", encoding="utf-8") as file:
        fieldnames = ["City", "Monument", "Ind_Price","Frgn_price"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
                
        if not file_exists:
            writer.writeheader()  # Write header only if file doesn't exist    
        writer.writerows(all_data)

    print("Data saved to asi_monuments_pricing1.csv")

    driver.quit()

if __name__ == "__main__":
    scrape_asi_data()
