import os
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                idx = 1 if (bold and c.endswith(".ttc")) else 0
                return ImageFont.truetype(c, size, index=idx)
            except Exception:
                try:
                    return ImageFont.truetype(c, size)
                except Exception:
                    continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

# 1. Overlay 1A (Anniversary)
img1 = Image.open("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_1A_anniversary.jpg").convert("RGBA")
overlay1 = Image.new("RGBA", img1.size, (0, 0, 0, 0))
d1 = ImageDraw.Draw(overlay1)
W, H = img1.size

# Top IG Story Sticker - 2 lines if needed
sticker_text = "Booked the Seine dinner cruise for our anniversary in Paris"
font_sticker = get_font(int(W * 0.034), bold=True)
bbox_st = d1.textbbox((0, 0), sticker_text, font=font_sticker)
tw, th = bbox_st[2] - bbox_st[0], bbox_st[3] - bbox_st[1]
px, py = 24, 12
st_x = (W - (tw + px * 2)) // 2
st_y = int(H * 0.045)
draw_rounded_rect(d1, (st_x, st_y, st_x + tw + px * 2, st_y + th + py * 2), radius=16, fill=(255, 255, 255, 245))
d1.text((st_x + px, st_y + py - 2), sticker_text, fill=(15, 23, 42, 255), font=font_sticker)

# Subtitle
sub_text = "3 courses, Champagne & live music while gliding past the Eiffel Tower"
font_sub = get_font(int(W * 0.027), bold=True)
bbox_sub = d1.textbbox((0, 0), sub_text, font=font_sub)
sw, sh = bbox_sub[2] - bbox_sub[0], bbox_sub[3] - bbox_sub[1]
sub_x = (W - sw) // 2
sub_y = st_y + th + py * 2 + 14
d1.text((sub_x + 2, sub_y + 2), sub_text, fill=(0, 0, 0, 200), font=font_sub)
d1.text((sub_x, sub_y), sub_text, fill=(255, 255, 255, 255), font=font_sub)

# Bottom Pill
pill_text = "Reserve Online in 60s • From €114 • 100% Refund up to 24h"
font_pill = get_font(int(W * 0.032), bold=True)
bbox_pill = d1.textbbox((0, 0), pill_text, font=font_pill)
pw, ph = bbox_pill[2] - bbox_pill[0], bbox_pill[3] - bbox_pill[1]
ppx, ppy = 28, 16
pill_w = pw + ppx * 2
pill_x = (W - pill_w) // 2
pill_y = int(H * 0.90)
draw_rounded_rect(d1, (pill_x, pill_y, pill_x + pill_w, pill_y + ph + ppy * 2), radius=28, fill=(26, 67, 50, 240))
d1.text((pill_x + ppx, pill_y + ppy - 2), pill_text, fill=(255, 255, 255, 255), font=font_pill)

final1 = Image.alpha_composite(img1, overlay1).convert("RGB")
final1.save("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_1A_ad.jpg", quality=95)
final1.save("/Users/adamdimitrov/.gemini/antigravity/brain/305234ad-f367-4e0c-8212-be99e14fb0a2/ideogram_1A_ad.jpg", quality=95)

# 2. Overlay 2A (Birthday)
img2 = Image.open("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_2A_birthday.jpg").convert("RGBA")
overlay2 = Image.new("RGBA", img2.size, (0, 0, 0, 0))
d2 = ImageDraw.Draw(overlay2)
W, H = img2.size

# Headline top-left
h1_text = "The Ultimate Paris Birthday Dinner"
h2_text = "3 Courses, Champagne & Eiffel Tower Views"
font_h1 = get_font(int(W * 0.046), bold=True)
font_h2 = get_font(int(W * 0.036), bold=True)
d2.text((int(W*0.06) + 2, int(H*0.05) + 2), h1_text, fill=(0, 0, 0, 180), font=font_h1)
d2.text((int(W*0.06), int(H*0.05)), h1_text, fill=(255, 255, 255, 255), font=font_h1)
d2.text((int(W*0.06) + 2, int(H*0.05) + int(W*0.065) + 2), h2_text, fill=(0, 0, 0, 180), font=font_h2)
d2.text((int(W*0.06), int(H*0.05) + int(W*0.065)), h2_text, fill=(255, 255, 255, 240), font=font_h2)

# Bottom Card
card_margin = int(W * 0.05)
card_w = W - card_margin * 2
card_h = int(H * 0.15)
card_y = int(H * 0.81)
draw_rounded_rect(d2, (card_margin, card_y, card_margin + card_w, card_y + card_h), radius=22, fill=(255, 255, 255, 248), outline=(226, 232, 240, 200), width=2)

font_row = get_font(int(W * 0.031), bold=True)
rows = [
    "[✓]  3-Course Gourmet Dinner Cooked Fresh on Board",
    "[✓]  Champagne Apéritif + Full Bottle of Wine Included",
    "[✓]  Live Violin & Piano • Private Tables from €114"
]
line_spacing = card_h // 4
for i, r in enumerate(rows):
    d2.text((card_margin + 24, card_y + 14 + i * line_spacing), r, fill=(15, 23, 42, 255), font=font_row)

final2 = Image.alpha_composite(img2, overlay2).convert("RGB")
final2.save("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_2A_ad.jpg", quality=95)
final2.save("/Users/adamdimitrov/.gemini/antigravity/brain/305234ad-f367-4e0c-8212-be99e14fb0a2/ideogram_2A_ad.jpg", quality=95)

# 3. Overlay 3A (Sparkle Rooftop)
img3 = Image.open("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_3A_sparkle.jpg").convert("RGBA")
overlay3 = Image.new("RGBA", img3.size, (0, 0, 0, 0))
d3 = ImageDraw.Draw(overlay3)
W, H = img3.size

# Top POV
pov_text = "POV: It's 21:00 in Paris and the Eiffel Tower starts sparkling"
font_pov = get_font(int(W * 0.035), bold=True)
bbox_pov = d3.textbbox((0, 0), pov_text, font=font_pov)
pvw, pvh = bbox_pov[2] - bbox_pov[0], bbox_pov[3] - bbox_pov[1]
pv_x = (W - pvw) // 2
pv_y = int(H * 0.045)
d3.text((pv_x + 2, pv_y + 2), pov_text, fill=(0, 0, 0, 220), font=font_pov)
d3.text((pv_x, pv_y), pov_text, fill=(255, 255, 255, 255), font=font_pov)

# Bottom Card
card_margin = int(W * 0.05)
card_w = W - card_margin * 2
card_h = int(H * 0.15)
card_y = int(H * 0.81)
draw_rounded_rect(d3, (card_margin, card_y, card_margin + card_w, card_y + card_h), radius=22, fill=(255, 255, 255, 248), outline=(226, 232, 240, 200), width=2)

font_head = get_font(int(W * 0.038), bold=True)
font_desc = get_font(int(W * 0.027), bold=False)
font_price = get_font(int(W * 0.030), bold=True)

d3.text((card_margin + 24, card_y + 14), "Bateaux Mouches 20:30 Prestige Dinner Cruise", fill=(15, 23, 42, 255), font=font_head)
d3.text((card_margin + 24, card_y + 50), "2h15m Night Cruise • 3-Course Gourmet Dinner • Champagne & Wine Included", fill=(71, 85, 105, 255), font=font_desc)
d3.text((card_margin + 24, card_y + 82), "Private Tables from €114 • 100% Full Refund up to 24h Prior", fill=(26, 67, 50, 255), font=font_price)

final3 = Image.alpha_composite(img3, overlay3).convert("RGB")
final3.save("/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives/ideogram_3A_ad.jpg", quality=95)
final3.save("/Users/adamdimitrov/.gemini/antigravity/brain/305234ad-f367-4e0c-8212-be99e14fb0a2/ideogram_3A_ad.jpg", quality=95)

print("All 3 ads re-rendered cleanly!")
