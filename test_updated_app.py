#!/usr/bin/env python3
"""
Test script to verify the updated expense ratio functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the expense ratio functions from app.py
from app import get_actual_expense_with_database

def test_expense_ratios():
    """Test the expense ratio functionality with known funds"""
    
    test_funds = [
        "Quant ELSS Tax Saver Fund - Direct Plan - Growth",
        "Axis ELSS Tax Saver Fund - Direct Plan - Growth", 
        "Mirae Asset ELSS Tax Saver Fund - Direct Plan - Growth",
        "SBI Small Cap Fund - Direct Plan - Growth",
        "HDFC Small Cap Fund - Direct Plan - Growth",
        "Some Unknown Fund Name"  # Should return None
    ]
    
    print("Testing Expense Ratio Database:")
    print("=" * 50)
    
    for fund_name in test_funds:
        expense_ratio = get_actual_expense_with_database(fund_name)
        if expense_ratio:
            print(f"✓ {fund_name[:50]}...")
            print(f"  → Actual Expense Ratio: {expense_ratio}%")
        else:
            print(f"* {fund_name[:50]}...")
            print(f"  → No actual data (will show estimated)")
        print()

if __name__ == "__main__":
    test_expense_ratios()
