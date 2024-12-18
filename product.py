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
from selenium.common.exceptions import TimeoutException
import configparser
import re
from test_utils import order

# Read properties from config file
config = configparser.ConfigParser()
config.read('product_config.ini')

class productTests(unittest.TestCase):

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
        
        if validation_type == "text":
            assert re.match("^[A-Za-z ]*$", value), f"Validation failed for {value}: Only alphabets and spaces are allowed."
        elif validation_type == "text_no_space":
            assert re.match("^[A-Za-z]*$", value), f"Validation failed for {value}: Only alphabets are allowed."
        elif validation_type == "any":
            assert len(value) <= 255, f"Validation failed for {value}: Exceeds maximum length of 255 characters."
        elif validation_type == "product_name":
            # Allow alphanumeric characters and hyphens, with a max length of 255
            assert re.match(r"^[A-Za-z0-9\- ]*$", value), f"Validation failed for {value}: Only alphanumeric characters and hyphens are allowed."
            assert len(value) <= 255, f"Validation failed for {value}: Exceeds maximum length of 255 characters."


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
    
    @order(2)
    def test_add_product(self):
        try:
            # Navigate to Product Master List Page
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Product Master List Page")

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Fill out "Name of the Product" field
            name_of_product_input = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product'), "product_name")

            # Click the Clear button to test functionality
            print("Attempting to click Clear Button")
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config.get('DEFAULT', 'clear_button_xpath')))
            )
            clear_button.click()
            print("Clicked Clear Button")
            time.sleep(2)

            # Verify that the Clear button works by checking if the input field is empty
            assert name_of_product_input.get_attribute("value") == "", "Clear button did not reset the product name input"
            print("Clear button works correctly on the add page")

            # Re-enter "Name of the Product" after clearing it
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product'), "product_name")
            time.sleep(1)
            # Submit the form
            print("Attempting to click Submit Button")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            # Handle confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            # Verify the new product entry in the list
            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            time.sleep(1)
            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new product entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_of_product')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created product entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add product test: {e}")

    @order(9)
    def test_view_product(self):
        try:
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)

            product_name_field = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))


            assert product_name_field.get_attribute("readonly") == "true", "product name field is editable"

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

    @order(10)
    def test_edit_product_name(self):
        try:
            # Navigate to Product Master List Page and open the edit view for the specific product
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
            print("Navigated to Product Edit Page")
            time.sleep(1)

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))

            # Locate the "Name of the Product" field
            name_of_product_field = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))

            # Verify that the field is editable
            assert name_of_product_field.is_enabled(), "Product Name field is not editable"

            # Clear the "Name of the Product" field and enter a new value
            name_of_product_field.clear()
            new_product_name = config.get('DEFAULT', 'edit_name_of_product')
            name_of_product_field.send_keys(new_product_name)
            print(f"Entered new value for 'Name of the Product': {new_product_name}")

            # Click the update button
            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            time.sleep(1)
            print("Clicked the update button")

            # Handle the confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")
            time.sleep(1)

            # Verify the updated product name in the product master list
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            time.sleep(1)

            # Locate the updated product entry to verify the name change
            updated_product_name = self.wait_and_find(config.get('DEFAULT', 'updated_product_name_xpath'))
            assert updated_product_name.text == new_product_name, "Product name did not update as expected"
            print("Product name updated successfully.")
            
        except Exception as e:
            self.fail(f"Error during edit product name test: {e}")

    @order(11)
    def test_delete_product(self):
        try:
            # Navigate to Product Master List Page
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            
            # Retrieve necessary XPaths from configuration for product entry and delete button
            product_entry_xpath = config.get('DEFAULT', 'product_entry_xpath')
            delete_button_xpath = config.get('DEFAULT', 'delete_button_xpath')
            notification_xpath = config.get('DEFAULT', 'custom_notification_id')
            notification_ok_button_xpath = config.get('DEFAULT', 'notification_ok_button_id')

            # Locate the product entry and obtain its unique identifier
            product_entry = self.wait_and_find(product_entry_xpath)
            product_id = product_entry.get_attribute("data-id")
            
            # Click the delete button for the product
            self.wait_and_click(delete_button_xpath)
            print("Clicked delete button for product")
            
            # Wait for the confirmation notification pop-up to appear
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, notification_xpath)))
            
            # Confirm the deletion by clicking the OK button in the notification pop-up
            self.wait_and_click(notification_ok_button_xpath)
            print("Confirmed deletion in notification pop-up")
            
            time.sleep(1)

            # Verify that the product entry is no longer present in the product table
            with self.assertRaises(Exception):
                self.driver.find_element(By.XPATH, f"//table[@id='productTable']//tr[@data-id='{product_id}']")
            print("Product deleted successfully, not found in the list")
            
        except Exception as e:
            self.fail(f"Error during delete product test: {e}")

    @order(12)
    def test_rerun_add_product(self):
        try:
            # Navigate to Product Master List Page
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            print("Navigated to Product Master List Page")

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))

            # Fill out "Name of the Product" field
            name_of_product_input = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product'), "product_name")

            # Submit the form
            print("Attempting to click Submit Button")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            # Handle confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            # Verify the new product entry in the list
            time.sleep(1)
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            time.sleep(1)
            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new product entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'name_of_product')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"
            # Fill out "Name of the Product" field
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            name_of_product_input = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product1'), "product_name")

            # Submit the form
            print("Attempting to click Submit Button")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            # Handle confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            # Fill out "Name of the Product" field
            name_of_product_input = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product2'), "product_name")

            # Submit the form
            print("Attempting to click Submit Button")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            # Handle confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")


            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            # Fill out "Name of the Product" field
            name_of_product_input = self.wait_and_find(config.get('DEFAULT', 'name_of_product_xpath'))
            self.validate_input(name_of_product_input, config.get('DEFAULT', 'name_of_product3'), "product_name")

            # Submit the form
            print("Attempting to click Submit Button")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            print("Clicked the submit button")

            # Handle confirmation pop-up
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            print("Handled confirmation pop-up")

            print("Newly created product entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add product test: {e}")


    @order(3)
    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            export_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['export_button_xpath']))
            )
            export_button.click()
            time.sleep(2)

            csv_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['csv_button_xpath']))
            )
            csv_button.click()
            time.sleep(5)

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
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
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
    def test_clear_button(self):
        try:
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
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

    @order(6)
    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
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
    
    @order(7)
    def test_pagination_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
            
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

    @order(8)
    def test_entries_per_page(self):
        try:
            self.driver.get(config.get('DEFAULT', 'product_masterlist_url'))
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

    suite = unittest.TestLoader().loadTestsFromTestCase(productTests)
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
    test_instance = productTests()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_product()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_product - {e}")
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
            test_instance.test_view_product()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_product - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_product_name()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_product_name - {e}")
            failed_tests += 1

        try:
            test_instance.test_delete_product()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_delete_product - {e}")
            failed_tests += 1
        try:
            test_instance.test_rerun_add_product()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_product - {e}")
            failed_tests += 1
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")