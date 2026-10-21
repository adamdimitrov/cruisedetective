import urllib.request
import urllib.error
import json
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

PAGE_ID = "6a68d3bb9bd0297b342845af"
API_KEY = "a334489d0e8448518e948e004f57b9cb98f77dcb464ebd63aa6a2b4b82dcb4c5"

base_dir = "/Users/adamdimitrov/Development/cruisedetective/seine-advertorial"

with open(os.path.join(base_dir, "index.html"), "r") as f:
    html = f.read()

with open(os.path.join(base_dir, "styles.css"), "r") as f:
    css = f.read()

with open(os.path.join(base_dir, "script.js"), "r") as f:
    js = f.read()

# We'll put CSS in the head
head_code = f"<style>\n{css}\n</style>"

# We'll put HTML and JS in the footer
# Note: we shouldn't include the outer <html>, <head>, and <body> tags from index.html
# because Webflow provides its own wrapper. Let's just extract the body content.
import re
body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
if body_match:
    body_content = body_match.group(1)
else:
    body_content = html

footer_code = f"{body_content}\n<script>\n{js}\n</script>"

payload = {
    "scripts": {
        "head": head_code,
        "footer": footer_code
    }
}

req = urllib.request.Request(
    f"https://api.webflow.com/v2/pages/{PAGE_ID}/custom_code",
    data=json.dumps(payload).encode('utf-8'),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "accept-version": "2.0.0",
        "Content-Type": "application/json"
    },
    method="PUT"
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print("Error:", e)
