import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ads_dir = "/Users/adamdimitrov/Development/cruisedetective/ads"
os.makedirs(ads_dir, exist_ok=True)

# -------------------------------------------------------------
# Asset Sources (High-res Tiqets & Webflow CDN)
# -------------------------------------------------------------
BOAT_IMAGE_URL = "https://aws-tiqets-cdn.imgix.net/images/content/e6865f6dc1754bf79f4f96aa5fab07bf.jpeg?auto=format,compress&w=1200"
UPPER_DECK_URL = "https://aws-tiqets-cdn.imgix.net/images/content/6d9a538afbed4e0d93b420ee4c113cb0.jpeg?auto=format,compress&w=1200"
EIFFEL_BOAT_URL = "https://aws-tiqets-cdn.imgix.net/images/content/e6a2ad487dfe46d38df7015a6f0660ac.jpeg?auto=format,compress&w=1200"
CROWD_QUEUE_URL = "https://images.unsplash.com/photo-1577744486770-020ab432da65?w=1200&auto=format&fit=crop&q=80"
SUNSET_SEINE_URL = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1200&auto=format&fit=crop&q=80"

def download_image(url, filename):
    path = os.path.join(ads_dir, filename)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(path, "wb") as f:
            f.write(resp.read())
    return Image.open(path).convert("RGBA")

# Font helpers
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# -------------------------------------------------------------
# 1. Concept 1: Split Screen "Us vs. Them"
# -------------------------------------------------------------
def create_ad_1():
    print("Generating Ad 1: Split Screen...")
    w, h = 1080, 1350
    canvas = Image.new("RGBA", (w, h), (15, 23, 42, 255))

    # Top: Queue (0 to 650)
    top_raw = download_image(CROWD_QUEUE_URL, "crowd_raw.jpg")
    top_img = top_raw.resize((w, 650), Image.Resampling.LANCZOS)
    # Add dark reddish overlay
    red_overlay = Image.new("RGBA", (w, 650), (120, 20, 20, 100))
    top_img = Image.alpha_composite(top_img, red_overlay)
    canvas.paste(top_img, (0, 0))

    # Bottom: Boat (650 to 1350)
    bot_raw = download_image(EIFFEL_BOAT_URL, "boat_eiffel_raw.jpg")
    bot_img = bot_raw.resize((w, 700), Image.Resampling.LANCZOS)
    canvas.paste(bot_img, (0, 650))

    draw = ImageDraw.Draw(canvas)

    # Divider Line
    draw.rectangle([0, 646, w, 654], fill=(255, 255, 255, 255))

    # Top Badges & Text
    # Badge "DOCK TICKET BOOTH"
    draw.rounded_rectangle([50, 40, 420, 100], radius=12, fill=(220, 38, 38, 240))
    font_badge = get_font(FONT_BLACK, 28)
    draw.text((70, 52), "❌ DOCK BOX OFFICE", font=font_badge, fill=(255, 255, 255))

    # Big top callout
    draw.rounded_rectangle([50, 480, 780, 610], radius=16, fill=(15, 23, 42, 220))
    font_h1 = get_font(FONT_BLACK, 44)
    font_sub = get_font(FONT_BOLD, 28)
    draw.text((75, 495), "45-MINUTE WAIT IN LINE", font=font_h1, fill=(248, 113, 113))
    draw.text((75, 555), "Boats often depart full while you wait", font=font_sub, fill=(226, 232, 240))

    # Bottom Badges & Text
    # Badge "ONLINE SMARTPHONE TICKET"
    draw.rounded_rectangle([50, 690, 500, 750], radius=12, fill=(5, 150, 105, 240))
    draw.text((70, 702), "✅ SMARTPHONE TICKET", font=font_badge, fill=(255, 255, 255))

    # Big bottom callout
    draw.rounded_rectangle([50, 1100, 1030, 1300], radius=20, fill=(15, 23, 42, 235))
    draw.text((80, 1120), "WALK STRAIGHT TO PIER 3 • €18", font=font_h1, fill=(52, 211, 153))
    draw.text((80, 1180), "Scan your phone barcode • Hop on any boat today", font=font_sub, fill=(241, 245, 249))
    draw.text((80, 1230), "Departs every 30 mins directly beneath Eiffel Tower →", font=get_font(FONT_BOLD, 24), fill=(253, 224, 71))

    out_path = os.path.join(ads_dir, "ad_1_split_screen.jpg")
    canvas.convert("RGB").save(out_path, quality=95)
    print("Saved:", out_path)

# -------------------------------------------------------------
# 2. Concept 2: Native iPhone Notes App
# -------------------------------------------------------------
def create_ad_2():
    print("Generating Ad 2: iPhone Notes Hack...")
    w, h = 1080, 1350
    # Warm off-white background like iOS Notes
    canvas = Image.new("RGBA", (w, h), (252, 250, 242, 255))
    draw = ImageDraw.Draw(canvas)

    font_nav = get_font(FONT_BOLD, 36)
    font_title = get_font(FONT_BLACK, 54)
    font_body = get_font(FONT_BOLD, 36)
    font_regular = get_font(FONT_REGULAR, 32)
    font_small = get_font(FONT_REGULAR, 26)

    # Top Navigation Bar (< Notes)
    draw.text((50, 60), "‹ Notes", font=font_nav, fill=(234, 179, 8))
    draw.text((w - 180, 60), "•••", font=font_nav, fill=(234, 179, 8))

    # Date
    draw.text((w//2 - 130, 130), "Today at 14:15", font=font_small, fill=(160, 160, 160))

    # Title
    draw.text((50, 190), "Paris Hack: The Eiffel Tower\nBoat Cruise Mistake 🗼", font=font_title, fill=(28, 25, 23))

    # Divider
    draw.line([50, 340, w - 50, 340], fill=(225, 220, 210), width=2)

    # Lead paragraph
    draw.text((50, 370), "If you are doing a Seine river cruise this week,\nDO NOT buy tickets at the dock box office.", font=font_body, fill=(68, 64, 60))

    # Box 1: The Mistake (Red tint)
    draw.rounded_rectangle([50, 490, w - 50, 710], radius=16, fill=(254, 242, 242), outline=(252, 165, 165), width=2)
    draw.text((80, 520), "❌ Buying at Port de la Bourdonnais:", font=get_font(FONT_BLACK, 32), fill=(185, 28, 28))
    draw.text((80, 575), "• 40 to 50-minute queue in the cold / sun", font=font_regular, fill=(50, 50, 50))
    draw.text((80, 620), "• Sunset and night slots sell out while you wait", font=font_regular, fill=(50, 50, 50))
    draw.text((80, 665), "• Exact same price as online (€18)", font=font_regular, fill=(50, 50, 50))

    # Box 2: The Solution (Green tint)
    draw.rounded_rectangle([50, 750, w - 50, 1020], radius=16, fill=(240, 253, 244), outline=(134, 239, 172), width=2)
    draw.text((80, 780), "✅ Getting the official mobile ticket:", font=get_font(FONT_BLACK, 32), fill=(21, 128, 61))
    draw.text((80, 835), "• Skip the box office line completely", font=font_body, fill=(22, 101, 52))
    draw.text((80, 880), "• Walk straight to Pier 3 right under Eiffel Tower", font=font_regular, fill=(50, 50, 50))
    draw.text((80, 925), "• Flexible day pass: Hop on any boat today", font=font_regular, fill=(50, 50, 50))
    draw.text((80, 970), "• Audio guide in 11 languages + 360° top deck", font=font_regular, fill=(50, 50, 50))

    # Final advice
    draw.text((50, 1055), "Save yourself the 45-minute wait. Tap below to grab\nyour mobile tickets on Tiqets before walking down.", font=font_regular, fill=(80, 80, 80))

    # Yellow/Gold Button
    draw.rounded_rectangle([50, 1160, w - 50, 1270], radius=18, fill=(234, 179, 8))
    font_btn = get_font(FONT_BLACK, 36)
    draw.text((150, 1195), "BOOK MOBILE TICKETS (€18) →", font=font_btn, fill=(255, 255, 255))

    out_path = os.path.join(ads_dir, "ad_2_iphone_notes.jpg")
    canvas.convert("RGB").save(out_path, quality=95)
    print("Saved:", out_path)

# -------------------------------------------------------------
# 3. Concept 3: Review Overlay (Social Proof)
# -------------------------------------------------------------
def create_ad_3():
    print("Generating Ad 3: Review Overlay...")
    w, h = 1080, 1350
    bg_raw = download_image(UPPER_DECK_URL, "upper_deck_raw.jpg")
    bg = bg_raw.resize((w, h), Image.Resampling.LANCZOS)

    # Dark gradient overlay at bottom for readability
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(500, h):
        alpha = int(220 * ((y - 500) / (h - 500)))
        grad_draw.line([(0, y), (w, y)], fill=(11, 17, 32, alpha))
    bg = Image.alpha_composite(bg, gradient)

    draw = ImageDraw.Draw(bg)

    # Top Brand Bar
    draw.rounded_rectangle([50, 50, 600, 110], radius=30, fill=(15, 23, 42, 220))
    draw.text((75, 65), "🗼 BATEAUX PARISIENS SEINE CRUISE", font=get_font(FONT_BOLD, 26), fill=(255, 255, 255))

    # Main Headline
    font_hero = get_font(FONT_BLACK, 56)
    draw.text((50, 580), "“Best €18 We Spent\nin All of Paris.”", font=font_hero, fill=(255, 255, 255))

    # Floating Review Card
    draw.rounded_rectangle([50, 750, w - 50, 1140], radius=24, fill=(255, 255, 255, 245), outline=(226, 232, 240), width=2)

    # Review header
    draw.text((90, 790), "★★★★★", font=get_font(FONT_BOLD, 46), fill=(234, 179, 8))
    draw.text((270, 798), "4.4 / 5.0  (77,000+ Reviews)", font=get_font(FONT_BOLD, 30), fill=(71, 85, 105))
    
    # Badge Verified
    draw.rounded_rectangle([720, 790, 980, 840], radius=8, fill=(236, 253, 245))
    draw.text((740, 802), "✓ Verified Traveler", font=get_font(FONT_BOLD, 22), fill=(5, 150, 105))

    # Review Quote Text
    review_lines = [
        "“The ticket booth queue stretched back to the bridge.",
        "We bought these online 10 mins before walking to Pier 3,",
        "scanned our phones, and walked straight onto the top deck.",
        "Cruising past the Eiffel Tower as it lit up was magical!”"
    ]
    font_quote = get_font(FONT_REGULAR, 28)
    for i, line in enumerate(review_lines):
        draw.text((90, 870 + (i * 40)), line, font=font_quote, fill=(30, 41, 59))

    draw.text((90, 1060), "— Sarah & Mark T., USA", font=get_font(FONT_BOLD, 26), fill=(15, 23, 42))

    # Bottom CTA Banner
    draw.rounded_rectangle([50, 1180, w - 50, 1290], radius=16, fill=(16, 185, 129))
    draw.text((120, 1210), "SKIP THE LINE • BOOK TICKETS (€18) →", font=get_font(FONT_BLACK, 36), fill=(255, 255, 255))

    out_path = os.path.join(ads_dir, "ad_3_review_proof.jpg")
    bg.convert("RGB").save(out_path, quality=95)
    print("Saved:", out_path)

# -------------------------------------------------------------
# 4. Concept 4: Map & Pier Location Anchor
# -------------------------------------------------------------
def create_ad_4():
    print("Generating Ad 4: Pier Location Anchor...")
    w, h = 1080, 1350
    bg_raw = download_image(BOAT_IMAGE_URL, "boat_pier_raw.jpg")
    bg = bg_raw.resize((w, h), Image.Resampling.LANCZOS)

    # Dark overlay
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for y in range(400, h):
        alpha = int(230 * ((y - 400) / (h - 400)))
        ov_draw.line([(0, y), (w, y)], fill=(15, 23, 42, alpha))
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)

    # Top Location Pin Card
    draw.rounded_rectangle([50, 60, w - 50, 210], radius=20, fill=(255, 255, 255, 245), outline=(226, 232, 240), width=2)
    draw.text((90, 85), "📍 DEPARTS DIRECTLY AT EIFFEL TOWER", font=get_font(FONT_BLACK, 32), fill=(225, 29, 72))
    draw.text((90, 135), "Port de la Bourdonnais, Pier 3 • 2-min walk from Champ de Mars", font=get_font(FONT_BOLD, 26), fill=(51, 65, 85))

    # Main Headline in bottom section
    font_h1 = get_font(FONT_BLACK, 54)
    draw.text((50, 520), "1-Hour Panoramic\nSeine River Cruise", font=font_h1, fill=(255, 255, 255))

    # Price Tag Callout
    draw.rounded_rectangle([50, 680, 480, 770], radius=16, fill=(5, 150, 105))
    draw.text((80, 700), "From €18 / Person", font=get_font(FONT_BLACK, 38), fill=(255, 255, 255))
    draw.text((510, 715), "• Kids under 4 free", font=get_font(FONT_BOLD, 30), fill=(241, 245, 249))

    # Checklist
    checks = [
        "⚡ 100% Smartphone Ticket (Skip the 45-min dock line)",
        "⏱️ Departs every 30-60 mins (Open ticket, no fixed hour)",
        "🎧 Audio guide in 11 languages (listen on your phone)",
        "🗼 360° Open top deck for stunning Eiffel Tower photos",
        "🔄 100% Free cancellation up to 24 hours before"
    ]
    font_check = get_font(FONT_BOLD, 28)
    for i, c in enumerate(checks):
        draw.text((50, 820 + (i * 65)), c, font=font_check, fill=(226, 232, 240))

    # Bottom CTA Button
    draw.rounded_rectangle([50, 1180, w - 50, 1290], radius=16, fill=(16, 185, 129))
    draw.text((160, 1210), "GET MOBILE TICKETS & BOARD →", font=get_font(FONT_BLACK, 36), fill=(255, 255, 255))

    out_path = os.path.join(ads_dir, "ad_4_pier_location.jpg")
    bg.convert("RGB").save(out_path, quality=95)
    print("Saved:", out_path)

if __name__ == "__main__":
    create_ad_1()
    create_ad_2()
    create_ad_3()
    create_ad_4()
    print("ALL 4 STATIC AD CREATIVES GENERATED SUCCESSFULLY!")
