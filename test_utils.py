# test_utils.py

def order(index):
    def decorator(func):
        func._order = index
        return func
    return decorator

import unittest

class OrderedTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        # Get the test method names
        test_names = super().getTestCaseNames(testCaseClass)
        # Order the test methods based on the custom order attribute
        test_names.sort(key=lambda name: getattr(getattr(testCaseClass, name), '_order', 0))
        return test_names