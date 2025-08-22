#!/usr/bin/env python3
"""
Test actual expense ratio fetching for Quant ELSS
"""

import requests
import re
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_quant_elss_expense():
    """Test expense ratio fetching for Quant ELSS"""
    scheme_code = "120847"  # Quant ELSS Direct Growth
    fund_name = "quant ELSS Tax Saver Fund - Growth Option - Direct Plan"
    
    print(f"🧪 Testing expense ratio for: {fund_name}")
    print(f"Scheme Code: {scheme_code}")
    print("=" * 80)
    
    # 1. Test Quant Mutual website
    print("\n🔍 Testing Quant Mutual website...")
    try:
        # Try different URL patterns for Quant
        quant_urls = [
            "https://www.quantmutual.com/funds/equity-funds/quant-elss-tax-saver-fund",
            "https://www.quantmutual.com/funds/elss/quant-elss-tax-saver-fund",
            "https://www.quantmutual.com/scheme-information",
            "https://www.quantmutual.com/fund-performance"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for url in quant_urls:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                print(f"  {url}: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Save content for analysis
                    filename = url.split('/')[-1] or 'index'
                    with open(f"quant_{filename}.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"    ✅ Saved content to quant_{filename}.html")
                    
                    # Look for expense ratio
                    expense_patterns = [
                        r'expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                        r'total\s*expense\s*ratio[:\s]*(\d+\.?\d*)%?',
                        r'ter[:\s]*(\d+\.?\d*)%?',
                        r'(\d+\.?\d*)%?\s*expense\s*ratio',
                        r'ongoing\s*charges[:\s]*(\d+\.?\d*)%?',
                        r'management\s*fee[:\s]*(\d+\.?\d*)%?'
                    ]
                    
                    for pattern in expense_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"    📈 Pattern '{pattern}' found: {matches}")
                            
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Quant website error: {e}")
    
    # 2. Test BSE/NSE data
    print("\n🔍 Testing BSE/NSE sources...")
    try:
        # BSE mutual fund data
        bse_url = f"https://www.bseindia.com/mf/fund-information.aspx?FundId={scheme_code}"
        response = requests.get(bse_url, headers=headers, timeout=15)
        print(f"  BSE MF page: {response.status_code}")
        
        if response.status_code == 200:
            print("    ✅ BSE accessible - might contain fund data")
            
    except Exception as e:
        print(f"    ❌ BSE Error: {e}")
    
    # 3. Test SEBI/regulatory filings
    print("\n🔍 Testing regulatory sources...")
    try:
        # SEBI SCORES or fund disclosures
        search_terms = [
            f"quant+elss+expense+ratio",
            f"quant+mutual+fund+{scheme_code}+expense"
        ]
        
        for term in search_terms:
            regulatory_search = f"https://www.google.com/search?q=site:sebi.gov.in+OR+site:amfiindia.com+{term}+filetype:pdf"
            print(f"    🔍 Regulatory search: {regulatory_search}")
    
    except Exception as e:
        print(f"    ❌ Regulatory search error: {e}")
    
    # 4. Test annual reports
    print("\n🔍 Testing annual report sources...")
    try:
        # Annual reports often contain detailed expense information
        report_urls = [
            "https://www.quantmutual.com/downloads/annual-reports",
            "https://www.quantmutual.com/downloads",
            "https://www.quantmutual.com/investor-services"
        ]
        
        for url in report_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"    {url}: {response.status_code}")
                if response.status_code == 200:
                    print(f"      ✅ Accessible - might contain annual reports")
            except:
                print(f"    ❌ Not accessible: {url}")
                
    except Exception as e:
        print(f"    ❌ Annual report error: {e}")

if __name__ == "__main__":
    test_quant_elss_expense()
