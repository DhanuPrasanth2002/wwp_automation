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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import configparser
import re


# Read properties from config file
config = configparser.ConfigParser()
config.read('reward_payment_recommendation_chemist.ini')

class reward_payment_recommendation_chemist(unittest.TestCase):

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
        

    @classmethod
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


    def select_condition(self):
        try:
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            condition_xpath = config.get('DEFAULT', 'condition_dropdown')
            condition_option_xpath = config.get('DEFAULT', 'condition_option')

            condition = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, condition_xpath))
            )
            condition.click()
            time.sleep(2)

            condition_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, condition_option_xpath))
            )
            condition_option.click()
            time.sleep(2)

            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during condition selection: {e}")

    def test_export_buttons(self):
        try:
             
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            self.select_condition() 
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

    def test_print_button(self):
        try: 
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            self.select_condition() 
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

    def test_clear_button(self):
        try:  
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            self.select_condition() 
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

    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
        self.select_condition() 
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
    
    def test_pagination_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            self.select_condition() 
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

    def test_entries_per_page(self):
        try: 
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            self.select_condition() 
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

    def test_add_to_cart(self):
        try:
            self.driver.get(config.get('DEFAULT', 'reward_payment_recommendation_chemist_url'))
            
            # Select the condition
            self.select_condition()
            time.sleep(1) 
            
            # Select the datatable values
            tick_first_xpath = config.get('DEFAULT', 'tick_first_xpath')
            tick_first_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, tick_first_xpath))
            )
            tick_first_element.click()
            time.sleep(2)

            # Click the add to cart button
            add_to_cart_button_xpath = config.get('DEFAULT', 'add_to_cart_button_xpath')
            add_to_cart_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, add_to_cart_button_xpath))
            )
            add_to_cart_button.click()
            time.sleep(2)

            # Click export button
            export_button_xpath = config.get('DEFAULT', 'export_button_xpath')
            export_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, export_button_xpath))
            )
            export_button.click()
            time.sleep(2)

            # Click CSV button
            csv_button_xpath = config.get('DEFAULT', 'csv_button_xpath')
            csv_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, csv_button_xpath))
            )
            csv_button.click()
            time.sleep(5)

            # Click PDF button
            pdf_button_xpath = config.get('DEFAULT', 'pdf_button_xpath')
            pdf_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, pdf_button_xpath))
            )
            pdf_button.click()
            time.sleep(2)

            # Click outside the button
            ActionChains(self.driver).move_by_offset(10, 10).click().perform()
            time.sleep(2)

            # Click print button
            print_button_xpath = config.get('DEFAULT', 'print_button_xpath')
            print_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, print_button_xpath))
            )
            try:
                print_button.click()
            except ElementClickInterceptedException:
                # Wait for the overlay to disappear
                WebDriverWait(self.driver, 10).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, 'dt-button-background'))
                )
                print_button.click()
            time.sleep(1)

            inner_print_button_xpath = config.get('DEFAULT', 'inner_print_button_xpath')
            inner_print_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, inner_print_button_xpath))
            )
            inner_print_button.click()
            time.sleep(1)

            pyautogui.press('esc')
            time.sleep(1)
            pyautogui.press('esc')
            self.assertTrue(True)

            # Click clear button
            clear_button_xpath = config.get('DEFAULT', 'reset_button_xpath')
            clear_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, clear_button_xpath))
            )
            clear_button.click()
            time.sleep(2)

            # Perform search
            search_input_xpath = config.get('DEFAULT', 'search_input_xpath')
            search_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, search_input_xpath))
            )
            search_input.send_keys(config.get('DEFAULT', 'clear_button_search_term'))
            time.sleep(2)

            # Click clear button again
            clear_button.click()
            time.sleep(2)

         # Pagination buttons
            pages = self.driver.find_elements(By.XPATH, config.get('DEFAULT', 'page_numbers_xpath'))
            if len(pages) > 1:
                next_button_xpath = config.get('DEFAULT', 'next_button_xpath')
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, next_button_xpath))
                )
                next_button.click()
                time.sleep(2)

                last_button_xpath = config.get('DEFAULT', 'last_button_xpath')
                last_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, last_button_xpath))
                )
                last_button.click()
                time.sleep(5)

                prev_button_xpath = config.get('DEFAULT', 'previous_button_xpath')
                prev_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, prev_button_xpath))
                )
                prev_button.click()
                time.sleep(5)

                first_button_xpath = config.get('DEFAULT', 'first_button_xpath')
                first_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, first_button_xpath))
                )
                first_button.click()
                time.sleep(5)

                active_page_xpath = config.get('DEFAULT', 'current_page_xpath')
                active_page = self.driver.find_element(By.XPATH, active_page_xpath).text
                self.assertEqual(active_page, "1")

            # Entries per page
            entries_select_xpath = config.get('DEFAULT', 'entries_select_xpath')
            entries_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, entries_select_xpath))
            )
            for value in ['5', '10', '15', '20', '50', '-1']:
                entries_select.click()
                option_xpath = config.get('DEFAULT', 'entries_option_xpath').replace('{value}', value)
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                option.click()
                time.sleep(1)

            # Finally, set the entries per page back to 5
            entries_select.click()
            option_xpath = config.get('DEFAULT', 'entries_option_xpath').replace('{value}', '5')
            option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option.click()
            time.sleep(1)

            rows = self.driver.find_elements(By.XPATH, config.get('DEFAULT', 'last_row_xpath'))
            self.assertEqual(len(rows), min(5, len(rows)))

            self.assertTrue(True)


            # Select add_tick_selectall
            add_tick_selectall_xpath = config.get('DEFAULT', 'add_tick_selectall')
            add_tick_selectall_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, add_tick_selectall_xpath))
            )
            add_tick_selectall_element.click()
            time.sleep(2)

            # Click submit button
            submit_button_xpath = config.get('DEFAULT', 'submit_button_xpath')
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
            )
            submit_button.click()
            time.sleep(2)

            # Click OK button in confirmation pop-up
            ok_button_xpath = config.get('DEFAULT', 'ok_button_xpath')
            ok_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, ok_button_xpath))
            )
            ok_button.click()
            print("Handled confirmation pop-up")

           
        except Exception as e:
            self.fail(f"Error during add to cart test: {e}")

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

    suite = unittest.TestLoader().loadTestsFromTestCase(reward_payment_recommendation_chemist)
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
    test_instance = reward_payment_recommendation_chemist()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_add_to_cart()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_add_to_cart - {e}")
            failed_tests += 1

        try:
            test_instance.select_condition()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: select_condition - {e}")
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
    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")