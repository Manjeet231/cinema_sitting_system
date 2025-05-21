import unittest
import sys
import os

# Add the tests directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test modules
from test_seating_algorithm import TestSeatingAlgorithm
from test_seating_algorithm_js import TestSeatingAlgorithmJS

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add tests from TestSeatingAlgorithm
    test_suite.addTest(unittest.makeSuite(TestSeatingAlgorithm))
    
    # Add tests from TestSeatingAlgorithmJS
    test_suite.addTest(unittest.makeSuite(TestSeatingAlgorithmJS))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
