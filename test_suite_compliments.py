import unittest
import time
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from compliment_issue_tracking_customer import complimentissuecustomer
from compliment_issue_tracking_chemist import complimentissuechemist



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
        print(f"Test failed: {test._testMethodName} functionality did not work")

    def addError(self, test, err):
        super().addError(test, err)
        self.error_messages[test] = self._exc_info_to_string(err, test)
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

        self.send_email(report, report_path)
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
                </tr>
        """

        for test, _ in result.failures + result.errors:
            if isinstance(test, unittest.TestCase):
                test_class = test.__class__.__name__
                test_name = test._testMethodName
                test_time = result.test_times.get(test, "N/A")
                screenshot_path = f"screenshots/{test_name}.png"  # Define screenshot_path here
            
                report += f"""
                    <tr class="failed">
                        <td>{test_class}</td>
                        <td>{test_name}</td>
                        <td>{test_time:.2f}</td>
                        <td>Failed</td>
                
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
                </tr>
            """

        report += """
            </table>
        </body>
        </html>
        """
        return report

    def send_email(self, report_content, report_path):
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

        # Create SMTP session for sending the mail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable security
            server.login(from_email, "cmnjixovamtjfinc")  # Login with your email and password
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)


# Create a test suite combining all test cases
suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(complimentissuecustomer))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(complimentissuechemist))



# Run the test suite and generate a custom HTML report
runner = CustomHTMLTestRunner(output='test_reports', report_name='CustomTestReport')
runner.run(suite)