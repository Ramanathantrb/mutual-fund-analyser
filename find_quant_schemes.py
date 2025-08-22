#!/usr/bin/env python3
"""
Find Quant ELSS Tax Saver scheme code and test expense ratio sources
"""

import requests
import re
import urllib3
from src.data.amfi_fund_fetcher import AMFIFundFetcher

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_quant_elss():
    """Find Quant ELSS Tax Saver scheme code"""
    print("🔍 Finding Quant ELSS Tax Saver scheme...")
    
    fetcher = AMFIFundFetcher()
    schemes = fetcher.fetch_all_schemes()
    
    quant_schemes = []
    for scheme in schemes:
        if 'quant' in scheme['scheme_name'].lower() and 'elss' in scheme['scheme_name'].lower():
            quant_schemes.append(scheme)
    
    print(f"Found {len(quant_schemes)} Quant ELSS schemes:")
    for scheme in quant_schemes:
        print(f"  Code: {scheme['scheme_code']} - {scheme['scheme_name']}")
    
    return quant_schemes

def test_alternative_sources(scheme_code, scheme_name):
    """Test alternative expense ratio sources"""
    print(f"\n🧪 Testing alternative sources for: {scheme_name}")
    print(f"Code: {scheme_code}")
    
    # 1. Try MF API with more details
    print("\n🔍 Testing MF API for detailed info...")
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url, timeout=15, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MF API Response keys: {list(data.keys())}")
            # Check if meta data has expense info
            if 'meta' in data:
                print(f"Meta keys: {list(data['meta'].keys()) if isinstance(data['meta'], dict) else data['meta']}")
        else:
            print(f"❌ MF API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MF API Error: {e}")
    
    # 2. Try mutual fund fact sheet URLs
    print("\n🔍 Testing fact sheet sources...")
    
    # Extract AMC name for fact sheet search
    amc_name = scheme_name.split(' ')[0].lower()  # Usually first word
    
    fact_sheet_urls = [
        f"https://www.axismf.com/docs/default-source/fact-sheets/{scheme_name.replace(' ', '-').lower()}.pdf",
        f"https://www.quantmutual.com/downloads/factsheets/{scheme_name.replace(' ', '-').lower()}.pdf",
        f"https://www.sbimf.com/Docs/FactSheet/{scheme_name.replace(' ', '_')}.pdf"
    ]
    
    for url in fact_sheet_urls:
        try:
            response = requests.head(url, timeout=10)
            print(f"Fact sheet {url}: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Found fact sheet: {url}")
        except:
            print(f"❌ Fact sheet not found: {url}")
    
    # 3. Try RTA (Registrar and Transfer Agent) data
    print("\n🔍 Testing RTA sources...")
    
    # CAMS, Karvy, etc. might have expense data
    try:
        # Some funds publish data on their websites
        search_terms = [
            scheme_name.replace(' ', '+'),
            scheme_code
        ]
        
        for term in search_terms:
            google_search = f"https://www.google.com/search?q=\"{term}\"+expense+ratio+filetype:pdf"
            print(f"🔍 Google search: {google_search}")
            
    except Exception as e:
        print(f"❌ Search Error: {e}")

if __name__ == "__main__":
    # Find Quant ELSS schemes
    quant_schemes = find_quant_elss()
    
    # Test with found Quant schemes
    for scheme in quant_schemes[:2]:  # Test first 2
        test_alternative_sources(scheme['scheme_code'], scheme['scheme_name'])
        print("\n" + "="*60)
