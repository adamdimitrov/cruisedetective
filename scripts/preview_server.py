#!/usr/bin/env python3
"""
The Cruise Detective - Vercel-Emulating Local Preview Server
Simulates Vercel rewrites, cleanUrls, and static delivery locally.
Zero external dependencies (uses standard library http.server).
"""

import http.server
import json
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load rewrites from vercel.json
VERCEL_JSON_PATH = os.path.join(ROOT_DIR, "vercel.json")
rewrites = []
if os.path.exists(VERCEL_JSON_PATH):
    try:
        with open(VERCEL_JSON_PATH, "r", encoding="utf-8") as f:
            v_data = json.load(f)
            rewrites = v_data.get("rewrites", [])
    except Exception as e:
        print(f"[WARN] Could not parse vercel.json: {e}")

class VercelPreviewHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def translate_path(self, path):
        clean_path = path.split("?")[0].rstrip("/")
        if not clean_path:
            clean_path = "/"

        # 1. Match exact vercel.json rewrites
        for r in rewrites:
            src = r["source"].rstrip("/") or "/"
            if clean_path == src:
                dest = r["destination"].lstrip("/")
                target = os.path.join(ROOT_DIR, dest)
                if os.path.isfile(target):
                    return target

        # 2. Check for clean folder index.html
        subpath = clean_path.lstrip("/")
        if subpath:
            candidate = os.path.join(ROOT_DIR, subpath, "index.html")
            if os.path.isfile(candidate):
                return candidate

        return super().translate_path(path)

    def end_headers(self):
        # Disable caching for live preview inspection
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

if __name__ == "__main__":
    os.chdir(ROOT_DIR)
    server_address = ("127.0.0.1", PORT)
    httpd = http.server.HTTPServer(server_address, VercelPreviewHandler)
    print(f"\n==========================================================")
    print(f" Cruise Detective Preview Server running at http://localhost:{PORT}")
    print(f" Testing 5 Money Hubs:")
    print(f"   1. http://localhost:{PORT}/seine-river-cruises-paris")
    print(f"   2. http://localhost:{PORT}/dinner-cruises-paris")
    print(f"   3. http://localhost:{PORT}/canal-cruises-amsterdam")
    print(f"   4. http://localhost:{PORT}/thames-river-cruises-london")
    print(f"   5. http://localhost:{PORT}/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison")
    print(f" Press Ctrl+C to stop.")
    print(f"==========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()
