import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/Users/adamdimitrov/.gemini/antigravity/brain/c4d06a09-c919-4811-89a1-4cdbfbc647c4/scratch/env/bin/ffmpeg"
RAW_DIR = "/Users/adamdimitrov/Development/cruisedetective/ads/video_raw"
SRC = os.path.join(RAW_DIR, "review_full.mp4")
OUT_DIR = "/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives"
PHOTO_REF = "/Users/adamdimitrov/Development/cruisedetective/ads/reference_library/adams_real_photos/06_6557d4b0f32b0baf412f95f5_Bateaux-mouches-dinner-cruise_(7).webp"

# 1. Clip 1: Use high-res photo 06 with subtle pan/zoom for Hook (0:00 to 0:08.50) + Adam's real voice
hook_audio = os.path.join(RAW_DIR, "hook_audio.aac")
subprocess.run([
    FFMPEG, "-ss", "00:00:00.00", "-t", "00:00:08.50", "-i", SRC,
    "-vn", "-c:a", "aac", "-b:a", "192k", hook_audio, "-y"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

hook_clip = os.path.join(RAW_DIR, "c1_hook_hires.mp4")
# Create 8.5s video from photo 06 scaled to 640x360 with subtle zoom
cmd_hook_vid = [
    FFMPEG, "-loop", "1", "-i", PHOTO_REF, "-i", hook_audio,
    "-filter_complex", "scale=640:360,zoompan=z='min(zoom+0.0008,1.15)':d=215:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=640x360",
    "-c:v", "libx264", "-t", "00:00:08.50", "-c:a", "copy", "-shortest",
    hook_clip, "-y"
]
subprocess.run(cmd_hook_vid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
print("Clip 1 Hook created with High-Res Photo & Voiceover!")

# 2. Clips 2 to 7 from live video (second 23 onwards - NO QR codes!)
TIGHT_SEGMENTS = [
    ("00:00:23.00", "00:00:08.00", "c2_mission"),
    ("00:00:48.50", "00:00:08.50", "c3_rooftop"),
    ("00:01:21.00", "00:00:05.50", "c4_food"),
    ("00:01:32.40", "00:00:08.60", "c5_drinks"),
    ("00:02:11.80", "00:00:04.20", "c6_value"),
    ("00:02:51.60", "00:00:05.50", "c7_verdict")
]

trimmed_files = [hook_clip]
for start, dur, label in TIGHT_SEGMENTS:
    out_clip = os.path.join(RAW_DIR, f"{label}.mp4")
    cmd = [
        FFMPEG, "-ss", start, "-t", dur, "-i", SRC,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        out_clip, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    trimmed_files.append(out_clip)

concat_list = os.path.join(RAW_DIR, "concat_clean.txt")
with open(concat_list, "w") as f:
    for tf in trimmed_files:
        f.write(f"file '{tf}'\n")

clean_horizontal = os.path.join(RAW_DIR, "clean_horizontal.mp4")
cmd_concat = [
    FFMPEG, "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", clean_horizontal, "-y"
]
subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
print("Clean narrative cut assembled (45 seconds)!")

# 3. Build 1080x1920 Clean Vector Overlay
W, H = 1080, 1920
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

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
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(bbox, radius=radius, fill=fill, outline=outline, width=width)

# Top Section (0 to 520)
draw.rectangle((0, 0, W, 520), fill=(10, 15, 26, 255))

pill_text = "THE CRUISE DETECTIVE • PERSONALLY TESTED"
font_pill = get_font(26, bold=True)
bbox_p = draw.textbbox((0, 0), pill_text, font=font_pill)
pw = bbox_p[2] - bbox_p[0]
draw_rounded_rect(draw, ((W - pw - 48)//2, 45, (W + pw + 48)//2, 100), radius=28, fill=(26, 67, 50, 255))
draw.text(((W - pw)//2, 60), pill_text, fill=(255, 255, 255, 255), font=font_pill)

h1 = "I Tested 5 Paris Dinner Cruises"
h2 = "Here's Why This One Took #1"
font_h1 = get_font(50, bold=True)
font_h2 = get_font(50, bold=True)
bbox_h1 = draw.textbbox((0, 0), h1, font=font_h1)
bbox_h2 = draw.textbbox((0, 0), h2, font=font_h2)
draw.text(((W - (bbox_h1[2] - bbox_h1[0]))//2, 135), h1, fill=(255, 255, 255, 255), font=font_h1)
draw.text(((W - (bbox_h2[2] - bbox_h2[0]))//2, 205), h2, fill=(255, 215, 0, 255), font=font_h2)

stars_text = "4.7 / 5.0 (2,840+ Verified Reviews)"
font_stars = get_font(30, bold=True)
bbox_s = draw.textbbox((0, 0), stars_text, font=font_stars)
draw.text(((W - (bbox_s[2] - bbox_s[0]))//2, 280), stars_text, fill=(203, 213, 225, 255), font=font_stars)

draw.line((60, 500, W - 60, 500), fill=(51, 65, 85, 255), width=2)

# Bottom Section (1350 to 1920)
draw.rectangle((0, 1350, W, H), fill=(10, 15, 26, 255))
draw.line((60, 1360, W - 60, 1360), fill=(51, 65, 85, 255), width=2)

card_margin = 50
card_w = W - card_margin * 2
card_y = 1395
card_h = 450
draw_rounded_rect(draw, (card_margin, card_y, card_margin + card_w, card_y + card_h), radius=28, fill=(255, 255, 255, 250), outline=(226, 232, 240, 255), width=2)

font_title = get_font(40, bold=True)
draw.text((card_margin + 36, card_y + 28), "Bateaux Mouches 20:30 Prestige Cruise", fill=(15, 23, 42, 255), font=font_title)

font_checks = get_font(30, bold=True)
checks = [
    "[✓]  Fresh 3-Course French Gourmet Dining",
    "[✓]  Bottle of Wine for 2 + Champagne Included",
    "[✓]  360° Open-Air Rooftop Deck (Eiffel Sparkle)",
    "[✓]  Live Classical Grand Piano & Violin Duo"
]
for i, c in enumerate(checks):
    draw.text((card_margin + 36, card_y + 90 + i * 50), c, fill=(30, 41, 59, 255), font=font_checks)

btn_y = card_y + 325
btn_h = 88
draw_rounded_rect(draw, (card_margin + 28, btn_y, card_margin + card_w - 28, btn_y + btn_h), radius=22, fill=(26, 67, 50, 255))
btn_text = "Reserve Online • From €114 • Instant QR Pass"
font_btn = get_font(32, bold=True)
bbox_b = draw.textbbox((0, 0), btn_text, font=font_btn)
draw.text(((W - (bbox_b[2] - bbox_b[0]))//2, btn_y + 26), btn_text, fill=(255, 255, 255, 255), font=font_btn)

overlay_path = os.path.join(RAW_DIR, "clean_vertical_overlay.png")
overlay.save(overlay_path)

# 4. Final Render
final_video = os.path.join(OUT_DIR, "bateaux_mouches_45s_vertical_ad.mp4")

cmd_compose = [
    FFMPEG,
    "-f", "lavfi", "-i", f"color=c=0x0a0f1a:s={W}x{H}:r=25",
    "-i", clean_horizontal,
    "-i", overlay_path,
    "-filter_complex",
    "[1:v]scale=1080:608:force_original_aspect_ratio=decrease[vid];"
    "[0:v][vid]overlay=0:640:shortest=1[bgvid];"
    "[bgvid][2:v]overlay=0:0[outv]",
    "-map", "[outv]",
    "-map", "1:a",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    final_video, "-y"
]
print("Rendering final clean 9:16 vertical video ad...")
subprocess.run(cmd_compose, check=True)
print("SUCCESS: Rendered", final_video)

