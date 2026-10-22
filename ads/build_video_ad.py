import os
import subprocess

FFMPEG = "/Users/adamdimitrov/.gemini/antigravity/brain/c4d06a09-c919-4811-89a1-4cdbfbc647c4/scratch/env/bin/ffmpeg"
RAW_DIR = "/Users/adamdimitrov/Development/cruisedetective/ads/video_raw"
SRC = os.path.join(RAW_DIR, "review_full.mp4")

# Defined segments (start, duration, label)
SEGMENTS = [
    ("00:00:00.00", "00:00:08.50", "01_hook"),
    ("00:00:20.50", "00:00:10.50", "02_mission"),
    ("00:00:43.70", "00:00:13.30", "03_rooftop"),
    ("00:01:21.00", "00:00:20.00", "04_food_drinks"),
    ("00:02:11.80", "00:00:04.20", "05_bang_for_buck"),
    ("00:02:51.60", "00:00:08.50", "06_verdict")
]

trimmed_files = []
for start, dur, label in SEGMENTS:
    out_clip = os.path.join(RAW_DIR, f"{label}.mp4")
    cmd = [
        FFMPEG, "-ss", start, "-t", dur, "-i", SRC,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        out_clip, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    trimmed_files.append(out_clip)
    print(f"Trimmed {label} ({dur})")

# Write concat list
concat_list = os.path.join(RAW_DIR, "concat.txt")
with open(concat_list, "w") as f:
    for tf in trimmed_files:
        f.write(f"file '{tf}'\n")

# Concatenate
concat_mp4 = os.path.join(RAW_DIR, "ad_cut_horizontal.mp4")
cmd_concat = [
    FFMPEG, "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", concat_mp4, "-y"
]
subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
print("Concatenated cut created at", concat_mp4)

