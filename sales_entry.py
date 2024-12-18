import time
from selenium.webdriver.support.ui import Select
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
from selenium.common.exceptions import TimeoutException
import configparser
import re
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import random
from datetime import datetime, timedelta
from test_utils import order

# Read properties from config file
config = configparser.ConfigParser()
config.read('sales_entry.ini')

class sales_entry(unittest.TestCase):

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


    @classmethod
    @order(1)
    def login_as_admin(cls):
        cls.driver.get(config.get('DEFAULT', 'url'))
        username_input = cls.wait_and_find("//input[@id='username']")
        password_input = cls.wait_and_find("//input[@id='password']")
        username_input.send_keys(config.get('DEFAULT', 'username'))
        password_input.send_keys(config.get('DEFAULT', 'password'))
        cls.wait_and_click("//button[@type='submit' and contains(text(), 'Login')]")
        time.sleep(3)  # Wait for login to complete

    @classmethod
    def wait_and_check(cls, by, value, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((by, value)))
        element.click()
        return element

    @classmethod
    def wait_and_click(cls, xpath, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element

    @classmethod
    def wait_and_find(cls, xpath, timeout=10):
        return WebDriverWait(cls.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))

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

    def generate_random_start_date(self):
        start_date = datetime(1990, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        random_date = random_date.replace(day=1)
        return random_date.strftime("%d/%m/%Y")


    @order(2)
    def test_add_total_sales_entry(self):
        try:
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
            print("Navigated to sales entry List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_name_dropdown_xpath'))
            time.sleep(3)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(3)

            # Click the dropdown box for total amount 
            total_amount_input = self.wait_and_find(config.get('DEFAULT', 'total_amount_xpath'))
            print("Waiting for total amount input")
            time.sleep(3)
            total_amount_input.clear()  # Clear any existing value
            total_amount_input.send_keys(config.get('DEFAULT', 'total_amount'))
            time.sleep(3)

            # Click the dropdown box for total_sales_entry
            total_sales_entry_input = self.wait_and_find(config.get('DEFAULT', 'total_sales_entry_xpath'))
            print("Waiting for total sales entry input")
            time.sleep(3)
            total_sales_entry_input.clear()  # Clear any existing value
            total_sales_entry_input.send_keys(config.get('DEFAULT', 'value'))
            time.sleep(3)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

        # Check if navigated to the business set config page or sales entry list page
            current_url = self.driver.current_url
            if "business_set_configuration_masterlist.php" in current_url:
                print("Navigated to Business Set Customer Master List Page")
                time.sleep(3)

                # Verify the current sales value for each customer in the business set customer master list
                customer_ids = config.get('DEFAULT', 'customer_ids').split(',')
                for index, customer_id in enumerate(customer_ids):
                    current_sales_value_xpath = config.get('DEFAULT', 'current_sales_value_xpath_template').format(customer_id=customer_id)
                    print(f"Looking for current sales value element with XPath: {current_sales_value_xpath}")
                    try:
                        current_sales_value_element = self.wait_and_find(current_sales_value_xpath)
                        current_sales_value = float(current_sales_value_element.text.strip())
                        print(f"Current sales value for customer {customer_id}: {current_sales_value}")

                        target_value_xpath = f"//tr[@data-customer-id='{customer_id}']/td[@class='target_value']"
                        print(f"Looking for target value element with XPath: {target_value_xpath}")
                        target_value_element = self.wait_and_find(target_value_xpath)
                        target_value = float(target_value_element.text.strip())
                        print(f"Target value for customer {customer_id}: {target_value}")

                        # Check if the current sales value is greater than or equal to the target value
                        assert current_sales_value >= target_value, f"Current sales value '{current_sales_value}' for customer '{customer_id}' is less than target value '{target_value}'"
                        print(f"Current sales value for customer {customer_id} is greater than or equal to target value.")
                    except TimeoutException:
                        print(f"TimeoutException: Element with XPath {current_sales_value_xpath} not found.")
                        self.fail(f"Error during add product test: Element with XPath {current_sales_value_xpath} not found.")
            else:
                print("Navigated to Sales Entry List Page")
                time.sleep(3)

                # Verify the new entry in the first row
                first_row = self.wait_and_find(config.get('DEFAULT', 'total_first_row_xpath'))
                first_row_text = first_row.text
                print(f"First row text: {first_row_text}")

                # Verify the expected values in the first row
                expected_values = [
                    config.get('DEFAULT', 'total_billing_name'),
                ]

                for value in expected_values:
                    assert value in first_row_text, f"Expected value '{value}' not found in the first row"

                print("Newly created product entry verified successfully.")



        except Exception as e:
            self.fail(f"Error during add product test: {e}")
  
  
  
    @order(3)    
    def test_add_product_based_sales_entry(self):
        try:
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
            print("Navigated to sales entry List Page")
            
        #bill name and stockist name
            self.driver.get(config.get('DEFAULT', 'billName_and_stockist_config_url'))
            print("Navigated to bill name and stockist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

          

            # Select billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_dropdown_name_xpath'))
            time.sleep(3)
            billing_name_option_xpath = config.get('DEFAULT', 'product_and_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(3)

            # Select stockist name
            self.wait_and_click(config.get('DEFAULT', 'stockist_dropdown_name_xpath'))
            time.sleep(3)
            stockist_option_xpath = config.get('DEFAULT', 'stockist_option_value')
            self.wait_and_click(stockist_option_xpath)
            time.sleep(3)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(3)


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")
    

            #add bill customer and product master
            self.driver.get(config.get('DEFAULT', 'bill_customer_and_product_master_url'))
       
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customer_dropdown_name_xpath'))
            time.sleep(3)
            customer_name_option_xpath = config.get('DEFAULT', 'customer_name_option_value')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(3)

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'cus_billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'cus_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(3)

    


            # Enter 100% value in the global percentage input
            global_percentage_input = self.wait_and_find(config.get('DEFAULT', 'global_percentage_input_xpath'))
            global_percentage_input.clear()
            global_percentage_input.send_keys(config.get('DEFAULT', 'global_percentage_value'))
            print("Entered 100% in global percentage input")
            time.sleep(3)

            # Click the checkboxes for the given XPaths
            checkbox_xpaths = [
                config.get('DEFAULT', 'checkbox_xpath1'),
                config.get('DEFAULT', 'checkbox_xpath2'),
                config.get('DEFAULT', 'checkbox_xpath3'),
            ]
            
            for xpath in checkbox_xpaths:
                checkbox = self.wait_and_find(xpath)
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(1)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

           
            # redirect to sales entry
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_name_dropdown_xpath'))
            time.sleep(3)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'product_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(3)

            # Click the dropdown box for total amount 
            total_amount_input = self.wait_and_find(config.get('DEFAULT', 'product_total_amount_xpath'))
            print("Waiting for total amount input")
            time.sleep(3)
            total_amount_input.clear()  # Clear any existing value
            total_amount_input.send_keys(config.get('DEFAULT', 'p_total_amount'))
            time.sleep(3)

            # Set sales values
            sales_values = {
                config.get('DEFAULT', 'product_based_sales_entry_xpath1'): config.get('DEFAULT', 'p_value1'),
                config.get('DEFAULT', 'product_based_sales_entry_xpath2'): config.get('DEFAULT', 'p_value2'),
                config.get('DEFAULT', 'product_based_sales_entry_xpath3'): config.get('DEFAULT', 'p_value3'),

            }

            for xpath, value in sales_values.items():
                input_element = self.wait_and_find(xpath)
                input_element.clear()
                input_element.send_keys(str(value))
                time.sleep(1)  # Add a small delay if necessary

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

             # Check if navigated to the business set customer master list page
            if self.is_element_present(config.get('DEFAULT', 'current_sales_value_xpath')):
                self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
                print("Navigated to Business Set Customer Master List Page")
                time.sleep(3)

                # Verify the current sales value in the business set customer master list
                current_sales_value_element = self.wait_and_find(config.get('DEFAULT', 'current_sales_value_xpath'))
                current_sales_value = float(current_sales_value_element.text.strip())
                print(f"Current sales value: {current_sales_value}")

                # Verify the target value in the business set customer master list
                target_value_element = self.wait_and_find(config.get('DEFAULT', 'target_value_xpath'))
                target_value = float(target_value_element.text.strip())
                print(f"Target value: {target_value}")

                # Check if the current sales value is greater than or equal to the target value
                assert current_sales_value >= target_value, f"Current sales value '{current_sales_value}' is less than target value '{target_value}'"
                print("Current sales value is greater than or equal to target value.")

            elif self.driver.current_url == config.get('DEFAULT', 'sales_entry_url'):
                print("Navigated to Sales Entry List Page")
                billing_name_element = self.wait_and_find(config.get('DEFAULT', 'p_billing_name_xpath'))
                billing_name = billing_name_element.text.strip()
                expected_billing_name = config.get('DEFAULT', 'p_billing_name')
                assert billing_name == expected_billing_name, f"Expected billing name '{expected_billing_name}', but got '{billing_name}'"
                print(f"Billing name: {billing_name}")
            else:
                self.fail("Did not navigate to the expected page")

        except Exception as e:
            self.fail(f"Error during add product test: {e}")


    def is_element_present(self, xpath, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            return False





    def set_sales_values(self):
        # Directly assign the values from the configuration file
        sales_values = {
            'product_based_sales_entry_xpath1': config.get('DEFAULT', 'value1'),
            'product_based_sales_entry_xpath2': config.get('DEFAULT', 'value2'),
            'product_based_sales_entry_xpath3': config.get('DEFAULT', 'value3')

        }

        for key, value in sales_values.items():
            xpath = config.get('DEFAULT', key)
            input_element = self.wait_and_find(xpath)
            input_element.clear()
            input_element.send_keys(str(value))
            time.sleep(1)  # Add a small delay if necessary



    @order(4)
    def test_check_multiple_customer(self):
        try:

            #add customer 1------------------->
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_customer_add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_as_per_records_input.send_keys(config.get('DEFAULT', 'name_as_per_records1'))

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            name_for_usage_input.send_keys(config.get('DEFAULT', 'name_for_usage'))

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            institution_name_input.send_keys(config.get('DEFAULT', 'institution_name'))

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'mobile_number1'))

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




            #add customer 2------------------>
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_customer_add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_as_per_records_input.send_keys(config.get('DEFAULT', 'name_as_per_records2'))

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            name_for_usage_input.send_keys(config.get('DEFAULT', 'name_for_usage'))

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            institution_name_input.send_keys(config.get('DEFAULT', 'institution_name'))

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'mobile_number2'))

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


            #add billing name ----------------->
            self.driver.get(config.get('DEFAULT', 'billing_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_bill_add_button_xpath'))
            print("Navigated to billing Master List Page")

            billing_name_input = self.wait_and_find(config.get('DEFAULT', 'billing_name_xpath'))
            billing_name_input.send_keys(config.get('DEFAULT', 'm_billing_name'))

            contact_person_name_input = self.wait_and_find(config.get('DEFAULT', 'contact_person_name_xpath'))
            contact_person_name_input.send_keys(config.get('DEFAULT', 'contact_person_name'))

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'mobile_number'))

            email_id_input = self.wait_and_find(config.get('DEFAULT', 'email_id_xpath'))
            email_id_input.send_keys(config.get('DEFAULT', 'email_id'))

            Address1_input = self.wait_and_find(config.get('DEFAULT', 'address_1_xpath'))
            Address1_input.send_keys(config.get('DEFAULT', 'Address1'))

            Address2_input = self.wait_and_find(config.get('DEFAULT', 'address_2_xpath'))
            Address2_input.send_keys(config.get('DEFAULT', 'Address2'))

            City_input = self.wait_and_find(config.get('DEFAULT', 'City_xpath'))
            City_input.send_keys(config.get('DEFAULT', 'City'))

            State_input = self.wait_and_find(config.get('DEFAULT', 'State_xpath'))
            State_input.send_keys(config.get('DEFAULT', 'State'))

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")









            #business set config customer1 ------------>

            self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'business_set_config_add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customers_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customer_name_option_values1')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Select mode of business (OBV)
            self.wait_and_click(config.get('DEFAULT', 'mode_of_business_dropdown_xpath'))
            time.sleep(1)
            mode_of_business_option_xpath = config.get('DEFAULT', 'mode_of_business_option_value_obv')
            self.wait_and_click(mode_of_business_option_xpath)
            time.sleep(1)

            # Enter reward recommendation
            self.wait_and_click(config.get('DEFAULT', 'reward_recommendation_dropdown_xpath'))
            reward_recommendation_option_xpath = config.get('DEFAULT', 'reward_recommendation_option_value')
            self.wait_and_click(reward_recommendation_option_xpath)
            time.sleep(1)

            target_value_input = self.wait_and_find(config.get('DEFAULT', 'target_values_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            target_value_input.clear()  # Clear any existing value
            target_value_input.send_keys(config.get('DEFAULT', 'target_value'))


            # Enter business set start date
            business_set_start_date_input = self.wait_and_find(config.get('DEFAULT', 'add_business_set_start_date_xpath'))
            print("Waiting for business set start date input")
            time.sleep(1)
            business_set_start_date_input.clear()
            random_start_date = self.generate_random_start_date()
            business_set_start_date_input.send_keys(random_start_date)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")







            #business set config customer2 ---------------->

            self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'business_set_config_add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customers_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customer_name_option_values2')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Select mode of business (OBV)
            self.wait_and_click(config.get('DEFAULT', 'mode_of_business_dropdown_xpath'))
            time.sleep(1)
            mode_of_business_option_xpath = config.get('DEFAULT', 'mode_of_business_option_value_obv')
            self.wait_and_click(mode_of_business_option_xpath)
            time.sleep(1)

            # Enter reward recommendation
            self.wait_and_click(config.get('DEFAULT', 'reward_recommendation_dropdown_xpath'))
            reward_recommendation_option_xpath = config.get('DEFAULT', 'reward_recommendation_option_value')
            self.wait_and_click(reward_recommendation_option_xpath)
            time.sleep(1)

            target_value_input = self.wait_and_find(config.get('DEFAULT', 'target_values_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            target_value_input.clear()  # Clear any existing value
            target_value_input.send_keys(config.get('DEFAULT', 'target_value'))


            # Enter business set start date
            business_set_start_date_input = self.wait_and_find(config.get('DEFAULT', 'add_business_set_start_date_xpath'))
            print("Waiting for business set start date input")
            time.sleep(1)
            business_set_start_date_input.clear()
            random_start_date = self.generate_random_start_date()
            business_set_start_date_input.send_keys(random_start_date)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")






            #customer_config_master1 -------------->
            self.driver.get(config.get('DEFAULT', 'customer_config_master_url'))
            print("Navigated to  customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customer_dropdown_name_xpaths'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customers_name_option_value1')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Supplied_Item_Credit_Period_input = self.wait_and_find(config.get('DEFAULT', 'Supplied_Item_Credit_Period_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            Supplied_Item_Credit_Period_input.clear()  # Clear any existing value
            Supplied_Item_Credit_Period_input.send_keys(config.get('DEFAULT', 'Supplied_Item_Credit_Period'))


            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)
        
            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")




            #customer_config_master2 ----------->
            self.driver.get(config.get('DEFAULT', 'customer_config_master_url'))
            print("Navigated to  customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customer_dropdown_name_xpaths'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customers_name_option_value2')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Supplied_Item_Credit_Period_input = self.wait_and_find(config.get('DEFAULT', 'Supplied_Item_Credit_Period_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            Supplied_Item_Credit_Period_input.clear()  # Clear any existing value
            Supplied_Item_Credit_Period_input.send_keys(config.get('DEFAULT', 'Supplied_Item_Credit_Period'))


            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)
        
            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")




            #billing and stockist----------->
        #bill name and stockist name
            self.driver.get(config.get('DEFAULT', 'billName_and_stockist_config_url'))
            print("Navigated to bill name and stockist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

        

            # Select billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_dropdown_name_xpath'))
            time.sleep(1)
            billing_name_option_xpath = config.get('DEFAULT', 'multiple_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

            # Select stockist name
            self.wait_and_click(config.get('DEFAULT', 'stockist_dropdown_name_xpath'))
            time.sleep(1)
            stockist_option_xpath = config.get('DEFAULT', 'stockist_option_value')
            self.wait_and_click(stockist_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")






            # bill_customer_product_config1----------->
            # add bill customer and product master
            self.driver.get(config.get('DEFAULT', 'bill_customer_and_product_master_url'))
       
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_add_button_xpath'))





            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customer_name_option_value1')
            customer_name_element = self.wait_and_find(customer_name_option_xpath)
            customer_name = customer_name_element.text

            # Extract alphabets only from the customer name
            alphabets = ''.join(re.findall("[A-Za-z]", customer_name))

            # Extract alphabets only from the option value
            option_value_text = self.wait_and_find(customer_name_option_xpath).text
            option_value_alphabets = ''.join(re.findall("[A-Za-z]", option_value_text))

            # Check if the extracted alphabets match and click the option if they do
            if alphabets == option_value_alphabets:
                self.wait_and_click(customer_name_option_xpath)
                time.sleep(1)
            else:
                self.fail(f"Customer name '{customer_name}' does not match the expected option value.")

            # Print the extracted alphabets (for debugging purposes)
            print(f"Customer Name Alphabets: {alphabets}")
            print(f"Option Value Alphabets: {option_value_alphabets}")

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'cus_billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'mul_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

    


            # Enter 100% value in the global percentage input
            global_percentage_input = self.wait_and_find(config.get('DEFAULT', 'global_percentage_input_xpath'))
            global_percentage_input.clear()
            global_percentage_input.send_keys(config.get('DEFAULT', 'multi_global_percentage_value'))
            print("Entered 100% in global percentage input")
            time.sleep(1)

            # Click the checkboxes for the given XPaths
            checkbox_xpaths = [
                config.get('DEFAULT', 'checkbox_xpath1'),
                config.get('DEFAULT', 'checkbox_xpath2')
               
            ]
            
            for xpath in checkbox_xpaths:
                checkbox = self.wait_and_find(xpath)
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(1)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")






            #bill_customer_product_config2--------->
            #add bill customer and product master
            self.driver.get(config.get('DEFAULT', 'bill_customer_and_product_master_url'))
       
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'customer_name_option_value2')
            customer_name_element = self.wait_and_find(customer_name_option_xpath)
            customer_name = customer_name_element.text

            # Extract alphabets only from the customer name
            alphabets = ''.join(re.findall("[A-Za-z]", customer_name))

            # Extract alphabets only from the option value
            option_value_text = self.wait_and_find(customer_name_option_xpath).text
            option_value_alphabets = ''.join(re.findall("[A-Za-z]", option_value_text))

            # Check if the extracted alphabets match and click the option if they do
            if alphabets == option_value_alphabets:
                self.wait_and_click(customer_name_option_xpath)
                time.sleep(1)
            else:
                self.fail(f"Customer name '{customer_name}' does not match the expected option value.")

            # Print the extracted alphabets (for debugging purposes)
            print(f"Customer Name Alphabets: {alphabets}")
            print(f"Option Value Alphabets: {option_value_alphabets}")

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'cus_billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'mul_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

    


            # Enter 100% value in the global percentage input
            global_percentage_input = self.wait_and_find(config.get('DEFAULT', 'global_percentage_input_xpath'))
            global_percentage_input.clear()
            global_percentage_input.send_keys(config.get('DEFAULT', 'multi_global_percentage_value'))
            print("Entered 100% in global percentage input")
            time.sleep(1)

            # Click the checkboxes for the given XPaths
            checkbox_xpaths = [
                config.get('DEFAULT', 'checkbox_xpath3')
               
               
            ]
            
            for xpath in checkbox_xpaths:
                checkbox = self.wait_and_find(xpath)
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(1)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")



            #sales_entry ----------->
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
            print("Navigated to sales entry List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'multi_customer_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for total amount 
            total_amount_input = self.wait_and_find(config.get('DEFAULT', 'total_amount_xpath'))
            print("Waiting for total amount input")
            time.sleep(1)
            total_amount_input.clear()  # Clear any existing value
            total_amount = config.get('DEFAULT', 'mul_total_amount')
            total_amount_input.send_keys(str(total_amount))
            time.sleep(1)

            # Set sales values dynamically based on total amount
            self.set_sales_values()

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            # Check if navigated to the business set config page or sales entry list page
            current_url = self.driver.current_url
            if "business_set_configuration_masterlist.php" in current_url:
                print("Navigated to Business Set Customer Master List Page")
                time.sleep(1)

                # Verify the current sales value for each customer in the business set customer master list
                customer_ids = config.get('DEFAULT', 'customer_ids').split(',')
                for index, customer_id in enumerate(customer_ids):
                    row_index = index + 1  # Adjust for 1-based index in XPath
                    current_sales_value_xpath = f"//table[@id='customerTable']/tbody/tr[{row_index}]/td[6]"
                    print(f"Looking for current sales value element with XPath: {current_sales_value_xpath}")
                    try:
                        current_sales_value_element = self.wait_and_find(current_sales_value_xpath)
                        current_sales_value = float(current_sales_value_element.text.strip())
                        print(f"Current sales value for customer {customer_id}: {current_sales_value}")

                        target_value_xpath = f"//table[@id='customerTable']/tbody/tr[{row_index}]/td[5]"
                        print(f"Looking for target value element with XPath: {target_value_xpath}")
                        target_value_element = self.wait_and_find(target_value_xpath)
                        target_value = float(target_value_element.text.strip())
                        print(f"Target value for customer {customer_id}: {target_value}")

                        # Check if the current sales value is greater than or equal to the target value
                        assert current_sales_value >= target_value, f"Current sales value '{current_sales_value}' for customer '{customer_id}' is less than target value '{target_value}'"
                        print(f"Current sales value for customer {customer_id} is greater than or equal to target value.")
                    except TimeoutException:
                        print(f"TimeoutException: Element with XPath {current_sales_value_xpath} not found.")
                        self.fail(f"Error during add product test: Element with XPath {current_sales_value_xpath} not found.")
            else:
                print("Navigated to Sales Entry List Page")
                time.sleep(1)

                # Verify the hospital name in the list page
                first_row_xpath = config.get('DEFAULT', 'first_row_xpath')
                first_row_element = self.wait_and_find(first_row_xpath)
                first_row_text = first_row_element.text
                expected_hospital_name = config.get('DEFAULT', 'billing_name')
                assert expected_hospital_name in first_row_text, f"Expected hospital name '{expected_hospital_name}' not found in the first row"
                print(f"Hospital name '{expected_hospital_name}' found in the first row")

        except Exception as e:
            self.fail(f"Error during add product test: {e}")




    order(5)
    def test_check_chemist(self):
        try:

            #add chemist------------------>
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_customer_add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_as_per_records_input.send_keys(config.get('DEFAULT', 'che_name_as_per_records'))

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            name_for_usage_input.send_keys(config.get('DEFAULT', 'name_for_usage'))

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            institution_name_input.send_keys(config.get('DEFAULT', 'institution_name'))

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(3)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'che_mobile_number'))

            # Set random birth date
            birth_date_input = self.wait_and_find(config.get('DEFAULT', 'birth_date_xpath'))
            random_birth_date = self.generate_random_birth_date()
            birth_date_input.send_keys(random_birth_date)
            time.sleep(3)

            # Set random wedding date
            wedding_date_input = self.wait_and_find(config.get('DEFAULT', 'wedding_date_xpath'))
            random_wedding_date = self.generate_random_wedding_date()
            wedding_date_input.send_keys(random_wedding_date)
            time.sleep(3)

            # Click the dropdown box for mode_of_business
            self.wait_and_click(config.get('DEFAULT', 'mode_of_crm_dropdown_xpath'))
            # Select the option for mode_of_business
            mode_of_crm_option_value = config.get('DEFAULT', 'mode_of_crm_option_value')
            self.wait_and_click(mode_of_crm_option_value)
            time.sleep(3)

            # Click volunteer
            volunteer_locator = config.get('DEFAULT', 'volunteer_button_id')
            self.wait_and_check(By.XPATH, volunteer_locator)
            time.sleep(3)

            # Click customer
            customer_locator = config.get('DEFAULT', 'chemist_button_id')
            self.wait_and_check(By.XPATH, customer_locator)
            time.sleep(3)

            # Click SMS
            sms_locator = config.get('DEFAULT', 'sms_button_id')
            self.wait_and_check(By.XPATH, sms_locator)
            time.sleep(3)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")


            #add billing name ----------------->
            self.driver.get(config.get('DEFAULT', 'billing_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_bill_add_button_xpath'))
            print("Navigated to billing Master List Page")

            billing_name_input = self.wait_and_find(config.get('DEFAULT', 'billing_name_xpath'))
            billing_name_input.send_keys(config.get('DEFAULT', 'che_billing_name'))

            contact_person_name_input = self.wait_and_find(config.get('DEFAULT', 'contact_person_name_xpath'))
            contact_person_name_input.send_keys(config.get('DEFAULT', 'contact_person_name'))

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'c_mobile_number'))

            email_id_input = self.wait_and_find(config.get('DEFAULT', 'email_id_xpath'))
            email_id_input.send_keys(config.get('DEFAULT', 'email_id'))

            Address1_input = self.wait_and_find(config.get('DEFAULT', 'address_1_xpath'))
            Address1_input.send_keys(config.get('DEFAULT', 'Address1'))

            Address2_input = self.wait_and_find(config.get('DEFAULT', 'address_2_xpath'))
            Address2_input.send_keys(config.get('DEFAULT', 'Address2'))

            City_input = self.wait_and_find(config.get('DEFAULT', 'City_xpath'))
            City_input.send_keys(config.get('DEFAULT', 'City'))

            State_input = self.wait_and_find(config.get('DEFAULT', 'State_xpath'))
            State_input.send_keys(config.get('DEFAULT', 'State'))

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")








            #business set config chemist ---------------->

            self.driver.get(config.get('DEFAULT', 'business_set_config_chemist_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'business_set_config_add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customers_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'chemist_config_name_option_values')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Select mode of business (OBV)
            self.wait_and_click(config.get('DEFAULT', 'mode_of_business_dropdown_xpath'))
            time.sleep(1)
            mode_of_business_option_xpath = config.get('DEFAULT', 'mode_of_business_option_value_obv')
            self.wait_and_click(mode_of_business_option_xpath)
            time.sleep(1)

            # Enter reward recommendation
            self.wait_and_click(config.get('DEFAULT', 'reward_recommendation_dropdown_xpath'))
            reward_recommendation_option_xpath = config.get('DEFAULT', 'reward_recommendation_option_value')
            self.wait_and_click(reward_recommendation_option_xpath)
            time.sleep(1)

            target_value_input = self.wait_and_find(config.get('DEFAULT', 'target_values_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            target_value_input.clear()  # Clear any existing value
            target_value_input.send_keys(config.get('DEFAULT', 'target_value'))


            # Enter business set start date
            business_set_start_date_input = self.wait_and_find(config.get('DEFAULT', 'add_business_set_start_date_xpath'))
            print("Waiting for business set start date input")
            time.sleep(1)
            business_set_start_date_input.clear()
            random_start_date = self.generate_random_start_date()
            business_set_start_date_input.send_keys(random_start_date)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")





            #chemist_config_master ----------->
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            print("Navigated to  customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customer_dropdown_name_xpaths'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Supplied_Item_Credit_Period_input = self.wait_and_find(config.get('DEFAULT', 'Supplied_Item_Credit_Period_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            Supplied_Item_Credit_Period_input.clear()  # Clear any existing value
            Supplied_Item_Credit_Period_input.send_keys(config.get('DEFAULT', 'Supplied_Item_Credit_Period'))


            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)
        
            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")




            #billing and stockist----------->
        #bill name and stockist name
            self.driver.get(config.get('DEFAULT', 'billName_and_stockist_config_url'))
            print("Navigated to bill name and stockist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

        

            # Select billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_dropdown_name_xpath'))
            time.sleep(1)
            billing_name_option_xpath = config.get('DEFAULT', 'che_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

            # Select stockist name
            self.wait_and_click(config.get('DEFAULT', 'stockist_dropdown_name_xpath'))
            time.sleep(1)
            stockist_option_xpath = config.get('DEFAULT', 'stockist_option_value')
            self.wait_and_click(stockist_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")






            #bill_chemist_product_config--------->
           
            self.driver.get(config.get('DEFAULT', 'bill_chemist_and_product_master_url'))
       
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'bill_chemist_name_option_value')
            customer_name_element = self.wait_and_find(customer_name_option_xpath)
            customer_name = customer_name_element.text

            # Extract alphabets only from the customer name
            alphabets = ''.join(re.findall("[A-Za-z]", customer_name))

            # Extract alphabets only from the option value
            option_value_text = self.wait_and_find(customer_name_option_xpath).text
            option_value_alphabets = ''.join(re.findall("[A-Za-z]", option_value_text))

            # Check if the extracted alphabets match and click the option if they do
            if alphabets == option_value_alphabets:
                self.wait_and_click(customer_name_option_xpath)
                time.sleep(1)
            else:
                self.fail(f"Customer name '{customer_name}' does not match the expected option value.")

            # Print the extracted alphabets (for debugging purposes)
            print(f"Customer Name Alphabets: {alphabets}")
            print(f"Option Value Alphabets: {option_value_alphabets}")

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'cus_billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'chemist_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

    


            # Enter 100% value in the global percentage input
            global_percentage_input = self.wait_and_find(config.get('DEFAULT', 'global_percentage_input_xpath'))
            global_percentage_input.clear()
            global_percentage_input.send_keys(config.get('DEFAULT', 'che_global_percentage_value'))
            print("Entered 100% in global percentage input")
            time.sleep(1)

            # Click the checkboxes for the given XPaths
            checkbox_xpaths = [
                config.get('DEFAULT', 'checkbox_xpath2'),
                config.get('DEFAULT', 'checkbox_xpath3')
               
               
            ]
            
            for xpath in checkbox_xpaths:
                checkbox = self.wait_and_find(xpath)
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(1)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")



            #sales_entry ----------->
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
            print("Navigated to sales entry List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'chemist_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for total amount 
            total_amount_input = self.wait_and_find(config.get('DEFAULT', 'total_amount_xpath'))
            print("Waiting for total amount input")
            time.sleep(1)
            total_amount_input.clear()  # Clear any existing value
            total_amount = config.get('DEFAULT', 'mul_total_amount')
            total_amount_input.send_keys(str(total_amount))
            time.sleep(1)

            # Set sales values dynamically based on total amount
            self.chemist_set_sales_values()

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")
      

                                        
            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'che_back_button'))
            print("Clicked back button")
            time.sleep(1)
            
        


            # Verify the current sales value in the business set config chemist page
            current_sales_value_element = self.wait_and_find(config.get('DEFAULT', 'current_sales_value_xpath'))
            current_sales_value = current_sales_value_element.text.strip()
            print(f"Current sales value: {current_sales_value}")

            if current_sales_value:  # Check if current_sales_value is not empty
                # Verify the target value in the business set config chemist page
                target_value_element = self.wait_and_find(config.get('DEFAULT', 'target_value_xpath'))
                target_value = target_value_element.text.strip()
                print(f"Target value: {target_value}")

                # Check if the current sales value is greater than or equal to the target value
                assert current_sales_value >= target_value, f"Current sales value '{current_sales_value}' is less than target value '{target_value}'"
                print("Current sales value is greater than or equal to target value.")
            else:
                print("Navigated to Sales Entry List Page")
                time.sleep(1)

                # Verify the hospital name in the list page
                first_row_xpath = config.get('DEFAULT', 'check_chemist_first_row_xpath')
                first_row_element = self.wait_and_find(first_row_xpath)
                first_row_text = first_row_element.text
                expected_hospital_name = config.get('DEFAULT', 'chemist_billing_name')
                assert expected_hospital_name in first_row_text, f"Expected hospital name '{expected_hospital_name}' not found in the first row"
                print(f"Hospital name '{expected_hospital_name}' found in the first row")

        except Exception as e:
            self.fail(f"Error during add product test: {e}")


    def chemist_set_sales_values(self):
        # Directly assign the values from the configuration file
        sales_values = {
            'product_based_sales_entry_xpath1': config.get('DEFAULT', 'value1'),
            'product_based_sales_entry_xpath2': config.get('DEFAULT', 'chemist_value')
            

        }

        for key, value in sales_values.items():
            xpath = config.get('DEFAULT', key)
            input_element = self.wait_and_find(xpath)
            input_element.clear()
            input_element.send_keys(str(value))
            time.sleep(1)  # Add a small delay if necessary


    # def test_view_products(self):
    #     try:
    #         self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
    #         time.sleep(1)  # Wait for the page to load

    #         self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
    #         time.sleep(1)

    #         # Check for the presence of the table
    #         table_xpath = config.get('DEFAULT', 'table_xpath')
    #         table_element = self.wait_and_find(table_xpath)
    #         assert table_element is not None, "Table is not present on the view page"

    #         print("Table is present on the view page.")
    #     except Exception as e:
    #         self.fail(f"Error during view test: {e}")

    #     # Adding the back button click
    #     try:
    #         print("Clicking back button")
    #         back_button = self.wait_and_find(config.get('DEFAULT', 'view_back_button'))
    #         if back_button.is_enabled() and back_button.is_displayed():
    #             back_button.click()
    #             print("Back button clicked")
    #         else:
    #             print("Back button is not clickable")
    #         time.sleep(5)
    #     except Exception as e:
    #         print(f"Error while clicking back button: {e}")

    def single_customer_single_billing_name_OBV(self):
        try:
            #add customer ------------------->
            self.driver.get(config.get('DEFAULT', 'customer_chemist_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_customer_add_button_xpath'))
            print("Navigated to Customer/Chemist Master List Page")

            name_as_per_records_input = self.wait_and_find(config.get('DEFAULT', 'name_as_per_records_xpath'))
            name_as_per_records_input.send_keys(config.get('DEFAULT', 's_cus_s_bill_name'))

            name_for_usage_input = self.wait_and_find(config.get('DEFAULT', 'name_for_usage_xpath'))
            name_for_usage_input.send_keys(config.get('DEFAULT', 'name_for_usage'))

            institution_name_input = self.wait_and_find(config.get('DEFAULT', 'institution_name_xpath'))
            institution_name_input.send_keys(config.get('DEFAULT', 'institution_name'))

            # Click the dropdown box for speciality
            self.wait_and_click(config.get('DEFAULT', 'speciality_dropdown_xpath'))
            # Select the option for speciality
            speciality_option_xpath = config.get('DEFAULT', 'speciality_option_value')
            self.wait_and_click(speciality_option_xpath)
            time.sleep(1)

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'cus_bill_mobile_number'))

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
            
            

            #add billing name ----------------->
            self.driver.get(config.get('DEFAULT', 'billing_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'multi_bill_add_button_xpath'))
            print("Navigated to billing Master List Page")

            billing_name_input = self.wait_and_find(config.get('DEFAULT', 'billing_name_xpath'))
            billing_name_input.send_keys(config.get('DEFAULT', 's_cus_s_billing_name'))

            contact_person_name_input = self.wait_and_find(config.get('DEFAULT', 'contact_person_name_xpath'))
            contact_person_name_input.send_keys(config.get('DEFAULT', 'contact_person_name'))

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 's_bill_mobile_number'))

            email_id_input = self.wait_and_find(config.get('DEFAULT', 'email_id_xpath'))
            email_id_input.send_keys(config.get('DEFAULT', 'email_id'))

            Address1_input = self.wait_and_find(config.get('DEFAULT', 'address_1_xpath'))
            Address1_input.send_keys(config.get('DEFAULT', 'Address1'))

            Address2_input = self.wait_and_find(config.get('DEFAULT', 'address_2_xpath'))
            Address2_input.send_keys(config.get('DEFAULT', 'Address2'))

            City_input = self.wait_and_find(config.get('DEFAULT', 'City_xpath'))
            City_input.send_keys(config.get('DEFAULT', 'City'))

            State_input = self.wait_and_find(config.get('DEFAULT', 'State_xpath'))
            State_input.send_keys(config.get('DEFAULT', 'State'))

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")



            #business set config customer ------------>

            self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'business_set_config_add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customers_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 's_customer_name_s_bill_option_value')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Select mode of business (OBV)
            self.wait_and_click(config.get('DEFAULT', 'mode_of_business_dropdown_xpath'))
            time.sleep(1)
            mode_of_business_option_xpath = config.get('DEFAULT', 'mode_of_business_option_value_obv')
            self.wait_and_click(mode_of_business_option_xpath)
            time.sleep(1)

            # Enter reward recommendation
            self.wait_and_click(config.get('DEFAULT', 'reward_recommendation_dropdown_xpath'))
            reward_recommendation_option_xpath = config.get('DEFAULT', 'reward_recommendation_option_value')
            self.wait_and_click(reward_recommendation_option_xpath)
            time.sleep(1)

            target_value_input = self.wait_and_find(config.get('DEFAULT', 'target_values_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            target_value_input.clear()  # Clear any existing value
            target_value_input.send_keys(config.get('DEFAULT', 'target_value'))


            # Enter business set start date
            business_set_start_date_input = self.wait_and_find(config.get('DEFAULT', 'add_business_set_start_date_xpath'))
            print("Waiting for business set start date input")
            time.sleep(1)
            business_set_start_date_input.clear()
            random_start_date = self.generate_random_start_date()
            business_set_start_date_input.send_keys(random_start_date)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            #customer_config_master1 -------------->
            self.driver.get(config.get('DEFAULT', 'customer_config_master_url'))
            print("Navigated to  customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'customer_dropdown_name_xpaths'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 's_customer_name_s_bill_option_values')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Supplied_Item_Credit_Period_input = self.wait_and_find(config.get('DEFAULT', 'Supplied_Item_Credit_Period_xpath'))
            print("Waiting for target value input")
            time.sleep(1)
            Supplied_Item_Credit_Period_input.clear()  # Clear any existing value
            Supplied_Item_Credit_Period_input.send_keys(config.get('DEFAULT', 'Supplied_Item_Credit_Period'))


            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)
        
            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            #billing and stockist----------->
        #bill name and stockist name
            self.driver.get(config.get('DEFAULT', 'billName_and_stockist_config_url'))
            print("Navigated to bill name and stockist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

        

            # Select billing name
            self.wait_and_click(config.get('DEFAULT', 'billing_dropdown_name_xpath'))
            time.sleep(1)
            billing_name_option_xpath = config.get('DEFAULT', 's_cus_s_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

            # Select stockist name
            self.wait_and_click(config.get('DEFAULT', 'stockist_dropdown_name_xpath'))
            time.sleep(1)
            stockist_option_xpath = config.get('DEFAULT', 'stockist_option_value')
            self.wait_and_click(stockist_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)


            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            # bill_customer_product_config1----------->
            # add bill customer and product master
            self.driver.get(config.get('DEFAULT', 'bill_customer_and_product_master_url'))
       
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'bill_customer_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'bill_customer_name_option_value')
            customer_name_element = self.wait_and_find(customer_name_option_xpath)
            customer_name = customer_name_element.text

            # Extract alphabets only from the customer name
            alphabets = ''.join(re.findall("[A-Za-z]", customer_name))

            # Extract alphabets only from the option value
            option_value_text = self.wait_and_find(customer_name_option_xpath).text
            option_value_alphabets = ''.join(re.findall("[A-Za-z]", option_value_text))

            # Check if the extracted alphabets match and click the option if they do
            if alphabets == option_value_alphabets:
                self.wait_and_click(customer_name_option_xpath)
                time.sleep(1)
            else:
                self.fail(f"Customer name '{customer_name}' does not match the expected option value.")

            # Print the extracted alphabets (for debugging purposes)
            print(f"Customer Name Alphabets: {alphabets}")
            print(f"Option Value Alphabets: {option_value_alphabets}")

            # Click the dropdown box for billing name
            self.wait_and_click(config.get('DEFAULT', 'cus_billing_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'bill_cus_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
            time.sleep(1)

    


            # Enter 100% value in the global percentage input
            global_percentage_input = self.wait_and_find(config.get('DEFAULT', 'global_percentage_input_xpath'))
            global_percentage_input.clear()
            global_percentage_input.send_keys(config.get('DEFAULT', 'total_global_percentage_value'))
            print("Entered 100% in global percentage input")
            time.sleep(1)

            # Click the checkboxes for the given XPaths
            checkbox_xpaths = [
                config.get('DEFAULT', 'checkbox_xpath1'),
                config.get('DEFAULT', 'checkbox_xpath2'),
                config.get('DEFAULT', 'checkbox_xpath3'),
                config.get('DEFAULT', 'checkbox_xpath4')
               
            ]
            
            for xpath in checkbox_xpaths:
                checkbox = self.wait_and_find(xpath)
                if not checkbox.is_selected():
                    checkbox.click()
                time.sleep(1)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll down the page before submitting the form
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Submit the form
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")




            # Sales entry
            self.driver.get(config.get('DEFAULT', 'sales_entry_url'))
            print("Navigated to Sales Entry Page")
            
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            
            # Select the option for billing name
            billing_name_option_xpath = config.get('DEFAULT', 'S_billing_name_option_value')
            self.wait_and_click(billing_name_option_xpath)
    


            total_amount_input = self.wait_and_find(config.get('DEFAULT', 'total_amount_xpath'))
            total_amount_input.send_keys(config.get('DEFAULT', 'total_amount_value'))
            print("Entered total amount")

            value_input = self.wait_and_find(config.get('DEFAULT', 'total_sales_entry_xpath'))
            value_input.send_keys(config.get('DEFAULT', 'S_value'))
            print("Entered value")

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
            time.sleep(1)


            # Check if navigated to the business set customer master list page
            if self.is_element_present(config.get('DEFAULT', 'current_sales_value_xpath')):
                self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
                print("Navigated to Business Set Customer Master List Page")
                time.sleep(3)

                # Verify the current sales value in the business set customer master list
                current_sales_value_element = self.wait_and_find(config.get('DEFAULT', 'current_sales_value_xpath'))
                current_sales_value = current_sales_value_element.text.strip()
                print(f"Current sales value: {current_sales_value}")

                # Verify the target value in the business set customer master list
                target_value_element = self.wait_and_find(config.get('DEFAULT', 'target_value_xpath'))
                target_value = target_value_element.text.strip()
                print(f"Target value: {target_value}")

                # Check if the current sales value is greater than or equal to the target value
                assert current_sales_value >= target_value, f"Current sales value '{current_sales_value}' is less than target value '{target_value}'"
                print("Current sales value is greater than or equal to target value.")

            elif self.driver.current_url == config.get('DEFAULT', 'sales_entry_url'):
                print("Navigated to Sales Entry List Page")
                billing_name_element = self.wait_and_find(config.get('DEFAULT', 'single_bill_single_customer'))
                billing_name = billing_name_element.text.strip()
                expected_billing_name = config.get('DEFAULT', 'p_billing_name')
                assert billing_name == expected_billing_name, f"Expected billing name '{expected_billing_name}', but got '{billing_name}'"
                print(f"Billing name: {billing_name}")
            else:
                self.fail("Did not navigate to the expected page")
           
        except Exception as e:
            self.fail(f"Error during add product test: {e}")






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

    suite = unittest.TestLoader().loadTestsFromTestCase(sales_entry)
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
    test_instance = sales_entry()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_view_products()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_products - {e}")
            failed_tests += 1


        try:
            test_instance.test_add_total_sales_entry()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_total_sales_entry - {e}")
            failed_tests += 1

        try:
            test_instance.test_add_product_based_sales_entry()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_product_based_sales_entry - {e}")
            failed_tests += 1
        try:
            test_instance.test_check_multiple_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_check_multiple_customer - {e}")
            failed_tests += 1
        try:
            test_instance.test_check_chemist()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_check_chemist - {e}")
            failed_tests += 1

    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")