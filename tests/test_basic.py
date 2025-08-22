"""
Basic tests for AMFI Mutual Fund Analyzer
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAMFIAnalyzer(unittest.TestCase):
    """Basic test cases for the AMFI analyzer"""
    
    def test_import_data_module(self):
        """Test if data module can be imported"""
        try:
            from data.amfi_fund_fetcher import AMFIFundFetcher
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import AMFIFundFetcher")
    
    def test_import_analyzers_module(self):
        """Test if analyzers module can be imported"""
        try:
            from analyzers.expense_analyzer import ExpenseAnalyzer
            self.assertTrue(True)
        except ImportError:
            self.fail("Could not import ExpenseAnalyzer")
    
    def test_amfi_fetcher_initialization(self):
        """Test AMFI fetcher initialization"""
        try:
            from data.amfi_fund_fetcher import AMFIFundFetcher
            fetcher = AMFIFundFetcher()
            self.assertIsNotNone(fetcher)
            self.assertTrue(hasattr(fetcher, 'fetch_all_schemes'))
        except Exception as e:
            self.fail(f"AMFI fetcher initialization failed: {e}")
    
    def test_expense_analyzer_initialization(self):
        """Test expense analyzer initialization"""
        try:
            from analyzers.expense_analyzer import ExpenseAnalyzer
            analyzer = ExpenseAnalyzer()
            self.assertIsNotNone(analyzer)
            self.assertTrue(hasattr(analyzer, 'categorize_fund_type'))
        except Exception as e:
            self.fail(f"Expense analyzer initialization failed: {e}")

if __name__ == '__main__':
    unittest.main()
