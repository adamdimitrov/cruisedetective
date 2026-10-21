import os
import re

base_dir = "/Users/adamdimitrov/Development/cruisedetective/seine-advertorial"

with open(os.path.join(base_dir, "index.html"), "r") as f:
    html = f.read()

with open(os.path.join(base_dir, "styles.css"), "r") as f:
    css = f.read()

with open(os.path.join(base_dir, "script.js"), "r") as f:
    js = f.read()

body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
if body_match:
    body_content = body_match.group(1)
else:
    body_content = html

bundled = f"""<!-- PASTE THIS ENTIRE SNIPPET INTO A WEBFLOW EMBED -->
<style>
{css}
</style>

{body_content}

<script>
{js}
</script>
"""

with open(os.path.join(base_dir, "bundled.html"), "w") as f:
    f.write(bundled)

print("Created bundled.html")
