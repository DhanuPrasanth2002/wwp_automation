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
import time
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import pyautogui
from test_utils import order


# Read properties from config file
config = configparser.ConfigParser()
config.read('headquarters.config.ini')

class HeadquartersTests(unittest.TestCase):

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

    def validate_input(self, input_element, value, validation_type):
        input_element.clear()
        input_element.send_keys(value)
        time.sleep(1)
        if validation_type == "text":
            assert re.match("^[A-Za-z ]*$", value), f"Validation failed for {value}: Only alphabets and spaces are allowed."


    @order(9)
    def test_view_headquarters(self):
        try:
            self.driver.get(config.get('DEFAULT', 'base_url'))
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'back_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)
            self.assertEqual(
                self.wait_and_find(config.get('DEFAULT', 'headquarters_name_field_xpath')).get_attribute("readonly"),
                "true",
                "Headquarters Name field is editable"
            )
        except Exception as e:
            self.fail(f"Error during view headquarters test: {e}")

        # Adding the back button click
        try:
            print("Clicking back button")
            back_button = self.wait_and_find(config.get('DEFAULT', 'view_back_button_xpath'))
            if back_button.is_enabled() and back_button.is_displayed():
                back_button.click()
                print("Back button clicked")
            else:
                print("Back button is not clickable")
            time.sleep(5)
        except Exception as e:
            print(f"Error while clicking back button: {e}")


    @order(2)
    def test_add_headquarters(self):
        try:
           
            self.driver.get(config.get('DEFAULT', 'base_url'))
            
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            time.sleep(1)
            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
          

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            headquarters_name_input = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_input_xpath'))
            headquarters_name = config.get('DEFAULT', 'headquarters_name')
            self.validate_input(headquarters_name_input, headquarters_name, "text")            
            self.wait_and_click(config.get('DEFAULT', 'clear_button_xpath'))
            self.assertEqual(headquarters_name_input.get_attribute("value"), "", "Clear button did not reset the headquarters name input")
            self.validate_input(headquarters_name_input, headquarters_name, "text")
            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
  
            self.driver.get(config.get('DEFAULT', 'base_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new headquarters entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'headquarters_name')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            print("Newly created headquarters entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add headquarters test: {e}")
    
    @order(10)
    def test_edit_headquarters(self):
        try:
            self.driver.get(config.get('DEFAULT', 'base_url'))
            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))
            time.sleep(5)

            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
            print("Clicked back button")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'edit_button_xpath'))

            headquarters_name_field = self.wait_and_find(config.get('DEFAULT', 'update_headquarters_name_field_xpath'))
            self.assertTrue(headquarters_name_field.is_enabled(), "Headquarters Name field is not editable")
            self.validate_input(headquarters_name_field,"hosur", "text")
            time.sleep(1)

            self.wait_and_click(config.get('DEFAULT', 'update_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
            time.sleep(1)

            self.driver.get(config.get('DEFAULT', 'base_url'))
            time.sleep(1)

            self.assertIsNotNone(
                self.wait_and_find(config.get('DEFAULT', 'updated_headquarters_xpath')),
                "Updated headquarters details not found in the table"
            )
        except Exception as e:
            self.fail(f"Error during edit headquarters test: {e}")

    @order(11)
    def test_delete_headquarters(self):
        try:
            self.driver.get(config.get('DEFAULT', 'base_url'))
            headquarters_entry_xpath = config.get('DEFAULT', 'headquarters_entry_xpath')
            delete_button_xpath = config.get('DEFAULT', 'delete_button_xpath')
            notification_xpath = config.get('DEFAULT', 'notification_xpath')
            notification_ok_button_xpath = config.get('DEFAULT', 'notification_ok_button_xpath')

            headquarters_entry = self.wait_and_find(headquarters_entry_xpath)
            headquarters_id = headquarters_entry.get_attribute("data-id")
            self.wait_and_click(delete_button_xpath)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, notification_xpath)))
            self.wait_and_click(notification_ok_button_xpath)
            time.sleep(1)
            with self.assertRaises(Exception):
                self.driver.find_element(By.XPATH, f"//table[@id='customerTable']//tr[@data-id='{headquarters_id}']")
        except Exception as e:
            self.fail(f"Error during delete headquarters test: {e}")

    @order(3)
    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'base_url'))
            export_button_xpath = config.get('DEFAULT', 'export_button_xpath')
            csv_button_xpath = config.get('DEFAULT', 'csv_button_xpath')
            pdf_button_xpath = config.get('DEFAULT', 'pdf_button_xpath')

            export_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, export_button_xpath))
            )
            export_button.click()
            time.sleep(2)

            csv_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, csv_button_xpath))
            )
            csv_button.click()
            time.sleep(2)

            pdf_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, pdf_button_xpath))
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
                    print_button_xpath = config.get('DEFAULT', 'print_button_xpath')
                    inner_print_button_xpath = config.get('DEFAULT', 'inner_print_button_xpath')

                    print_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, print_button_xpath))
                    )
                    print_button.click()
                    time.sleep(5)

                    inner_print_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, inner_print_button_xpath))
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
            self.driver.get(config.get('DEFAULT', 'base_url'))
            search_input_xpath = config.get('DEFAULT', 'search_input_xpath')
            clear_button_xpath = config.get('DEFAULT', 'reset_button_xpath')

            search_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, search_input_xpath))
            )
            search_input.send_keys("test search term")
            time.sleep(2)

            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, clear_button_xpath))
            )
            clear_button.click()
            time.sleep(2)

            self.assertEqual(search_input.get_attribute("value"), "", "Clear button did not reset the search input")
        except Exception as e:
            self.fail(f"Error during clear button test: {e}")

    @order(6)
    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'base_url'))
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
            self.driver.get(config.get('DEFAULT', 'base_url'))
            
            # Check the number of pages
            pages = self.driver.find_elements(By.XPATH, config['DEFAULT']['page_number_xpath'])
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
            self.driver.get(config.get('DEFAULT', 'base_url'))
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

    @order(12)
    def test_rerun_add_headquarters(self):
        try:
           
            self.driver.get(config.get('DEFAULT', 'base_url'))
            
            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))
            time.sleep(1)
            # Click the back button
            print("Clicking back button")
            self.wait_and_click(config.get('DEFAULT', 'back_button'))
          

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            headquarters_name_input = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_input_xpath'))
            headquarters_name = config.get('DEFAULT', 'headquarters_name')
            self.validate_input(headquarters_name_input, headquarters_name, "text")            

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))
  
            self.driver.get(config.get('DEFAULT', 'base_url'))
            time.sleep(1)

            try:
                self.wait_and_click(config.get('DEFAULT', 'first_page_button_xpath'))
                time.sleep(1)
            except:
                pass

            # Verify the new headquarters entry in the first row
            first_row = self.wait_and_find(config.get('DEFAULT', 'first_row_xpath'))
            first_row_text = first_row.text
            print(f"First row text: {first_row_text}")

            # Verify the expected values in the first row
            expected_values = [
                config.get('DEFAULT', 'headquarters_name')
            ]

            for value in expected_values:
                assert value in first_row_text, f"Expected value '{value}' not found in the first row"

            self.wait_and_click(config.get('DEFAULT', 'add_button_xpath'))


            headquarters_name_input = self.wait_and_find(config.get('DEFAULT', 'headquarters_name_input_xpath'))
            headquarters_name = config.get('DEFAULT', 'headquarters_name1')
            self.validate_input(headquarters_name_input, headquarters_name, "text")            

            self.wait_and_click(config.get('DEFAULT', 'submit_button_xpath'))
            self.wait_and_click(config.get('DEFAULT', 'ok_button_xpath'))

            print("Newly created headquarters entry verified successfully.")
        except Exception as e:
            self.fail(f"Error during add headquarters test: {e}")
    

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

    suite = unittest.TestLoader().loadTestsFromTestCase(HeadquartersTests)
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
    test_instance = HeadquartersTests()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_headquarters - {e}")
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
            test_instance.test_view_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_headquarters - {e}")
            failed_tests += 1

        try:
            test_instance.test_edit_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_edit_headquarters - {e}")
            failed_tests += 1

        try:
            test_instance.test_delete_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_delete_headquarters - {e}")
            failed_tests += 1

        try:
            test_instance.test_rerun_add_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_headquarters - {e}")
            failed_tests += 1
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")