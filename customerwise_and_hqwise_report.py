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
config.read('customerwise_and_hqwise_report.ini')

class customerwiseandhqwisereport(unittest.TestCase):

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


    def test_select_headquarters(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            customer_xpath = config.get('DEFAULT', 'hq_dropdown')
            customer_option_xpath = config.get('DEFAULT', 'hq_option_xpath')

            condition = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, customer_xpath))
            )
            condition.click()
            time.sleep(2)

            condition_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, customer_option_xpath))
            )
            condition_option.click()
            time.sleep(2)

            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during condition selection: {e}")

    def test_select_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            customer_xpath = config.get('DEFAULT', 'customer_dropdown')
            customer_option_xpath = config.get('DEFAULT', 'customer_option_xpath')

            condition = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, customer_xpath))
            )
            condition.click()
            time.sleep(2)

            condition_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, customer_option_xpath))
            )
            condition_option.click()
            time.sleep(2)

            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Error during condition selection: {e}")


    def test_export_buttons(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            self.test_select_headquarters() 
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
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            self.test_select_headquarters() 
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
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            self.test_select_headquarters() 
            search_input = self.wait_and_find(config.get('DEFAULT', 'search_input_xpath'))
            search_input.send_keys(config.get('DEFAULT', 'clear_button_search_term'))
            time.sleep(2)

            clear_button = self.wait_and_click(config.get('DEFAULT', 'reset_button_xpath'))
            time.sleep(2)

            # Re-locate the search input element after clicking the clear button
            search_input = self.wait_and_find(config.get('DEFAULT', 'search_input_xpath'))
            self.assertEqual(search_input.get_attribute("value"), "", "Clear button did not reset the search input")
        except Exception as e:
            self.fail(f"Error during clear button test: {e}")


    def test_search_functionality(self):
        self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
        self.test_select_headquarters() 
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
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            self.test_select_headquarters() 
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
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            self.test_select_customer() 
            entries_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, config['DEFAULT']['entries_select_xpath']))
            )
            for value in ['5', '10', '15', '20', '50', '-1']:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", entries_select)
                self.driver.execute_script("arguments[0].click();", entries_select)
                option_xpath = config['DEFAULT']['entries_option_xpath'].replace('{value}', value)
                option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, option_xpath))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                self.driver.execute_script("arguments[0].click();", option)
                time.sleep(1)

                # Scroll down to the bottom of the page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            self.driver.execute_script("arguments[0].scrollIntoView(true);", entries_select)
            self.driver.execute_script("arguments[0].click();", entries_select)
            option_xpath = config['DEFAULT']['entries_option_xpath'].replace('{value}', '5')
            option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
            self.driver.execute_script("arguments[0].click();", option)
            time.sleep(1)

            rows = self.driver.find_elements(By.XPATH, config['DEFAULT']['last_row_xpath'])
            self.assertEqual(len(rows), min(5, len(rows)))
        except Exception as e:
            self.fail(f"Error during entries per page test: {e}")
            
           

    def test_view_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'customerwise_and_hqwise_report_url'))
            time.sleep(1)  # Wait for the page to load
            self.test_select_customer()
 
            self.wait_and_click(config.get('DEFAULT', 'view_button_xpath'))
            time.sleep(1)            

            Name_as_per_records_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_records_field_xpath'))

            Name_as_per_convenience_field = self.wait_and_find(config.get('DEFAULT', 'Name_as_per_convenience_xpath'))

            Mobile_Number_field = self.wait_and_find(config.get('DEFAULT', 'Mobile_Number_xpath'))

            Mode_Of_Business_field = self.wait_and_find(config.get('DEFAULT', 'Mode_Of_Business_xpath'))

            Business_Set_Start_Date_field = self.wait_and_find(config.get('DEFAULT', 'Business_Set_Start_Date_xpath'))
 
            Business_Set_End_Date_field = self.wait_and_find(config.get('DEFAULT', 'Business_Set_End_Date_xpath'))
            
            Reward_Points_Percentage_field = self.wait_and_find(config.get('DEFAULT', 'Reward_Points_Percentage_xpath')) 

            Supplied_Item_Credit_Period_field= self.wait_and_find(config.get('DEFAULT', 'Supplied_Item_Credit_Period_xpath'))

            Billing_Name_field = self.wait_and_find(config.get('DEFAULT', 'Billing_Name_xpath'))
             
            Stockist_Name_field = self.wait_and_find(config.get('DEFAULT', 'Stockist_Name_xpath'))

            Target_Value_field = self.wait_and_find(config.get('DEFAULT', 'Target_Value_xpath'))
            
            Current_Sales_Value_field = self.wait_and_find(config.get('DEFAULT', 'Current_Sales_Value_xpath'))

            Balance_field = self.wait_and_find(config.get('DEFAULT', 'Balance_xpath'))

            Headquarter_field = self.wait_and_find(config.get('DEFAULT', 'Headquarter_xpath'))

            Mode_of_CRM_field= self.wait_and_find(config.get('DEFAULT', 'Mode_of_CRM_xpath'))

            assert Name_as_per_records_field.get_attribute("readonly") == "true", "customer field is editable"
            assert Name_as_per_convenience_field.get_attribute("readonly") == "true", "Name as per convenience field is editable"
            assert Mobile_Number_field.get_attribute("readonly") == "true", "Mobile Number field is editable"
            assert Mode_Of_Business_field.get_attribute("readonly") == "true", "Speciality field is editable"
            assert Business_Set_Start_Date_field.get_attribute("readonly") == "true", "Mobile Number field is editable"
            assert Business_Set_End_Date_field.get_attribute("readonly") == "true", "Birth Date field is editable"
            assert Supplied_Item_Credit_Period_field.get_attribute("readonly") == "true", "Wedding Date field is editable"
            assert Billing_Name_field.get_attribute("readonly") == "true", "Mode of CRM field is editable"
            assert Stockist_Name_field.get_attribute("readonly") == "true", "Reward Status field is editable"
            assert Target_Value_field.get_attribute("readonly") == "true", "customer field is editable"
            assert Current_Sales_Value_field.get_attribute("readonly") == "true", "Name as per convenience field is editable"
            assert Reward_Points_Percentage_field.get_attribute("readonly") == "true", "Birth Date field is editable"
            assert Balance_field.get_attribute("readonly") == "true", "Wedding Date field is editable"
            assert Headquarter_field.get_attribute("readonly") == "true", "Mode of CRM field is editable"
            assert Mode_of_CRM_field.get_attribute("readonly") == "true", "Reward Status field is editable"

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

    suite = unittest.TestLoader().loadTestsFromTestCase(customerwiseandhqwisereport)
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
    test_instance = customerwiseandhqwisereport()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
        try:
            test_instance.test_view_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_view_customer - {e}")
            failed_tests += 1

        try:
            test_instance.test_select_headquarters()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_select_headquarters - {e}")
            failed_tests += 1

        try:
            test_instance.test_select_customer()
            passed_tests += 1
        except Exception as e:
            print(f"Test failed: test_select_customer - {e}")
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