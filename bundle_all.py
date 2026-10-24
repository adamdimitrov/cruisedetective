import os
import re

directories = [
    "romantic-quiz",
    "dinner-comparison",
    "dinner-advertorial",
    "seine-deal",
    "paris-fast-booking",
    "paris-family-cruise",
    "paris-family-pass",
    "paris-family-compare",
    "paris-couples-pass",
    "seine-comparison"
]

base_root = "/Users/adamdimitrov/Development/cruisedetective"

for dir_name in directories:
    dir_path = os.path.join(base_root, dir_name)
    html_path = os.path.join(dir_path, "index.html")
    css_path = os.path.join(dir_path, "styles.css")
    js_path = os.path.join(dir_path, "script.js")
    bundled_path = os.path.join(dir_path, "bundled.html")

    if not (os.path.exists(html_path) and os.path.exists(css_path) and os.path.exists(js_path)):
        print(f"Skipping {dir_name}: missing core files")
        continue

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_content = body_match.group(1)
    else:
        body_content = html

    bundled = f"""<!-- BUNDLED FOR WEBFLOW EMBED OR STANDALONE USE: {dir_name} -->
<style>
{css}
</style>

{body_content}

<script>
{js}
</script>
"""

    with open(bundled_path, "w", encoding="utf-8") as f:
        f.write(bundled)

    print(f"Successfully generated bundled.html for {dir_name}")
