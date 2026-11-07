#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup

LANGS = ['fr', 'de', 'es', 'it', 'ja', 'nl', 'pl', 'ro']
BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

FORBIDDEN_ENGLISH_PHRASES = [
    # Founder & About section phrases
    "The Cruise Detective Leadership",
    "FIELD INVESTIGATORS",
    "Undercover River Audits",
    "40+ Cruises Tested",
    "Paris • Amsterdam • London",
    "Adam Dimitrov founded The Cruise Detective",
    "Having audited river cruises",
    "During multi-week tasting expeditions",
    "A river cruise is often the centerpiece",
    "Our job is to test the details in person",
    "Vacations Don't Have A Return Policy",
    "The Missing Safety Net",
    "The PR & Influencer Blindspot",
    "Blended Review Aggregation",
    "100% Out-of-Pocket Payment",
    "Zero Pay-for-Rank Placements",
    "Price-Transparency Anchoring",
    
    # Homepage phrases
    "Explore our testing methodology",
    "Personally tested undercover",
    "ALL RIGHTS RESERVED",
    "All rights reserved",
    "Undercover River Audits",
    
    # Guide phrases
    "Schedule & Frequency",
    "Ticket Format",
    "Dress Code",
    "Child Discounts",
    "Parking & Arrival",
    "Live Availability Confirmed",
    "Check Dates & Book Tickets",
    "Personally tested and verified",
    "Video Review & Onboard Atmosphere",
    "Live Singer",
]

def scan_all_pages():
    total_files = 0
    issues_found = 0
    
    for lang in LANGS:
        lang_dir = os.path.join(BASE_DIR, lang)
        if not os.path.exists(lang_dir):
            continue
            
        for root, dirs, files in os.walk(lang_dir):
            for file in files:
                if file.endswith('.html'):
                    total_files += 1
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, BASE_DIR)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Parse html and remove scripts/styles/JSON-LD for text checks
                    soup = BeautifulSoup(content, 'html.parser')
                    for s in soup(['script', 'style', 'noscript']):
                        s.decompose()
                        
                    visible_text = soup.get_text()
                    
                    for phrase in FORBIDDEN_ENGLISH_PHRASES:
                        # "Paris • Amsterdam • London" is identical in German
                        if lang == 'de' and phrase == "Paris • Amsterdam • London":
                            continue
                        if phrase in visible_text:
                            print(f"[UNTRANSLATED LEAK] {relpath} contains English phrase: '{phrase}'")
                            issues_found += 1
                            
    print(f"\nScan complete: Checked {total_files} foreign HTML files.")
    if issues_found == 0:
        print("PERFECT: 0 untranslated English fragments found across all pages!")
    else:
        print(f"FAILED: Found {issues_found} untranslated fragments.")

if __name__ == '__main__':
    scan_all_pages()
