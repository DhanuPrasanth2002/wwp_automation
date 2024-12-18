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


# Read properties from config file
config = configparser.ConfigParser()
config.read('sales_slip.ini')

class saleslip(unittest.TestCase):

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


    def test_select_customer(self):
        try:
            self.driver.get(config.get('DEFAULT', 'sales_slip_customer_url'))
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
             
            self.driver.get(config.get('DEFAULT', 'sales_slip_customer_url'))
            self.test_select_customer()
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
            self.driver.get(config.get('DEFAULT', 'sales_slip_customer_url'))
            self.test_select_customer()
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

    suite = unittest.TestLoader().loadTestsFromTestCase(saleslip)
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
    test_instance = saleslip()

    # Counters for passed and failed tests
    passed_tests = 0
    failed_tests = 0

    # Manually call the test functions in the desired order
    test_instance.setUpClass()
    try:
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

    finally:
        test_instance.tearDownClass()

    # Print the summary of test results
    print(f"Tests run: {passed_tests + failed_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")