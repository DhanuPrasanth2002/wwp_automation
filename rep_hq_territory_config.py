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
from test_utils import order


# Read properties from config file
config = configparser.ConfigParser()
config.read('rep,hq,territory_config.ini')

class RepHqTerritoryConfigTests(unittest.TestCase):

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

    @order(3)
    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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
        self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            
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
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
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


    @order(10)
    def test_view_rep_hq_territory_config(self):
        try:
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)

            headquarters_name_field = self.wait_and_find(config.get('DEFAULT', 'headquarters_xpath'))
            rep_name_field = self.wait_and_find(config.get('DEFAULT', 'rep_name_xpath'))
            territory_name_field = self.wait_and_find(config.get('DEFAULT', 'territory_name_xpath'))
           
            assert headquarters_name_field.get_attribute("readonly") == "true", "headquarters name field is editable"
            assert rep_name_field.get_attribute("readonly") == "true", "rep name field is editable"
            assert territory_name_field.get_attribute("readonly") == "true", "territory name field is editable"

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

    @order(2)
    def test_add_rep_hq_territory_config(self):
        try:
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            print("Navigated to rep hq territory config Master List Page")


            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

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


            # Click outside any place (e.g., click on the body element)
            self.driver.execute_script("document.body.click();")
            time.sleep(1)


            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'headquarters_name_option_text'),
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created product entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add product test: {e}")
   
    @order(11)
    def test_edit_rep_hq_territory_config(self):
        try:
            # Navigate to the edit rep hq territory master list page
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            time.sleep(1)
            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))   
            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))

            # Enter new values into all fields using XPath
            headquarters_name_field = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            rep_name_field = self.wait_and_find(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            territory_name_field = self.wait_and_find(config.get('DEFAULT', 'territory_name_dropdown_xpath'))


            assert headquarters_name_field.is_enabled(), "headquarters name field is not editable"
            assert rep_name_field.is_enabled(), "rep name field is not editable"
            assert territory_name_field.is_enabled(), "territory name field is not editable"

            try:
                Select(rep_name_field).select_by_visible_text(config.get('DEFAULT', 'rep_name'))
            except NoSuchElementException:
                self.fail(f"rep_name '{config.get('DEFAULT', 'rep_name')}' not found in the dropdown")
            time.sleep(1)

            try:
                Select(headquarters_name_field).select_by_visible_text(config.get('DEFAULT', 'headquarters_name'))
            except NoSuchElementException:
                self.fail(f"headquarters_name '{config.get('DEFAULT', 'headquarters_name')}' not found in the dropdown")
            time.sleep(1)


           
            # Click outside any place (e.g., click on the body element)
            self.driver.execute_script("document.body.click();")
            time.sleep(1)

            # Click the update button
            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            time.sleep(1)

            # Handle the confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            time.sleep(1)

            # Verify the updated values in the edit_rep_hq_territory config table
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            time.sleep(1)

            updated_user = self.wait_and_find(config.get('DEFAULT', 'updated_user_xpath'))
            assert updated_user is not None, "Updated edit_rep_hq_territory details not found in the table"

            print("edit_rep_hq_territory details updated successfully.")
        except Exception as e:
            self.fail(f"Error during edit test: {e}")


    @order(12)
    def test_delete_rep_hq_territory(self):
        try:
            # Navigate to Product Master List Page
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            
            # Retrieve necessary XPaths from configuration for rep_hq_territory entry and delete button
            product_entry_xpath = config.get('DEFAULT', 'rep_hq_territory_entry_xpath')
            delete_button_xpath = config.get('DEFAULT', 'delete_button_xpath')
            notification_xpath = config.get('DEFAULT', 'custom_notification_id')
            notification_ok_button_xpath = config.get('DEFAULT', 'notification_ok_button_id')

            # Locate the product entry and obtain its unique identifier
            rep_hq_territory_entry = self.wait_and_find(product_entry_xpath)
            product_id = rep_hq_territory_entry.get_attribute("data-id")
            
            # Click the delete button for the product
            self.wait_and_click(delete_button_xpath)
            print("Clicked delete button for rep_hq_territory")
            
            # Wait for the confirmation notification pop-up to appear
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, notification_xpath)))
            
            # Confirm the deletion by clicking the OK button in the notification pop-up
            self.wait_and_click(notification_ok_button_xpath)
            print("Confirmed deletion in notification pop-up")
            
            time.sleep(1)

            # Verify that the product entry is no longer present in the rep_hq_territory table
            with self.assertRaises(Exception):
                self.driver.find_element(By.XPATH, f"//table[@id='productTable']//tr[@data-id='{product_id}']")
            print("Product deleted successfully, not found in the list")
            
        except Exception as e:
            self.fail(f"Error during delete rep_hq_territory test: {e}")
    @order(13)
    def test_dropdown_headquarters(self):
        try:
            # Step 1: Navigate to the headquarters list page
            self.driver.get(config.get('DEFAULT', 'headquarters_list_url'))
            print("Navigated to Headquarters Master List Page")
            time.sleep(1)

            # Step 2: Click the add button to navigate to the add headquarters page
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Add Headquarters Page")
            time.sleep(1)

            # Step 3: Enter the headquarters value and submit
            headquarters_name_input = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_input_xpath'))
            dropdown_headquarters_name = config.get('DEFAULT', 'dropdown_headquarters_name')
            print(f"Entering headquarters name: {dropdown_headquarters_name}")
            headquarters_name_input.clear()
            headquarters_name_input.send_keys(dropdown_headquarters_name)
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button for headquarters")
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up for headquarters")
            time.sleep(1)

            # Step 4: Navigate to the config add page
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            print("Navigated to Rep HQ Territory Config Master List Page")
            time.sleep(1)
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Clicked add button on Rep HQ Territory Config Master List Page")
            time.sleep(1)

            # Step 5: Click the dropdown and check if the newly created headquarters value is present
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            print("Clicked headquarters dropdown")
            time.sleep(1)
            headquarters_name_option_value = config.get('DEFAULT', 'dropdown_headquarters_name_option_value')
            headquarters_option = self.wait_and_find(headquarters_name_option_value)
            print(f"Dropdown option text: {headquarters_option.text}")
            assert headquarters_option.text == dropdown_headquarters_name, f"Expected headquarters name '{dropdown_headquarters_name}' not found in the dropdown"
            print("Headquarters name is found in the dropdown")

            # Select the option for headquarters
            self.wait_and_click(headquarters_name_option_value)
            time.sleep(1)
        except Exception as e:
            self.fail(f"Error during add headquarters dropdown test: {e}")
    @order(14)
    def test_dropdown_rep(self):
        try:

            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
    #         print("Navigated to Headquarters Master List Page")
            # Step 1: Navigate to the rep list page
            self.driver.get(config.get('DEFAULT', 'rep_list_url'))
            print("Navigated to Rep Master List Page")
            time.sleep(1)

            # Step 2: Click the add button to navigate to the add rep page
            self.wait_and_click(config.get('DEFAULT', 'check_add_button_xpath'))
            print("Navigated to Add Rep Page")
            time.sleep(1)

            # Step 3: Enter the rep value and submit
            rep_name_input = self.wait_and_find(config.get('DEFAULT', 'check_rep_name_xpath'))
            rep_name_input.send_keys(config.get('DEFAULT', 'rep_name'))

            mobile_number_input = self.wait_and_find(config.get('DEFAULT', 'mobile_number_xpath'))
            mobile_number_input.send_keys(config.get('DEFAULT', 'mobile_number'))

            email_id_input = self.wait_and_find(config.get('DEFAULT', 'email_id_xpath'))
            email_id_input.send_keys(config.get('DEFAULT', 'email_id'))

            address_1_input = self.wait_and_find(config.get('DEFAULT', 'address_1_xpath'))
            address_1_input.send_keys(config.get('DEFAULT', 'address_1'))

            address_2_input = self.wait_and_find(config.get('DEFAULT', 'address_2_xpath'))
            address_2_input.send_keys(config.get('DEFAULT', 'address_2'))

            city_input = self.wait_and_find(config.get('DEFAULT', 'city_xpath'))
            city_input.send_keys(config.get('DEFAULT', 'city'))

            state_input = self.wait_and_find(config.get('DEFAULT', 'state_xpath'))
            state_input.send_keys(config.get('DEFAULT', 'state'))


            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button for rep")
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up for rep")
            time.sleep(1)

            # Step 4: Navigate to the config add page
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            print("Navigated to Rep HQ Territory Config Master List Page")
            time.sleep(1)
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Clicked add button on Rep HQ Territory Config Master List Page")
            time.sleep(1)

            # Step 5: Click the dropdown and check if the newly created rep value is present
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            print("Clicked rep dropdown")
            time.sleep(1)
            rep_name = config.get('DEFAULT', 'rep_name')
            rep_option_xpath = f"//option[text()='{rep_name}']"
            rep_option = self.wait_and_find(rep_option_xpath)
            print(f"Dropdown option text: {rep_option.text}")
            assert rep_option.text == rep_name, f"Expected rep name '{rep_name}' not found in the dropdown"
            print("Rep name is found in the dropdown")

            # Select the option for rep
            self.wait_and_click(rep_option_xpath)
            time.sleep(1)
        except Exception as e:
            self.fail(f"Error during add rep dropdown test: {e}")


    @order(15)
    def test_rerun_add_rep_hq_territory_config(self):
        try:
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            print("Navigated to rep hq territory config Master List Page")


            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

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


            # Click outside any place (e.g., click on the body element)
            self.driver.execute_script("document.body.click();")
            time.sleep(1)


            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(1)

            # Click the dropdown box for rep name
            self.wait_and_click(config.get('DEFAULT', 'rep_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            rep_name_option_xpath = config.get('DEFAULT', 'rep_name_option_value')
            self.wait_and_click(rep_name_option_xpath)
            time.sleep(1)

            # Click the dropdown box for headquarters name
            self.wait_and_click(config.get('DEFAULT', 'headquarters_name_dropdown_xpath'))
            time.sleep(1)

            # Select the option for rep name
            headquarters_name_option_xpath = config.get('DEFAULT', 'headquarters_name_option_value')
            self.wait_and_click(headquarters_name_option_xpath)
            time.sleep(1)

            # Click outside any place
            actions = ActionChains(self.driver)
            actions.move_by_offset(0, 0).click().perform()
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            

            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'rep_hq_territory_config_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'headquarters_name_option_text'),
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created product entry verified successfully.")
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

    suite = unittest.TestLoader().loadTestsFromTestCase(RepHqTerritoryConfigTests)
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
    test_instance = RepHqTerritoryConfigTests()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_rep_hq_territory_config()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_rep_hq_territory_config - {e}")
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
            test_instance.test_view_rep_hq_territory_config()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_rep_hq_territory_config - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_rep_hq_territory_config()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_rep_hq_territory_config - {e}")
            failed_tests += 1

        try:
            test_instance.test_delete_rep_hq_territory()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_delete_rep_hq_territory - {e}")
            failed_tests += 1
        try:
            test_instance.test_dropdown_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_dropdown_headquarters - {e}")
            failed_tests += 1



        try:
            test_instance.test_dropdown_rep()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_dropdown_rep - {e}")
            failed_tests += 1
        try:
            test_instance.test_rerun_add_rep_hq_territory_config()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_rep_hq_territory_config - {e}")
            failed_tests += 1
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")