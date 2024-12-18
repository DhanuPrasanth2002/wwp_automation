import unittest
import time
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# from user import userTests
# from speciality import specialityTests
# from cus_che import CusCheListTests
# from product import productTests
# from billingName import billingTests
# from stockist import stockistTests
# from headquarters import HeadquartersTests
# from territory import territoryTests
# from rep import repTests

# from rep_hq_territory_config import RepHqTerritoryConfigTests
# from business_set_config_customer import businesssetconfigcustomer
# from business_set_config_chemist import businesssetconfigchemist
# from customer_configuration_master import customerconfigmaster
# from chemist_configuration_master import chemistconfigmaster
# from bill_name_and_Stockist_config import billnameandstockistconfig
# from bill_customer_and_product_config import billcustomerandproductconfig
# from bill_chemist_and_product_config import billchemistandproductconfig

# from sales_entry import sales_entry

# from reward_payment_recommendation_customer import reward_payment_recommendation_customer
# from reward_payment_recommendation_chemist import reward_payment_recommendation_chemist
# from reward_recommendation_tracking_customer import reward_recommendation_tracking_customer
# from reward_recommendation_tracking_chemist import reward_recommendation_tracking_chemist

# from compliment_issue_tracking_customer import complimentissuecustomer
# from compliment_issue_tracking_chemist import complimentissuechemist

# from sales_slip import saleslip
# from sales_slip_chemist import saleslipchemist
# from customer_hqwise_report import hqwisereport
# from chemist_hqwise_report import chemisthqwisereport
# from customerwise_businessset_report import businesssetreport
# from chemistwise_businessset import chebusinesssetreport
# from customerwise_and_hqwise_report import customerwiseandhqwisereport
from chemistwise_and_hqwise_report import chemistwiseandhqwisereport
# from monthwise_sales_and_hqwise_report import monthwisesalesandhqwisereport
# from monthwise_sales_and_hqwise_chereport import monthwisesalesandhqwisechereport
# from non_supporting_customer_list import non_supporting_customer_list
# from non_supporting_chemist import non_supporting_chemist_list
# from reward_distribution_customer import reward_distribution_customer
# from reward_distribution_chemist import reward_distribution_chemist
# from compliment_report_customer import complimentreportcustomer
# from compliment_report_chemist import complimentreportchemist



def order(index):
    def decorator(func):
        func._order = index
        return func
    return decorator

class OrderedTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        # Get the test method names
        test_names = super().getTestCaseNames(testCaseClass)
        # Order the test methods based on the custom order attribute
        test_names.sort(key=lambda name: getattr(getattr(testCaseClass, name), '_order', 0))
        return test_names



class CustomTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
        self.test_times = {}  # Initialize test_times attribute
        self.error_messages = {}  # Initialize error_messages attribute
        self.screenshots = {}  # Initialize screenshots attribute

    def startTest(self, test):
        super().startTest(test)
        self.test_times[test] = time.time()

    def stopTest(self, test):
        self.test_times[test] = time.time() - self.test_times[test]
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)
        self.test_times[test] = time.time() - self.test_times[test]
        print(f"Test passed: {test._testMethodName} functionality worked")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.error_messages[test] = self._exc_info_to_string(err, test)
        self.capture_screenshot(test)
        print(f"Test failed: {test._testMethodName} functionality did not work")

    def addError(self, test, err):
        super().addError(test, err)
        self.error_messages[test] = self._exc_info_to_string(err, test)
        self.capture_screenshot(test)
        print(f"Test error: {test._testMethodName} encountered an error")

    def capture_screenshot(self, test):
        screenshot_dir = "test_reports/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"{test.id()}.png")
        try:
            if hasattr(test, 'driver'):
                test.driver.save_screenshot(screenshot_path)
            self.screenshots[test] = screenshot_path
        except Exception as e:
            print(f"Failed to take screenshot for {test.id()}: {e}")

class CustomHTMLTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        self.output = kwargs.pop('output', 'test_reports')
        self.report_name = kwargs.pop('report_name', 'CustomTestReport')
        super().__init__(*args, **kwargs)

    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        start_time = time.time()
        result = super().run(test)
        end_time = time.time()
        execution_time = end_time - start_time

        report = self.generate_report(result, start_time, end_time, execution_time)
        report_path = f"{self.output}/{self.report_name}.html"
        with open(report_path, "w") as f:
            f.write(report)

        self.send_email(report, report_path,result)
        return result

    def generate_report(self, result, start_time, end_time, execution_time):
        start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))

        total_tests = result.testsRun
        total_failures = len(result.failures)
        total_errors = len(result.errors)
        total_passed = len(result.successes)
        total_failed = total_failures + total_errors

        report = f"""
        <html>
        <head>
            <title>Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; }}
                .summary {{ background-color: #007bff; color: white; padding: 20px; border-radius: 5px; }}
                .summary h1 {{ margin-top: 0; }}
                .summary p {{ margin: 5px 0; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #007bff; color: white; }}
            </style>
        </head>
        <body>
            <div class="summary">
                <h1>WWP Test Suite Report</h1>
                <p><strong>Start Time:</strong> {start_time_str}</p>
                <p><strong>End Time:</strong> {end_time_str}</p>
                <p><strong>Total Execution Time:</strong> {execution_time:.2f} seconds</p>
                <p><strong>Overall Status:</p></strong> 
                <p><strong>Total test cases: {total_tests}</p> </strong> 
                <p><strong>Passed: {total_passed} </p></strong> 
                <p><strong>Failed: {total_failed}</p></strong> 
            </div>
            <h2>Test Case Details</h2>
            <table>
                <tr>
                    <th>Test Class</th>
                    <th>Test Case</th>
                    <th>Execution Time (seconds)</th>
                    <th>Status</th>
                    <th>Screenshot</th>
                </tr>
        """

        for test, _ in result.failures + result.errors:
            if isinstance(test, unittest.TestCase):
                test_class = test.__class__.__name__
                test_name = test._testMethodName
                test_time = result.test_times.get(test, "N/A")
                screenshot_path = result.screenshots.get(test, "N/A")
                screenshot_html = f'<a href="file:///{os.path.abspath(screenshot_path)}">View Screenshot</a>' if screenshot_path != "N/A" else "N/A"
                report += f"""
                    <tr class="failed">
                        <td>{test_class}</td>
                        <td>{test_name}</td>
                        <td>{test_time:.2f}</td>
                        <td>Failed </td>
                        <td>{screenshot_html}</td>
                    </tr>
                """
            else:
                report += f"""
                    <tr class="failed">
                        <td colspan="5">Error in test setup/teardown</td>
                    </tr>
                """

        for test in result.successes:
            test_class = test.__class__.__name__
            test_name = test._testMethodName
            test_time = result.test_times.get(test, "N/A")
            report += f"""
                <tr class="passed">
                    <td>{test_class}</td>
                    <td>{test_name}</td>
                    <td>{test_time:.2f}</td>
                    <td>Passed</td>
                    <td>N/A</td>
                </tr>
            """

        report += """


        
            </table>
        </body>
        </html>
        """
        return report
    
    

    def send_email(self, report_content, report_path,result):
        from_email = "prasandhanu2002@gmail.com"
        to_email = ["jshri.redmind@gmail.com","dhanuprasanth80@gmail.com"]
        cc_email = ""  # Add email addresses separated by commas
        subject = "WWP UI Test Suite Execution Report"
        body = report_content

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join( to_email)  # Join the list of emails into a comma-separated 
        msg['Cc'] = cc_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'html'))

        # Open the file to be sent
        with open(report_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {report_path}")

            # Attach the instance 'part' to instance 'msg'
            msg.attach(part)

        # Attach screenshots
        for test, screenshot_path in result.screenshots.items():
            if screenshot_path != "N/A":
                with open(screenshot_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(screenshot_path)}")
                    msg.attach(part)



        # Create SMTP session for sending the mail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable security
            server.login(from_email, "bwevzjjbkneullei")  # Login with your email and password
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)


# Create a test suite combining all test cases
suite = unittest.TestSuite()
loader = OrderedTestLoader()


# suite.addTests(loader.loadTestsFromTestCase(userTests))
# suite.addTests(loader.loadTestsFromTestCase(specialityTests))
# suite.addTests(loader.loadTestsFromTestCase(CusCheListTests))
# suite.addTests(loader.loadTestsFromTestCase(productTests))
# suite.addTests(loader.loadTestsFromTestCase(billingTests))
# suite.addTests(loader.loadTestsFromTestCase(stockistTests))
# suite.addTests(loader.loadTestsFromTestCase(HeadquartersTests))
# suite.addTests(loader.loadTestsFromTestCase(territoryTests))
# suite.addTests(loader.loadTestsFromTestCase(repTests))

# suite.addTests(loader.loadTestsFromTestCase(RepHqTerritoryConfigTests))
# suite.addTests(loader.loadTestsFromTestCase(businesssetconfigcustomer))
# suite.addTests(loader.loadTestsFromTestCase(businesssetconfigchemist))
# suite.addTests(loader.loadTestsFromTestCase(customerconfigmaster))
# suite.addTests(loader.loadTestsFromTestCase(chemistconfigmaster))
# suite.addTests(loader.loadTestsFromTestCase(billnameandstockistconfig))
# suite.addTests(loader.loadTestsFromTestCase(billcustomerandproductconfig))
# suite.addTests(loader.loadTestsFromTestCase(billchemistandproductconfig))

# suite.addTests(loader.loadTestsFromTestCase(sales_entry))


# suite.addTests(loader.loadTestsFromTestCase(reward_payment_recommendation_customer))
# suite.addTests(loader.loadTestsFromTestCase(reward_payment_recommendation_chemist))
# suite.addTests(loader.loadTestsFromTestCase(reward_recommendation_tracking_customer))
# suite.addTests(loader.loadTestsFromTestCase(reward_recommendation_tracking_chemist))

# suite.addTests(loader.loadTestsFromTestCase(complimentissuecustomer))
# suite.addTests(loader.loadTestsFromTestCase(complimentissuechemist))

# suite.addTests(loader.loadTestsFromTestCase(saleslip))
# suite.addTests(loader.loadTestsFromTestCase(saleslipchemist))
# suite.addTests(loader.loadTestsFromTestCase(hqwisereport))
# suite.addTests(loader.loadTestsFromTestCase(chemisthqwisereport))
# suite.addTests(loader.loadTestsFromTestCase(businesssetreport))
# suite.addTests(loader.loadTestsFromTestCase(chebusinesssetreport))
# suite.addTests(loader.loadTestsFromTestCase(customerwiseandhqwisereport))
suite.addTests(loader.loadTestsFromTestCase(chemistwiseandhqwisereport))
# suite.addTests(loader.loadTestsFromTestCase(monthwisesalesandhqwisereport))
# suite.addTests(loader.loadTestsFromTestCase(monthwisesalesandhqwisechereport))
# suite.addTests(loader.loadTestsFromTestCase(non_supporting_customer_list))
# suite.addTests(loader.loadTestsFromTestCase(non_supporting_chemist_list))
# suite.addTests(loader.loadTestsFromTestCase(reward_distribution_customer))
# suite.addTests(loader.loadTestsFromTestCase(reward_distribution_chemist))
# suite.addTests(loader.loadTestsFromTestCase(complimentreportcustomer))
# suite.addTests(loader.loadTestsFromTestCase(complimentreportchemist))




# Run the test suite and generate a custom HTML report
runner = CustomHTMLTestRunner(output='test_reports', report_name='CustomTestReport')
runner.run(suite)