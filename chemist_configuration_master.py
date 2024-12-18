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
config.read('chemist_config.ini')

class chemistconfigmaster(unittest.TestCase):

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
        time.sleep(1)  # Wait for login to complete

    @classmethod
    def wait_and_click(cls, xpath, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element

    @classmethod
    def wait_and_find(cls, xpath, timeout=10):
        return WebDriverWait(cls.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    
    @classmethod
    def wait_and_check(cls, by, value, timeout=10):
        element = WebDriverWait(cls.driver, timeout).until(EC.element_to_be_clickable((by, value)))
        element.click()
        return element

    @order(3)
    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            export_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['export_button_xpath']))
            )
            export_button.click()
            time.sleep(2)

            csv_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['csv_button_xpath']))
            )
            csv_button.click()
            time.sleep(2)

            pdf_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['pdf_button_xpath']))
            )
            pdf_button.click()
            time.sleep(2)

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during export button test: {e}")
    @order(4)
    def test_print_button(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            print_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['print_button_xpath']))
            )
            print_button.click()
            time.sleep(5)

            inner_print_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['inner_print_button_xpath']))
            )
            inner_print_button.click()
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
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            colvis_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['colvis_button_xpath']))
            )
            colvis_button.click()
            time.sleep(2)

            colvis_options = self.driver.find_elements(By.XPATH, config['DEFAULT']['colvis_options_xpath'])
            time.sleep(2)

            for index, option in enumerate(colvis_options):
                option.click()
                time.sleep(2)

            restore_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['colvis_restore_button_xpath']))
            )
            restore_button.click()
            time.sleep(2)

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during column visibility test: {e}")
    @order(6)
    def test_clear_button(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            search_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['search_input_xpath']))
            )
            search_input.send_keys(config.get('DEFAULT', 'clear_button_search_term'))
            time.sleep(2)

            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['reset_button_xpath']))
            )
            clear_button.click()
            time.sleep(2)

            self.assertEqual(search_input.get_attribute("value"), "", "Clear button did not reset the search input")
        except Exception as e:
            self.fail(f"Error during clear button test: {e}")
    @order(7)
    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
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
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            
            # Check the number of pages
            pages = self.driver.find_elements(By.XPATH, config['DEFAULT']['page_numbers_xpath'])
            if len(pages) <= 1:
                print("Only one page present, skipping pagination button checks.")
                self.assertTrue(True)
                return
            
            # Check "Next" button
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['next_button_xpath']))
            )
            next_button.click()
            time.sleep(2)

            # Check "Last" button
            last_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['last_button_xpath']))
            )
            last_button.click()
            time.sleep(5)

            # Check "Previous" button
            prev_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['previous_button_xpath']))
            )
            prev_button.click()
            time.sleep(5)

            # Check "First" button
            first_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['first_button_xpath']))
            )
            first_button.click()
            time.sleep(5)

            # Verify we are back to the first page
            active_page = self.driver.find_element(By.XPATH, config['DEFAULT']['current_page_xpath']).text
            self.assertEqual(active_page, "1")
        except Exception as e:
            self.fail(f"Error during pagination button test: {e}")
    @order(9)
    def test_entries_per_page(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
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

    @order(1)
    def test_add_chemist_config_master(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            print("Navigated to  chemist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Select chemist name
            self.wait_and_click(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            time.sleep(1)
            chemist_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(chemist_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))

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


            # Click the clear button
            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(1)

            # Re-enter values after clearing
            # Select chemist name
            self.wait_and_click(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            time.sleep(1)
            chemist_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(chemist_name_option_xpath)
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

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'Reward_Points_Percentage'),
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created business set chemist entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add business set chemist test: {e}")
        
    @order(10)
    def test_view_chemist_config_master(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)

            chemist_name_field = self.wait_and_find(config.get('DEFAULT', 'chemist_name_xpath'))
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_xpath'))
            reward_points_percentage_field = self.wait_and_find(config.get('DEFAULT', 'reward_recommendation_xpath'))
            supplied_item_credit_period_days_field = self.wait_and_find(config.get('DEFAULT', 'target_value_xpath'))
            headquarters_name_field = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_xpath'))
            rep_name_field = self.wait_and_find(config.get('DEFAULT', 'rep_name_xpath'))

            assert chemist_name_field.get_attribute("readonly") == "true", "chemist name field is editable"
            assert mode_of_business_field.get_attribute("readonly") == "true", "mode of business field is editable"
            assert reward_points_percentage_field.get_attribute("readonly") == "true", "reward points percentage field is editable"
            assert supplied_item_credit_period_days_field.get_attribute("readonly") == "true", "supplied item credit period days field is editable"
            assert headquarters_name_field.get_attribute("readonly") == "true", "headquarters name field is editable"
            assert rep_name_field.get_attribute("readonly") == "true", "rep name field is editable"
            print("All fields are correctly set to readonly.")
        except Exception as e:
            self.fail(f"Error during view test: {e}")

        # Adding the back button click
        try:
            print("Clicking back button")
            back_button = self.wait_and_find(config.get('DEFAULT', 'back_button_xpath'))
            if back_button.is_enabled() and back_button.is_displayed():
                back_button.click()
                print("Back button clicked")
            else:
                print("Back button is not clickable")
            time.sleep(5)
        except Exception as e:
            print(f"Error while clicking back button: {e}")

    @order(12)
    def test_delete_chemist_config_master(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            billing_entry_xpath = config.get('DEFAULT', 'chemist_config_master_entry_xpath')
            delete_button_xpath = config.get('DEFAULT', 'delete_button_xpath')
            notification_xpath = config.get('DEFAULT', 'custom_notification_id')
            notification_ok_button_xpath = config.get('DEFAULT', 'notification_ok_button_id')

            billing_entry = self.wait_and_find(billing_entry_xpath)
            billing_id = billing_entry.get_attribute("data-id")
            self.wait_and_click(delete_button_xpath)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, notification_xpath)))
            self.wait_and_click(notification_ok_button_xpath)
            time.sleep(1)
            with self.assertRaises(Exception):
                self.driver.find_element(By.XPATH, f"//table[@id='customerTable']//tr[@data-id='{billing_id}']")
        except Exception as e:
            self.fail(f"Error during delete billing test: {e}")


    @order(11)
    def test_edit_chemist_config_master(self):
        try:
            # Navigate to the edit business set chemist config page
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
            
            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'edit_back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
            time.sleep(1)

            # Enter new values into all fields using XPath
            chemist_name_field = self.wait_and_find(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            reward_points_percentage_field = self.wait_and_find(config.get('DEFAULT', 'reward_recommendation_dropdown_xpath'))
            supplied_item_credit_period_days_field = self.wait_and_find(config.get('DEFAULT', 'target_value_xpath'))
            headquarters_name_field = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            rep_name_field = self.wait_and_find(config.get('DEFAULT', 'rep_name_dropdown_xpath'))

            assert chemist_name_field.is_enabled(), "chemist name field is not editable"
            assert reward_points_percentage_field.is_enabled(), "reward points percentage field is not editable"
            assert supplied_item_credit_period_days_field.is_enabled(), "supplied item credit period days field is not editable"
            assert headquarters_name_field.is_enabled(), "headquarters name field is not editable"
            assert rep_name_field.is_enabled(), "rep name field is not editable"


            # Enter supplied item credit period days
            supplied_item_credit_period_days_field.clear()
            supplied_item_credit_period_days_field.send_keys(config.get('DEFAULT', 'edit_supplied_item_credit_period_days'))
            time.sleep(1)


            # Enter reward points percentage
            reward_points_percentage_field.clear()
            reward_points_percentage_field.send_keys(config.get('DEFAULT', 'edit_reward_points_percentage'))
            time.sleep(1)

             # Scroll to the update button before clicking
            update_button = self.wait_and_find(config.get('DEFAULT', 'update_button_xpath'))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", update_button)
            time.sleep(1)
 

            # Click the update button
            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            time.sleep(1)

            # Handle the confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            time.sleep(1)

            # Verify the updated values in the business set chemist config table
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            time.sleep(1)

            # Search for the updated entry
            search_input = self.wait_and_find(config.get('DEFAULT', 'search_input_xpath'))
            search_input.clear()
            search_input.send_keys(config.get('DEFAULT', 'edit_reward_points_percentage'))
            time.sleep(1)

            updated_entry = self.wait_and_find(config.get('DEFAULT', 'updated_user_xpath'))
            assert updated_entry is not None, "Updated chemist details not found in the table"

            print("chemist details updated successfully.")
        except Exception as e:
            self.fail(f"Error during edit test: {e}")
    
    def generate_random_start_date(self):
        start_date = datetime(1990, 1, 1)
        end_date = datetime.now()
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        random_date = random_date.replace(day=1)
        return random_date.strftime("%d/%m/%Y")
    @order(13)
    def test_mode_of_business(self):
        try:
            # Navigate to the edit business set customer config page
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            self.driver.get(config.get('DEFAULT', 'business_set_config_customer_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'check_customer_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'check_customer_name_option_value')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Select mode of business (OBV)
            self.wait_and_click(config.get('DEFAULT', 'mode_of_business_dropdown_xpath'))
            time.sleep(1)
            mode_of_business_option_xpath = config.get('DEFAULT', 'mode_of_business_option_value_obv')
            self.wait_and_click(mode_of_business_option_xpath)
            time.sleep(1)

            # Enter reward recommendation
            self.wait_and_click(config.get('DEFAULT', 'check_reward_recommendation_dropdown_xpath'))
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

            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            print("Navigated to business set customer config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Select customer name
            self.wait_and_click(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            time.sleep(1)
            customer_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(customer_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is correctly fetched and populated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            expected_mode_of_business = config.get('DEFAULT', 'expected_mode_of_business')
            assert mode_of_business_value == expected_mode_of_business, f"Expected mode of business '{expected_mode_of_business}', but got '{mode_of_business_value}'"
            print(f"Mode of business is correctly populated: {mode_of_business_value}")

        except Exception as e:
            self.fail(f"Error during mode of business test: {e}")

    @order(14)
    def test_rerun_add_chemist_config_master(self):
        try:
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            print("Navigated to  chemist config Master List Page")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Select chemist name
            self.wait_and_click(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            time.sleep(1)
            chemist_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(chemist_name_option_xpath)
            time.sleep(1)

            # Check if mode of business is auto-generated
            mode_of_business_field = self.wait_and_find(config.get('DEFAULT', 'mode_of_business_field_xpath'))
            mode_of_business_value = mode_of_business_field.get_attribute('value')
            assert mode_of_business_value != "", "Mode of business was not auto-generated"

            Reward_Points_Percentage_input = self.wait_and_find(config.get('DEFAULT', 'add_Reward_Points_Percentage_xpath'))
            print("Waiting for Reward Points Percentage input")
            time.sleep(1)
            Reward_Points_Percentage_input.clear()  # Clear any existing value
            Reward_Points_Percentage_input.send_keys(config.get('DEFAULT', 'Reward_Points_Percentage'))

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


            # Click the clear button
            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(1)

            # Re-enter values after clearing
            # Select chemist name
            self.wait_and_click(config.get('DEFAULT', 'chemist_dropdown_name_xpath'))
            time.sleep(1)
            chemist_name_option_xpath = config.get('DEFAULT', 'chemist_name_option_value')
            self.wait_and_click(chemist_name_option_xpath)
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

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'chemist_config_master_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'Reward_Points_Percentage'),
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created business set chemist entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add business set chemist test: {e}")
       

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

    suite = unittest.TestLoader().loadTestsFromTestCase(chemistconfigmaster)
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
    test_instance = chemistconfigmaster()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_chemist_config_master()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_chemist_config_master - {e}")
            failed_tests += 1
        try:
            test_instance.test_mode_of_business()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_mode_of_business - {e}")
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
            test_instance.test_view_chemist_config_master()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_chemist_config_master - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_chemist_config_master()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_chemist_config_master - {e}")
            failed_tests += 1

        try:
            test_instance.test_delete_chemist_config_master()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_delete_chemist_config_master - {e}")
            failed_tests += 1
        try:
            test_instance.test_rerun_add_chemist_config_master()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_rerun_add_chemist_config_master - {e}")
            failed_tests += 1
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")