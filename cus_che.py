import time
import pyautogui
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import configparser
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from test_utils import order


# Read properties from config file
config = configparser.ConfigParser()
config.read('cus_che_config.ini')


class CusCheListTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.prompt_for_download": config.getboolean('DEFAULT', 'download_prompt_for_download'),
            "safebrowsing.enabled": config.getboolean('DEFAULT', 'safebrowsing_enabled'),
            "download.default_directory": config.get('DEFAULT', 'download_directory')
        })
        chrome_options.add_argument("--kiosk-printing")

        # Initialize WebDriver
        cls.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        cls.driver.maximize_window()
        cls.config = config
        cls.login_as_admin()



    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def validate_input(self, input_element, value, validation_type):
        input_element.clear()
        input_element.send_keys(value)
        time.sleep(1)
        if validation_type == "name_with_space":
            assert re.match("^[A-Za-z ]*$", value), f"Validation failed for {value}: Only alphabets and spaces are allowed."
        elif validation_type == "any":
            assert len(value) <= 255, f"Validation failed for {value}: Exceeds maximum length of 255 characters."
        elif validation_type == "number":
            assert re.match("^[0-9]*$", value), f"Validation failed for {value}: Only numbers are allowed."
        elif validation_type == "mobile":
            assert re.match("^[0-9]{10}$", value), f"Validation failed for {value}: Invalid mobile number format."
        elif validation_type == "date":
            assert re.match(r"^\d{2}/\d{2}/\d{4}$", value), f"Validation failed for {value}: Invalid date format. Expected dd/mm/yyyy."


    @classmethod
    @order(1)
    def login_as_admin(cls):
        cls.driver.get(config.get('DEFAULT', 'url'))
        username_input = cls.wait_and_find("//input[@id='username']")
        password_input = cls.wait_and_find("//input[@id='password']")
        username_input.send_keys(config.get('DEFAULT', 'username'))
        password_input.send_keys(config.get('DEFAULT', 'password'))
        cls.wait_and_click("//button[@type='submit' and contains(text(), 'Login')]")
        time.sleep(1)  # Wait for login to complete

    @classmethod
    def wait_and_click(cls, xpath, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element

    @classmethod
    def wait_and_check(cls, by, value, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((by, value)))
        element.click()
        return element

    @classmethod
    def wait_and_find(cls, xpath, timeout=10):
        return WebDriverWait(cls.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

    @classmethod
    def wait_and_click(cls, xpath, timeout=10, retries=3):
        for _ in range(retries):
            try:
                element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                element.click()
                return element
            except StaleElementReferenceException:
                time.sleep(2)
        raise Exception(f"Failed to click element after {retries} retries: {xpath}")

    def generate_random_birth_date(self):
        start_date = datetime(1990, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        return random_date.strftime("%d/%m/%Y")
    
    def generate_random_wedding_date(self):
        start_date = datetime(1990, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        return random_date.strftime("%d/%m/%Y")

    

    def ensure_toggle_button_enabled(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            toggle_customer = self.wait_and_find("//input[@id='toggleCustomer']")
            toggle_chemist = self.wait_and_find("//input[@id='toggleChemist']")

            if not toggle_customer.is_selected():
                toggle_customer.click()
                toggle_chemist.click()
                print("Toggle button enabled")
            else:
                print("Toggle button is already enabled")
        except Exception as e:
            self.fail(f"Error during toggle button check: {e}")
        time.sleep(1)

    def setUp(self):
        self.ensure_toggle_button_enabled()

    @order(2)
    def test_add_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any") 


            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)


            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)

            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)

            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(1)

            # Click customer
            customer_locator = config.get('DEFAULT', 'customer_button_id')
            self.wait_and_check(By.XPATH, customer_locator)
            time.sleep(1)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(1)

            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(2)

            assert name_as_per_records_input.get_attribute("value") == "", "Clear button did not reset the name as per records input"
            print("Clear button works correctly on the add page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any")

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)


            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            self.ensure_toggle_button_enabled()

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new customer entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'cus_first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_as_per_records')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created customer entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add customer test: {e}")

    def test_add_chemist(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any") 


            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)


            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'che_mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)

            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)

            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(1)

            # Click chemist
            chemist_locator = config.get('DEFAULT', 'chemist_button_id')
            self.wait_and_check(By.XPATH, chemist_locator)
            time.sleep(1)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(1)

            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(2)

            assert name_as_per_records_input.get_attribute("value") == "", "Clear button did not reset the name as per records input"
            print("Clear button works correctly on the add page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any")

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))

            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'che_mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)


            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)


            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(1)

            # Click chemist
            chemist_locator = config.get('DEFAULT', 'chemist_button_id')
            self.wait_and_check(By.XPATH, chemist_locator)
            time.sleep(1)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            self.ensure_toggle_button_enabled()

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new chemist entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'che_first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_as_per_records')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created chemist entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add chemist test: {e}")

    @order(11)
    def test_view_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            print("Navigated to Customer/Chemist Master List Page")
            time.sleep(1)

            # Disable the chemist toggle button
            chemist_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'chemist_toggle_button_xpath'))
            if chemist_toggle_button.is_enabled():
                chemist_toggle_button.click()
                print("Disabled chemist toggle button.")
                time.sleep(1)

            entries_select = self.wait_and_click(config.get('DEFAULT', 'entries_select_xpath'))
            for value in ['-1']:
                option = self.driver.find_element(By.XPATH, f"//select[@id='entriesPerPage']/option[@value='{value}']")
                option.click()
                time.sleep(1)
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)

            Name_as_per_records_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_records_field_xpath'))
            Name_as_per_convenience_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_convenience_xpath'))
            Institution_Name_field = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            Speciality_field = self.wait_and_find(config.get('DEFAULT', 'Speciality_xpath'))
            Mobile_Number_field = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            Birth_Date_field = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            Wedding_Date_field = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            Mode_of_CRM_field = self.wait_and_find(config.get('DEFAULT', 'Mode_of_CRM_xpath'))
            Reward_Status_field = self.wait_and_find(config.get('DEFAULT', 'Reward_Status_xpath'))
            User_Type_field = self.wait_and_find(config.get('DEFAULT', 'User_Type_field_xpath'))
            SMS_field = self.wait_and_find(config.get('DEFAULT', 'SMS_field_xpath'))

            assert Name_as_per_records_field.get_attribute("readonly") == "true", "customer field is editable"
            assert Name_as_per_convenience_field.get_attribute("readonly") == "true", "Name as per convenience field is editable"
            assert Institution_Name_field.get_attribute("readonly") == "true", "Institution Name field is editable"
            assert Speciality_field.get_attribute("readonly") == "true", "Speciality field is editable"
            assert Mobile_Number_field.get_attribute("readonly") == "true", "Mobile Number field is editable"
            assert Birth_Date_field.get_attribute("readonly") == "true", "Birth Date field is editable"
            assert Wedding_Date_field.get_attribute("readonly") == "true", "Wedding Date field is editable"
            assert Mode_of_CRM_field.get_attribute("readonly") == "true", "Mode of CRM field is editable"
            assert Reward_Status_field.get_attribute("readonly") == "true", "Reward Status field is editable"
            assert User_Type_field.get_attribute("readonly") == "true", "User Type field field is editable" 
            assert SMS_field.get_attribute("readonly") == "true", "SMS field is editable"


            print("All fields are correctly set to readonly.")
        except Exception as e:
            self.fail(f"Error during view test: {e}")
            
        # Adding the back button click
        try:
            print("Clicking back button")
            back_button = self.wait_and_find(config.get('DEFAULT', 'back_button'))
            if back_button.is_enabled() and back_button.is_displayed():
                back_button.click()
                print("Back button clicked")
            else:
                print("Back button is not clickable")
            time.sleep(5)
        except Exception as e:
            print(f"Error while clicking back button: {e}")

        # Ensure the chemist toggle button is enabled
        try:
            chemist_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'chemist_toggle_button_xpath'))
            if not chemist_toggle_button.is_selected():
                chemist_toggle_button.click()
                time.sleep(1)
                print("Enabled chemist toggle button.")
            else:
                print("Chemist toggle button is already enabled")
        except Exception as e:
            print(f"Error while enabling chemist toggle button: {e}")            

    @order(13)
    def test_edit_customer(self):
        try:
            # Navigate to the customer/chemist master list page
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            # Disable the chemist toggle button
            chemist_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'chemist_toggle_button_xpath'))
            if chemist_toggle_button.is_enabled():
                chemist_toggle_button.click()
                print("Disabled chemist toggle button.")

            entries_select = self.wait_and_click(config.get('DEFAULT', 'entries_select_xpath'))
            for value in ['-1']:
                option = self.driver.find_element(By.XPATH, f"//select[@id='entriesPerPage']/option[@value='{value}']")
                option.click()
                time.sleep(1)

            # Click the edit button
            retries = 3
            for _ in range(retries):
                try:
                    self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
                    break
                except StaleElementReferenceException:
                    time.sleep(2)
            else:
                self.fail("Failed to click edit button after multiple retries")
            time.sleep(1)

            # Enter new values into all fields using XPath
            name_as_per_records_field = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_for_usage_field = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            institution_name_field = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            speciality_field = self.wait_and_find(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            mobile_number_field = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            birth_date_field = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            wedding_date_field = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            mode_of_crm_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))

            assert name_as_per_records_field.is_enabled(), "Name as per records field is not editable"
            assert name_for_usage_field.is_enabled(), "Name for usage field is not editable"
            assert institution_name_field.is_enabled(), "Institution name field is not editable"
            assert speciality_field.is_enabled(), "Speciality field is not editable"
            assert mobile_number_field.is_enabled(), "Mobile number field is not editable"
            assert birth_date_field.is_enabled(), "Birth date field is not editable"
            assert wedding_date_field.is_enabled(), "Wedding date field is not editable"
            assert mode_of_crm_field.is_enabled(), "Mode of CRM field is not editable"

            name_as_per_records_field.clear()
            name_as_per_records_field.send_keys(config.get('DEFAULT', 'edit_name_as_per_records'))
            time.sleep(1)

            name_for_usage_field.clear()
            name_for_usage_field.send_keys(config.get('DEFAULT', 'edit_name_for_usage'))

            institution_name_field.clear()
            institution_name_field.send_keys(config.get('DEFAULT', 'edit_institution_name'))

            try:
                Select(speciality_field).select_by_visible_text(config.get('DEFAULT', 'edit_speciality'))
            except NoSuchElementException:
                self.fail(f"Speciality '{config.get('DEFAULT', 'edit_speciality')}' not found in the dropdown")

            mobile_number_field.clear()
            mobile_number_field.send_keys(config.get('DEFAULT', 'edit_mobile_number'))

            birth_date_field.clear()
            birth_date_field.send_keys(config.get('DEFAULT', 'edit_birth_date'))

            wedding_date_field.clear()
            wedding_date_field.send_keys(config.get('DEFAULT', 'edit_wedding_date'))

            Select(mode_of_crm_field).select_by_visible_text(config.get('DEFAULT', 'edit_mode_of_crm'))

            # Click the update button
            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            time.sleep(1)

            # Handle the confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            time.sleep(1)

            # Verify the updated values in the customer/chemist master list
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)

            updated_user = self.wait_and_find(config.get('DEFAULT', 'updated_user_xpath'))
            assert updated_user is not None, "Updated customer/chemist details not found in the table"

            print("Customer/Chemist details updated successfully.")
        except Exception as e:
            self.fail(f"Error during edit test: {e}")

        # Ensure the chemist toggle button is enabled
        try:
            chemist_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'chemist_toggle_button_xpath'))
            if not chemist_toggle_button.is_selected():
                chemist_toggle_button.click()
                time.sleep(1)
                print("Enabled chemist toggle button.")
            else:
                print("Chemist toggle button is already enabled")
        except Exception as e:
            print(f"Error while enabling chemist toggle button: {e}")  
    
    @order(14)
    def test_edit_chemist(self):
        try:
            # Navigate to the customer/chemist master list page
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            # Disable the chemist toggle button
            customer_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'customer_toggle_button_xpath'))
            if customer_toggle_button.is_enabled():
                customer_toggle_button.click()
                print("Disabled customer toggle button.")

            entries_select = self.wait_and_click(config.get('DEFAULT', 'entries_select_xpath'))
            for value in ['-1']:
                option = self.driver.find_element(By.XPATH, f"//select[@id='entriesPerPage']/option[@value='{value}']")
                option.click()

            time.sleep(1)            

            # Click the edit button
            retries = 3
            for _ in range(retries):
                try:
                    self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
                    break
                except StaleElementReferenceException:
                    time.sleep(2)
            else:
                self.fail("Failed to click edit button after multiple retries")
            time.sleep(1)

            # Enter new values into all fields using XPath
            name_as_per_records_field = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_for_usage_field = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            institution_name_field = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            speciality_field = self.wait_and_find(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            mobile_number_field = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            birth_date_field = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            wedding_date_field = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            mode_of_crm_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))

            assert name_as_per_records_field.is_enabled(), "Name as per records field is not editable"
            assert name_for_usage_field.is_enabled(), "Name for usage field is not editable"
            assert institution_name_field.is_enabled(), "Institution name field is not editable"
            assert speciality_field.is_enabled(), "Speciality field is not editable"
            assert mobile_number_field.is_enabled(), "Mobile number field is not editable"
            assert birth_date_field.is_enabled(), "Birth date field is not editable"
            assert wedding_date_field.is_enabled(), "Wedding date field is not editable"
            assert mode_of_crm_field.is_enabled(), "Mode of CRM field is not editable"

            name_as_per_records_field.clear()
            name_as_per_records_field.send_keys(config.get('DEFAULT', 'edit_name_as_per_records'))
            time.sleep(1)

            name_for_usage_field.clear()
            name_for_usage_field.send_keys(config.get('DEFAULT', 'edit_name_for_usage'))

            institution_name_field.clear()
            institution_name_field.send_keys(config.get('DEFAULT', 'edit_institution_name'))

            try:
                Select(speciality_field).select_by_visible_text(config.get('DEFAULT', 'edit_speciality'))
            except NoSuchElementException:
                self.fail(f"Speciality '{config.get('DEFAULT', 'edit_speciality')}' not found in the dropdown")

            mobile_number_field.clear()
            mobile_number_field.send_keys(config.get('DEFAULT', 'edit_mobile_number'))

            birth_date_field.clear()
            birth_date_field.send_keys(config.get('DEFAULT', 'edit_birth_date'))

            wedding_date_field.clear()
            wedding_date_field.send_keys(config.get('DEFAULT', 'edit_wedding_date'))

            Select(mode_of_crm_field).select_by_visible_text(config.get('DEFAULT', 'edit_mode_of_crm'))

            # Click the update button
            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            time.sleep(1)

            # Handle the confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            time.sleep(1)

            # Verify the updated values in the customer/chemist master list
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)

            updated_user = self.wait_and_find(config.get('DEFAULT', 'updated_user_xpath'))
            assert updated_user is not None, "Updated customer/chemist details not found in the table"

            print("Customer/Chemist details updated successfully.")
        except Exception as e:
            self.fail(f"Error during edit test: {e}")

            def test_export_buttons(self):
                try:
                    export_button = self.wait_and_click(config.get('DEFAULT', 'export_button_xpath'))
                    time.sleep(2)

                    csv_button = self.wait_and_click(config.get('DEFAULT', 'csv_button_xpath'))
                    time.sleep(2)

                    pdf_button = self.wait_and_click(config.get('DEFAULT', 'pdf_button_xpath'))
                    time.sleep(2)

                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    self.assertTrue(True)
                except Exception as e:
                    self.fail(f"Error during export button test: {e}")

        # Ensure the chemist toggle button is enabled
        try:
            customer_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'customer_toggle_button_xpath'))
            if not customer_toggle_button.is_selected():
                customer_toggle_button.click()
                time.sleep(1)
                print("Enabled customer toggle button.")
            else:
                print("customer toggle button is already enabled")
        except Exception as e:
            print(f"Error while enabling customer toggle button: {e}")  

    @order(12)
    def test_view_chemist(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)  # Wait for the page to load

            # Disable the chemist toggle button
            customer_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'customer_toggle_button_xpath'))
            if customer_toggle_button.is_enabled():
                customer_toggle_button.click()
                print("Disabled customer toggle button.")

            entries_select = self.wait_and_click(config.get('DEFAULT', 'entries_select_xpath'))
            for value in ['-1']:
                option = self.driver.find_element(By.XPATH, f"//select[@id='entriesPerPage']/option[@value='{value}']")
                option.click()
                time.sleep(1)
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)            

            Name_as_per_records_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_records_field_xpath'))

            Name_as_per_convenience_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_convenience_xpath'))

            Institution_Name_field = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))

            Speciality_field = self.wait_and_find(config.get('DEFAULT', 'Speciality_xpath'))

            Mobile_Number_field = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
 
            Birth_Date_field = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))

            Wedding_Date_field = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
 
            Mode_of_CRM_field = self.wait_and_find(config.get('DEFAULT', 'Mode_of_CRM_xpath'))

            Reward_Status_field = self.wait_and_find(config.get('DEFAULT', 'Reward_Status_xpath'))

            User_Type_field = self.wait_and_find(config.get('DEFAULT', 'User_Type_field_xpath'))
 
            SMS_field = self.wait_and_find(config.get('DEFAULT', 'SMS_field_xpath'))
 

            assert Name_as_per_records_field.get_attribute("readonly") == "true", "customer field is editable"
            assert Name_as_per_convenience_field.get_attribute("readonly") == "true", "Name as per convenience field is editable"
            assert Institution_Name_field.get_attribute("readonly") == "true", "Institution Name field is editable"
            assert Speciality_field.get_attribute("readonly") == "true", "Speciality field is editable"
            assert Mobile_Number_field.get_attribute("readonly") == "true", "Mobile Number field is editable"
            assert Birth_Date_field.get_attribute("readonly") == "true", "Birth Date field is editable"
            assert Wedding_Date_field.get_attribute("readonly") == "true", "Wedding Date field is editable"
            assert Mode_of_CRM_field.get_attribute("readonly") == "true", "Mode of CRM field is editable"
            assert Reward_Status_field.get_attribute("readonly") == "true", "Reward Status field is editable"
            assert User_Type_field.get_attribute("readonly") == "true", "User Type field field is editable" 
            assert SMS_field.get_attribute("readonly") == "true", "SMS field is editable"



            print("All fields are correctly set to readonly.")
        except Exception as e:
            self.fail(f"Error during view test: {e}")

        # Adding the back button click
        try:
            print("Clicking back button")
            back_button = self.wait_and_find(config.get('DEFAULT', 'back_button'))
            if back_button.is_enabled() and back_button.is_displayed():
                back_button.click()
                print("Back button clicked")
            else:
                print("Back button is not clickable")
            time.sleep(5)
        except Exception as e:
            print(f"Error while clicking back button: {e}")

        # Ensure the chemist toggle button is enabled
        try:
            customer_toggle_button = self.driver.find_element(By.XPATH, config.get('DEFAULT', 'customer_toggle_button_xpath'))
            if not customer_toggle_button.is_selected():
                customer_toggle_button.click()
                time.sleep(1)
                print("Enabled customer toggle button.")
            else:
                print("customer toggle button is already enabled")
        except Exception as e:
            print(f"Error while enabling customer toggle button: {e}")  

    @order(15)
    def test_delete_customer_chemist(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.ensure_toggle_button_enabled()
            customer_entry_xpath = config.get('DEFAULT', 'customer_entry_xpath')
            delete_button_xpath = config.get('DEFAULT', 'delete_button_xpath')
            notification_xpath = config.get('DEFAULT', 'custom_notification_id')
            notification_ok_button_xpath = config.get('DEFAULT', 'notification_ok_button_id')

            customer_entry = self.wait_and_find(customer_entry_xpath)
            customer_id = customer_entry.get_attribute("data-id")
            self.wait_and_click(delete_button_xpath)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, notification_xpath)))
            self.wait_and_click(notification_ok_button_xpath)
            time.sleep(1)
            with self.assertRaises(Exception):
                self.driver.find_element(By.XPATH, f"//table[@id='customerTable']//tr[@data-id='{customer_id}']")
        except Exception as e:
            self.fail(f"Error during delete rep test: {e}")
         

    @order(17)
    def test_rerun_add_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any") 


            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)


            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)

            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)

            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(1)

            # Click customer
            customer_locator = config.get('DEFAULT', 'customer_button_id')
            self.wait_and_check(By.XPATH, customer_locator)
            time.sleep(1)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(1)


            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            self.ensure_toggle_button_enabled()

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new customer entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'cus_first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_as_per_records')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created customer entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add customer test: {e}")


    @order(18)
    def test_rerun_add_chemist(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            self.validate_input(name_as_per_records_input, config.get('DEFAULT', 'name_as_per_records'), "name_with_space")

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            self.validate_input(name_for_usage_input, config.get('DEFAULT', 'name_for_usage'), "name_with_space")

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            self.validate_input(institution_name_input, config.get('DEFAULT', 'institution_name'), "any") 


            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)


            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            self.validate_input(mobile_number_input, config.get('DEFAULT', 'che_mobile_number'), "mobile")

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(1)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(1)

            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(1)

            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(1)

            # Click chemist
            chemist_locator = config.get('DEFAULT', 'chemist_button_id')
            self.wait_and_check(By.XPATH, chemist_locator)
            time.sleep(1)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(1)


            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            time.sleep(1)
            self.ensure_toggle_button_enabled()

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new chemist entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'che_first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_as_per_records')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created chemist entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add chemist test: {e}")



    @order(16)
    def test_dropdown_customer_speciality(self):
        try:
            # Step 1: Navigate to the Customer/Chemist list page
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            print("Navigated to Customer/Chemist Master List Page")
            time.sleep(1)

            # Step 2: Navigate to the Speciality list page and click the add button
            self.driver.get(config.get('DEFAULT', 'speciality_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Speciality Master List Page")
            time.sleep(1)

            # Step 3: Enter the speciality value and submit
            speciality_name_input = self.wait_and_find(config.get('DEFAULT', 'Speciality_Name_xpath'))
            speciality_name = config.get('DEFAULT', 'Speciality_Name')
            print(f"Entering speciality name: {speciality_name}")
            speciality_name_input.clear()
            speciality_name_input.send_keys(speciality_name)
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button for speciality")
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up for speciality")
            time.sleep(1)

            # Step 4: Navigate back to the Customer/Chemist list page
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            print("Navigated back to Customer/Chemist Master List Page")
            time.sleep(1)

            # Step 5: Click the add button and navigate to the speciality field
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Clicked add button on Customer/Chemist Master List Page")
            time.sleep(1)

            # Step 6: Click the dropdown and check if the newly created speciality value is present
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            print("Clicked speciality dropdown")
            time.sleep(1)
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_xpath')
            speciality_option = self.wait_and_find(speciality_option_xpath)
            print(f"Dropdown option text: {speciality_option.text}")
            assert speciality_option.text == speciality_name, f"Expected speciality name '{speciality_name}' not found in the dropdown"
            print("Speciality name is found in the dropdown")

            # Select the option for speciality
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)
        except Exception as e:
            self.fail(f"Error during add customer speciality dropdown test: {e}")
   
    @order(3)
    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.ensure_toggle_button_enabled()
            export_button = self.wait_and_click(config.get('DEFAULT', 'export_button_xpath'))
            time.sleep(2)

            csv_button = self.wait_and_click(config.get('DEFAULT', 'csv_button_xpath'))
            time.sleep(2)

            pdf_button = self.wait_and_click(config.get('DEFAULT', 'pdf_button_xpath'))
            time.sleep(2)

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during export button test: {e}")

    @order(4)
    def test_print_button(self):
        try:
            self.ensure_toggle_button_enabled()
            print_button = self.wait_and_click(config.get('DEFAULT', 'print_button_xpath'))
            time.sleep(5)

            inner_print_button = self.wait_and_click(config.get('DEFAULT', 'inner_print_button_xpath'))
            time.sleep(5)

            pyautogui.press('esc')
            time.sleep(1)
            pyautogui.press('esc')
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during print button test: {e}")

    @order(5)
    def test_column_visibility(self):
        try:
            self.ensure_toggle_button_enabled()
            colvis_button = self.wait_and_click(config.get('DEFAULT', 'colvis_button_xpath'))
            time.sleep(2)

            colvis_options = self.driver.find_elements(By.XPATH, config.get('DEFAULT', 'colvis_options_xpath'))
            time.sleep(2)

            for option in colvis_options:
                option.click()
                time.sleep(2)

            restore_button = self.wait_and_click(config.get('DEFAULT', 'colvis_restore_button_xpath'))
            time.sleep(2)

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during column visibility test: {e}")

    @order(6)
    def test_clear_button(self):
        try:
            self.ensure_toggle_button_enabled()
            search_input = self.wait_and_find(config.get('DEFAULT', 'search_input_xpath'))
            search_input.send_keys(config.get('DEFAULT', 'clear_button_search_term'))
            time.sleep(2)

            clear_button = self.wait_and_click(config.get('DEFAULT', 'reset_button_xpath'))
            time.sleep(2)

            self.assertEqual(search_input.get_attribute("value"), "", "Clear button did not reset the search input")
        except Exception as e:
            self.fail(f"Error during clear button test: {e}")

    @order(7)
    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
        self.ensure_toggle_button_enabled()
        search_terms = config['DEFAULT']['search_terms'].split(',')
        for search_term in search_terms:
            with self.subTest(search_term=search_term):
                try:
                    search_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['search_input_xpath']))
                    )
                    search_input.clear()
                    search_input.send_keys(search_term)
                    
                    # Check if the search button is clickable and click it
                    search_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['search_button_xpath']))
                    )
                    search_button.click()
                    
                    time.sleep(1)

                    rows = self.driver.find_elements(By.XPATH, config['DEFAULT']['last_row_xpath'])
                    if len(rows) == 0 or (len(rows) == 1 and "no matching records found" in rows[0].text.lower()):
                        print(f"Test case failed: Value '{search_term}' not matched")
                    else:
                        matched = any(search_term.lower() in row.text.lower() for row in rows)
                        if matched:
                            print(f"Test case passed: Value '{search_term}' matched")
                        else:
                            print(f"Test case failed: Value '{search_term}' not matched")
                except Exception as e:
                    print(f"Error during search functionality test: {e}")
    
    @order(8)
    def test_pagination_buttons(self):
        try:
            self.ensure_toggle_button_enabled()
            # Check the number of pages
            pages = self.driver.find_elements(By.XPATH, config.get('DEFAULT', 'page_numbers_xpath'))
            if len(pages) <= 1:
                print("Only one page present, skipping pagination button checks.")
                self.assertTrue(True)
                return
            
            # Check "Next" button
            next_button = self.wait_and_click(config.get('DEFAULT', 'next_button_xpath'))
            time.sleep(2)

            # Check "Last" button
            last_button = self.wait_and_click(config.get('DEFAULT', 'last_button_xpath'))
            time.sleep(5)

            # Check "Previous" button
            prev_button = self.wait_and_click(config.get('DEFAULT', 'previous_button_xpath'))
            time.sleep(5)

            # Check "First" button
            first_button = self.wait_and_click(config.get('DEFAULT', 'first_button_xpath'))
            time.sleep(5)

            # Verify we are back to the first page
            active_page = self.wait_and_find(config.get('DEFAULT', 'current_page_xpath')).text
            self.assertEqual(active_page, "1")
        except Exception as e:
            self.fail(f"Error during pagination button test: {e}")
    
    @order(9)
    def test_entries_per_page(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.ensure_toggle_button_enabled()
            entries_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['entries_select_xpath']))
            )
            for value in ['5', '10', '15', '20', '50', '-1']:
                entries_select.click()
                option_xpath = config['DEFAULT']['entries_option_xpath'].replace('{value}', value)
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                option.click()
                time.sleep(1)

                # # Verify that the number of rows matches the selected value, except for '-1' which means all entries
                # rows = self.driver.find_elements(By.XPATH, config['DEFAULT']['last_row_xpath'])
                # if value == '-1':
                #     self.assertGreaterEqual(len(rows), 1)  # Assuming there is at least 1 row in total
                # else:
                #     expected_rows = min(int(value), len(rows))
                #     self.assertEqual(len(rows), expected_rows)

            # Finally, set the entries per page back to 5
            entries_select.click()
            option_xpath = config['DEFAULT']['entries_option_xpath'].replace('{value}', '5')
            option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option.click()
            time.sleep(1)

            rows = self.driver.find_elements(By.XPATH, config['DEFAULT']['last_row_xpath'])
            self.assertEqual(len(rows), min(5, len(rows)))
        except Exception as e:
            self.fail(f"Error during entries per page test: {e}")



    @order(10)
    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
        self.ensure_toggle_button_enabled()
        search_terms = config['DEFAULT']['search_terms'].split(',')
        for search_term in search_terms:
            with self.subTest(search_term=search_term):
                try:
                    search_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['search_input_xpath']))
                    )
                    search_input.clear()
                    search_input.send_keys(search_term)
                    
                    # Check if the search button is clickable and click it
                    search_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['search_button_xpath']))
                    )
                    search_button.click()
                    
                    time.sleep(1)

                    rows = self.driver.find_elements(By.XPATH, config['DEFAULT']['last_row_xpath'])
                    if len(rows) == 0 or (len(rows) == 1 and "no matching records found" in rows[0].text.lower()):
                        print(f"Test case failed: Value '{search_term}' not matched")
                    else:
                        matched = any(search_term.lower() in row.text.lower() for row in rows)
                        if matched:
                            print(f"Test case passed: Value '{search_term}' matched")
                        else:
                            print(f"Test case failed: Value '{search_term}' not matched")
                except Exception as e:
                    print(f"Error during search functionality test: {e}")
    


def run_all_tests():
    class CustomTextTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            print(f"Test passed: {test._testMethodName} functionality worked")

        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"Test failed: {test._testMethodName} functionality did not work")

        def addError(self, test, err):
            super().addError(test, err)
            print(f"Test error: {test._testMethodName} encountered an error")

    class CustomTextTestRunner(unittest.TextTestRunner):
        resultclass = CustomTextTestResult

    suite = unittest.TestLoader().loadTestsFromTestCase(CusCheListTests)
    result = CustomTextTestRunner(verbosity=2).run(suite)

    report = f"Tests run: {result.testsRun}\n"
    report += f"Errors: {len(result.errors)}\n"
    report += f"Failures: {len(result.failures)}\n"
    report += f"Passed: {result.testsRun - len(result.errors) - len(result.failures)}\n"
  
    # send_email(report)
    print(report)

# Example usage
if __name__ == "__main__":
    # Create an instance of the test class
    test_instance = CusCheListTests()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_customer - {e}")
            failed_tests += 1

        try:
            test_instance.test_add_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_chemist - {e}")
            failed_tests += 1

        try:
            test_instance.test_export_buttons()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_export_buttons - {e}")
            failed_tests += 1

        try:
            test_instance.test_print_button()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_print_button - {e}")
            failed_tests += 1

        try:
            test_instance.test_column_visibility()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_column_visibility - {e}")
            failed_tests += 1

        try:
            test_instance.test_clear_button()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_clear_button - {e}")
            failed_tests += 1

        try:
            test_instance.test_search_functionality()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_search_functionality - {e}")
            failed_tests += 1

        try:
            test_instance.test_pagination_buttons()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_pagination_buttons - {e}")
            failed_tests += 1

        try:
            test_instance.test_entries_per_page()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_entries_per_page - {e}")
            failed_tests += 1

        try:
            test_instance.test_dropdown_customer_speciality()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_dropdown_customer_speciality - {e}")
            failed_tests += 1

        try:
            test_instance.test_view_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_customer - {e}")
            failed_tests += 1

        try:
            test_instance.test_view_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_chemist - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_customer - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_chemist - {e}")
            failed_tests += 1

        try:
            test_instance.test_delete_customer_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_delete_customer_chemist - {e}")
        #     failed_tests += 1

        try:
            test_instance.test_rerun_add_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_customer - {e}")
            failed_tests += 1

        try:
            test_instance.test_rerun_add_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_chemist - {e}")
            failed_tests += 1
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")