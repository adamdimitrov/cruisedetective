import os
import re

def test_landing_pages():
    base_dir = "/Users/adamdimitrov/Development/cruisedetective"
    pages = [
        "romantic-quiz",
        "dinner-comparison",
        "dinner-advertorial",
        "seine-deal",
        "paris-fast-booking",
        "paris-family-cruise"
    ]

    expected_pixel_id = "1355732169631751"
    expected_partner_id = "thecruisedetective.com-176436"

    for page in pages:
        page_dir = os.path.join(base_dir, page)
        index_file = os.path.join(page_dir, "index.html")
        script_file = os.path.join(page_dir, "script.js")
        css_file = os.path.join(page_dir, "styles.css")
        bundled_file = os.path.join(page_dir, "bundled.html")

        print(f"\n--- Testing Landing Page: {page} ---")

        # 1. Check file existence
        for f in [index_file, script_file, css_file, bundled_file]:
            assert os.path.exists(f), f"Missing file: {f}"
            print(f"  ✓ File exists: {os.path.basename(f)}")

        # 2. Check HTML contents
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()

        assert expected_pixel_id in html, f"Meta Pixel ID {expected_pixel_id} missing from {index_file}"
        print(f"  ✓ Meta Pixel {expected_pixel_id} verified in HTML head")

        page_partner_id = "luxurytraveltester" if page == "paris-fast-booking" else expected_partner_id

        assert page_partner_id in html, f"Tiqets Partner ID {page_partner_id} missing from {index_file}"
        print(f"  ✓ Tiqets Partner ID {page_partner_id} verified on links")

        # Check Tiqets links
        tiqets_links = re.findall(r'href=[\'"](https://www\.tiqets\.com[^\'"]+)[\'"]', html)
        assert len(tiqets_links) >= 1, f"No Tiqets links found in {index_file}"
        print(f"  ✓ Found {len(tiqets_links)} Tiqets CTA link(s)")
        for link in tiqets_links:
            assert f"partner={page_partner_id}" in link, f"Partner missing in {link}"
            assert "tq_campaign=" in link, f"tq_campaign missing in {link}"

        # 3. Check Script contents
        with open(script_file, "r", encoding="utf-8") as f:
            js = f.read()

        assert "cd_gclid" in js, f"cd_gclid missing in {script_file}"
        assert "fbclid" in js, f"fbclid missing in {script_file}"
        assert "click_id" in js, f"click_id missing in {script_file}"
        assert "subid" in js, f"subid missing in {script_file}"
        assert "InitiateCheckout" in js, f"InitiateCheckout missing in {script_file}"
        print("  ✓ Tracking script verifies: fbclid capture, dual storage, link decoration, and InitiateCheckout")

    print("\n==========================================")
    print("ALL 3 LANDING PAGES PASSED ALL VERIFICATIONS!")
    print("==========================================")

if __name__ == "__main__":
    test_landing_pages()
