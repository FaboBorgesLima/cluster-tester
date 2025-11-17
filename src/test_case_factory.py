from test_case import TestCase

class TestCaseFactory:
    @staticmethod
    def create_test_case(app_url:str,test_case:str)->TestCase:
        match test_case:
            case "fibonacci" | "FibonacciTestCase":
                from fibonacci_test import FibonacciTest
                return FibonacciTest(application_base_url=app_url)
            case "bubble-sort" | "BubbleSortTestCase":
                from bubble_sort_test import BubbleSortTest
                return BubbleSortTest(application_base_url=app_url)
            case _:
                raise ValueError(f"Unknown test case: {test_case}. Supported cases are: fibonacci, bubble-sort.")