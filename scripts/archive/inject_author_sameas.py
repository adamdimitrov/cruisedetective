#!/usr/bin/env python3
"""
Enriches all JSON-LD Person schemas for 'Adam Dimitrov' with authoritative sameAs entity signals.
"""

import os
import glob
import json
import re

REPO_DIR = '/Users/adamdimitrov/Development/cruisedetective'

SAME_AS = [
    "https://www.youtube.com/channel/UCBEbDg9BiHUkppqseY5Oc7w",
    "https://www.instagram.com/adamdimitro/",
    "https://www.facebook.com/adam.dimitrov.39",
    "https://budapestadventures.com/",
    "https://luxurytraveltester.com/"
]

def enrich_dict(obj):
    if isinstance(obj, dict):
        # Check if this is an Adam Dimitrov Person node
        if obj.get('name') == 'Adam Dimitrov' or (obj.get('@type') == 'Person' and 'Adam Dimitrov' in str(obj.get('name', ''))):
            obj['sameAs'] = SAME_AS
        for k, v in list(obj.items()):
            enrich_dict(v)
    elif isinstance(obj, list):
        for item in obj:
            enrich_dict(item)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    def replace_jsonld(match):
        nonlocal modified
        tag_open = match.group(1)
        json_str = match.group(2)
        tag_close = match.group(3)

        try:
            data = json.loads(json_str.strip())
            enrich_dict(data)
            
            # Special case for index.html: attach founder to Organization
            if 'index.html' in file_path and isinstance(data, dict) and '@graph' in data:
                for node in data['@graph']:
                    if node.get('@type') == 'WebSite' and 'publisher' in node:
                        pub = node['publisher']
                        if pub.get('@type') == 'Organization' and 'founder' not in pub:
                            pub['founder'] = {
                                "@type": "Person",
                                "@id": "https://www.thecruisedetective.com/about/#adam-dimitrov",
                                "name": "Adam Dimitrov",
                                "jobTitle": "Founder & Head Cruise Detective",
                                "url": "https://www.thecruisedetective.com/about",
                                "sameAs": SAME_AS
                            }

            new_json_str = json.dumps(data, indent=2, ensure_ascii=False)
            modified = True
            return f"{tag_open}\n{new_json_str}\n{tag_close}"
        except Exception as e:
            print(f"Skipping malformed JSON-LD in {file_path}: {e}")
            return match.group(0)

    pattern = re.compile(r'(<script[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>)(.*?)(</script>)', re.DOTALL)
    new_content = pattern.sub(replace_jsonld, content)

    if modified and new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(REPO_DIR, '**', 'index.html'), recursive=True)
    count = 0
    for f in files:
        if process_file(f):
            count += 1
            print(f"Updated: {os.path.relpath(f, REPO_DIR)}")
    print(f"\nTotal files updated with sameAs entity links: {count}")

if __name__ == '__main__':
    main()
