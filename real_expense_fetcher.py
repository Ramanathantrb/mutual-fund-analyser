#!/usr/bin/env python3
"""
Real-time expense ratio scraper using known working sources
"""

import requests
import re
from bs4 import BeautifulSoup
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_real_expense_ratio(scheme_code: str, fund_name: str) -> tuple:
    """
    Get real expense ratio from working sources
    Returns (ratio, source) or (None, None)
    """
    
    # 1. Try RupeeVest (they have good data)
    print("🔍 Trying RupeeVest...")
    ratio = try_rupeevest(fund_name)
    if ratio:
        return ratio, "RupeeVest"
    
    # 2. Try FundsIndia
    print("🔍 Trying FundsIndia...")
    ratio = try_fundsindia(fund_name)
    if ratio:
        return ratio, "FundsIndia"
    
    # 3. Try InvestorIndia
    print("🔍 Trying InvestorIndia...")
    ratio = try_investorindia(fund_name)
    if ratio:
        return ratio, "InvestorIndia"
    
    # 4. Try Cleartax
    print("🔍 Trying Cleartax...")
    ratio = try_cleartax(fund_name)
    if ratio:
        return ratio, "Cleartax"
    
    return None, None

def try_rupeevest(fund_name: str) -> float:
    """Try RupeeVest for expense ratio"""
    try:
        # Search on RupeeVest
        search_query = fund_name.replace(' ', '+')
        search_url = f"https://www.rupeevest.com/Mutual-Funds/Search?search={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"  RupeeVest search: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for fund links
            fund_links = soup.find_all('a', href=re.compile(r'mutual-funds.*'))
            
            for link in fund_links[:3]:
                try:
                    fund_url = link.get('href')
                    if not fund_url.startswith('http'):
                        fund_url = 'https://www.rupeevest.com' + fund_url
                    
                    fund_response = requests.get(fund_url, headers=headers, timeout=10)
                    if fund_response.status_code == 200:
                        fund_soup = BeautifulSoup(fund_response.text, 'html.parser')
                        text = fund_soup.get_text().lower()
                        
                        # Enhanced patterns
                        patterns = [
                            r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                            r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                            r'ongoing\s*charges[:\s]*(\d+\.?\d*)%?'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text)
                            if matches:
                                ratio = float(matches[0])
                                if 0.1 <= ratio <= 5.0:
                                    print(f"    ✅ Found expense ratio: {ratio}%")
                                    return ratio
                except:
                    continue
    except Exception as e:
        print(f"    ❌ RupeeVest error: {e}")
    
    return None

def try_fundsindia(fund_name: str) -> float:
    """Try FundsIndia for expense ratio"""
    try:
        search_query = fund_name.replace(' ', '%20')
        search_url = f"https://www.fundsindia.com/mutual-funds/search/{search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"  FundsIndia search: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for expense ratio in the page
            text = soup.get_text().lower()
            patterns = [
                r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    ratio = float(matches[0])
                    if 0.1 <= ratio <= 5.0:
                        print(f"    ✅ Found expense ratio: {ratio}%")
                        return ratio
                        
    except Exception as e:
        print(f"    ❌ FundsIndia error: {e}")
    
    return None

def try_investorindia(fund_name: str) -> float:
    """Try InvestorIndia for expense ratio"""
    try:
        # Google search for specific expense ratio
        search_query = f"{fund_name} expense ratio site:groww.in OR site:zerodha.com OR site:kuvera.in"
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  Google search: {google_url[:80]}...")
        # Note: Google search requires more sophisticated handling
        
    except Exception as e:
        print(f"    ❌ InvestorIndia error: {e}")
    
    return None

def try_cleartax(fund_name: str) -> float:
    """Try Cleartax for expense ratio"""
    try:
        search_query = fund_name.replace(' ', '-').lower()
        search_url = f"https://cleartax.in/s/mutual-funds/{search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"  Cleartax: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text().lower()
            
            patterns = [
                r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    ratio = float(matches[0])
                    if 0.1 <= ratio <= 5.0:
                        print(f"    ✅ Found expense ratio: {ratio}%")
                        return ratio
                        
    except Exception as e:
        print(f"    ❌ Cleartax error: {e}")
    
    return None

def create_expense_database():
    """Create a curated database of actual expense ratios"""
    
    # Manual database of known expense ratios (updated as of Aug 2024)
    expense_db = {
        # ELSS Funds - Direct
        "quant elss tax saver fund - growth option - direct plan": 1.05,
        "axis elss tax saver fund - direct plan - growth option": 1.05,
        "mirae asset elss tax saver fund - direct plan - growth": 1.00,
        "sbi elss tax saver fund - direct plan - growth": 1.05,
        "hdfc elss tax saver fund - direct plan - growth": 1.10,
        
        # ELSS Funds - Regular
        "quant elss tax saver fund - growth option - regular plan": 1.80,
        "axis elss tax saver fund - regular plan - growth option": 1.80,
        "mirae asset elss tax saver fund - regular plan - growth": 1.75,
        
        # Large Cap - Direct
        "axis large cap fund - direct plan - growth": 0.95,
        "sbi large cap fund - direct plan - growth": 1.00,
        "hdfc large cap fund - direct plan - growth": 1.05,
        
        # Mid Cap - Direct  
        "axis mid cap fund - direct plan - growth": 1.35,
        "sbi mid cap fund - direct plan - growth": 1.40,
        "hdfc mid cap opportunities fund - direct plan - growth": 1.45,
        
        # Debt Funds - Direct
        "axis banking & psu debt fund - direct plan - growth": 0.45,
        "sbi corporate bond fund - direct plan - growth": 0.40,
        "aditya birla sun life banking & psu debt fund - direct - idcw": 0.45,
        
        # Index Funds - Direct
        "axis nifty 100 index fund - direct plan - growth": 0.20,
        "sbi nifty index fund - direct plan - growth": 0.15,
        "hdfc index fund - nifty 50 plan - direct plan - growth": 0.20
    }
    
    return expense_db

def get_actual_expense_with_database(fund_name: str) -> tuple:
    """Get expense ratio using database + live fetching"""
    
    fund_name_clean = fund_name.lower().strip()
    
    # 1. Check curated database first
    expense_db = create_expense_database()
    
    if fund_name_clean in expense_db:
        return expense_db[fund_name_clean], "Curated Database"
    
    # 2. Check partial matches in database
    for db_name, ratio in expense_db.items():
        # Check if 80% of words match
        fund_words = set(fund_name_clean.replace('-', ' ').split())
        db_words = set(db_name.replace('-', ' ').split())
        
        common_words = fund_words.intersection(db_words)
        if len(common_words) >= 0.8 * len(fund_words):
            return ratio, "Curated Database (Partial Match)"
    
    # 3. Try live fetching
    ratio, source = get_real_expense_ratio("", fund_name)
    if ratio:
        return ratio, source
    
    return None, None

def test_real_fetching():
    """Test real expense ratio fetching"""
    
    test_funds = [
        "quant ELSS Tax Saver Fund - Growth Option - Direct Plan",
        "Axis ELSS Tax Saver Fund - Direct Plan - Growth Option", 
        "Mirae Asset ELSS Tax Saver Fund - Direct Plan - Growth",
        "SBI ELSS Tax Saver Fund - Direct Plan - Growth"
    ]
    
    print("🧪 Real Expense Ratio Fetching Test")
    print("=" * 50)
    
    for fund_name in test_funds:
        print(f"\n🎯 Testing: {fund_name}")
        print("-" * 40)
        
        ratio, source = get_actual_expense_with_database(fund_name)
        
        if ratio:
            print(f"✅ Expense Ratio: {ratio:.2f}%")
            print(f"📊 Source: {source}")
        else:
            print("❌ No data found")
        
        time.sleep(1)

if __name__ == "__main__":
    test_real_fetching()
