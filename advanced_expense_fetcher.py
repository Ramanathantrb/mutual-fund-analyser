#!/usr/bin/env python3
"""
Advanced expense ratio fetching using multiple sophisticated sources
"""

import requests
import re
import json
from bs4 import BeautifulSoup
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_actual_expense_ratio_advanced(scheme_code: str, fund_name: str) -> tuple:
    """
    Advanced expense ratio fetching with multiple sources
    Returns (expense_ratio, source, confidence)
    """
    
    print(f"🔍 Advanced search for {fund_name} (Code: {scheme_code})")
    
    # 1. Try MorningStar India API (they have comprehensive data)
    print("📊 Trying MorningStar India...")
    morningstar_ratio = try_morningstar_api(fund_name)
    if morningstar_ratio:
        return morningstar_ratio, "MorningStar", "high"
    
    # 2. Try Value Research API/scraping
    print("📈 Trying Value Research...")
    vr_ratio = try_value_research(fund_name)
    if vr_ratio:
        return vr_ratio, "Value Research", "high"
    
    # 3. Try MoneyControl detailed scraping
    print("💰 Trying MoneyControl...")
    mc_ratio = try_moneycontrol_detailed(fund_name)
    if mc_ratio:
        return mc_ratio, "MoneyControl", "medium"
    
    # 4. Try ET Money API
    print("📱 Trying ET Money...")
    et_ratio = try_et_money(fund_name, scheme_code)
    if et_ratio:
        return et_ratio, "ET Money", "medium"
    
    # 5. Try Groww API (they have good MF data)
    print("🌱 Trying Groww...")
    groww_ratio = try_groww_api(fund_name, scheme_code)
    if groww_ratio:
        return groww_ratio, "Groww", "medium"
    
    # 6. Try official AMC annual reports
    print("📋 Trying AMC Annual Reports...")
    amc_ratio = try_amc_annual_reports(fund_name)
    if amc_ratio:
        return amc_ratio, "AMC Annual Report", "high"
    
    return None, "None", "none"

def try_morningstar_api(fund_name: str) -> float:
    """Try MorningStar India for expense ratio"""
    try:
        # MorningStar search API
        search_url = "https://www.morningstar.in/api/search/security"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        params = {
            'q': fund_name,
            'limit': 5,
            'type': 'fund'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                # Get first result and try to fetch detailed data
                fund_id = data['results'][0].get('id')
                if fund_id:
                    detail_url = f"https://www.morningstar.in/api/fund/{fund_id}/details"
                    detail_response = requests.get(detail_url, headers=headers, timeout=10)
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        expense_ratio = detail_data.get('expenseRatio')
                        if expense_ratio:
                            return float(expense_ratio)
    except:
        pass
    return None

def try_value_research(fund_name: str) -> float:
    """Try Value Research for expense ratio"""
    try:
        # Value Research search
        search_url = "https://www.valueresearchonline.com/api/search"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        params = {'q': fund_name}
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('funds'):
                fund_id = data['funds'][0].get('id')
                if fund_id:
                    # Get fund details
                    detail_url = f"https://www.valueresearchonline.com/api/fund/{fund_id}"
                    detail_response = requests.get(detail_url, headers=headers, timeout=10)
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        expense_ratio = detail_data.get('expense_ratio')
                        if expense_ratio:
                            return float(expense_ratio)
    except:
        pass
    return None

def try_moneycontrol_detailed(fund_name: str) -> float:
    """Detailed MoneyControl scraping"""
    try:
        # Search on MoneyControl
        search_url = "https://www.moneycontrol.com/mutual-funds/mf_search_result.php"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {'search': fund_name}
        response = requests.get(search_url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for fund links
            fund_links = soup.find_all('a', href=re.compile(r'/mutual-funds/.*'))
            
            for link in fund_links[:3]:  # Check first 3 results
                fund_url = "https://www.moneycontrol.com" + link.get('href')
                fund_response = requests.get(fund_url, headers=headers, timeout=10)
                
                if fund_response.status_code == 200:
                    fund_soup = BeautifulSoup(fund_response.text, 'html.parser')
                    
                    # Look for expense ratio in various patterns
                    text = fund_soup.get_text().lower()
                    patterns = [
                        r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                        r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                        r'ter[:\s]*(\d+\.?\d*)%?'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, text)
                        if matches:
                            try:
                                ratio = float(matches[0])
                                if 0.1 <= ratio <= 5.0:  # Sanity check
                                    return ratio
                            except:
                                continue
    except:
        pass
    return None

def try_et_money(fund_name: str, scheme_code: str) -> float:
    """Try ET Money API"""
    try:
        # ET Money search API
        search_url = "https://web-api.etmoney.com/mutual-funds/search"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        params = {'q': fund_name}
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                fund_data = data['data'][0]
                expense_ratio = fund_data.get('expenseRatio')
                if expense_ratio:
                    return float(expense_ratio)
    except:
        pass
    return None

def try_groww_api(fund_name: str, scheme_code: str) -> float:
    """Try Groww API"""
    try:
        # Groww search API
        search_url = "https://groww.in/v1/api/search/v2/derive/query"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        params = {
            'q': fund_name,
            'type': 'mf'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('content'):
                for fund in data['content']:
                    if fund.get('expense_ratio'):
                        return float(fund['expense_ratio'])
    except:
        pass
    return None

def try_amc_annual_reports(fund_name: str) -> float:
    """Try to find expense ratio in AMC annual reports"""
    try:
        # Extract AMC name
        amc_name = fund_name.split(' ')[0].lower()
        
        # Known AMC annual report URLs
        report_urls = {
            'axis': 'https://www.axismf.com/investors-corner/annual-reports',
            'hdfc': 'https://www.hdfcfund.com/investor-services/investor-information/annual-reports',
            'sbi': 'https://www.sbimf.com/en-us/investor-services/annual-reports',
            'icici': 'https://www.icicipruamc.com/docs/default-source/annual-reports',
            'quant': 'https://www.quantmutual.com/downloads/annual-reports'
        }
        
        if amc_name in report_urls:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(report_urls[amc_name], headers=headers, timeout=15)
            if response.status_code == 200:
                # This would require PDF parsing which is complex
                # For now, just check if the page exists
                print(f"✅ Found {amc_name} annual reports page")
                # Could implement PDF downloading and parsing here
                return None
    except:
        pass
    return None

def test_advanced_fetching():
    """Test the advanced fetching system"""
    
    test_funds = [
        ("120847", "quant ELSS Tax Saver Fund - Growth Option - Direct Plan"),
        ("120503", "Axis ELSS Tax Saver Fund - Direct Plan - Growth Option"),
        ("119551", "Aditya Birla Sun Life Banking & PSU Debt Fund - DIRECT - IDCW")
    ]
    
    print("🧪 Advanced Expense Ratio Fetching Test")
    print("=" * 60)
    
    for scheme_code, fund_name in test_funds:
        print(f"\n🎯 Testing: {fund_name}")
        print("-" * 40)
        
        ratio, source, confidence = fetch_actual_expense_ratio_advanced(scheme_code, fund_name)
        
        if ratio:
            print(f"✅ Found: {ratio:.2f}%")
            print(f"📊 Source: {source}")
            print(f"🎯 Confidence: {confidence}")
        else:
            print("❌ No actual data found")
        
        print()
        time.sleep(2)  # Be respectful to APIs

if __name__ == "__main__":
    test_advanced_fetching()
