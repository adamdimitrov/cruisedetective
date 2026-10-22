import os
import subprocess

FFMPEG = "/Users/adamdimitrov/.gemini/antigravity/brain/c4d06a09-c919-4811-89a1-4cdbfbc647c4/scratch/env/bin/ffmpeg"
RAW_DIR = "/Users/adamdimitrov/Development/cruisedetective/ads/video_raw"
OUT_DIR = "/Users/adamdimitrov/Development/cruisedetective/ads/dinner_creatives"

clean_horizontal = os.path.join(RAW_DIR, "clean_horizontal.mp4")
overlay_path = os.path.join(RAW_DIR, "clean_vertical_overlay.png")
final_video = os.path.join(OUT_DIR, "bateaux_mouches_45s_vertical_ad.mp4")

W, H = 1080, 1920

# Re-render with -loop 1 on the overlay image so it stays throughout all 48 seconds!
cmd_compose = [
    FFMPEG,
    "-f", "lavfi", "-i", f"color=c=0x0a0f1a:s={W}x{H}:r=25",
    "-i", clean_horizontal,
    "-loop", "1", "-i", overlay_path,
    "-filter_complex",
    "[1:v]scale=1080:608:force_original_aspect_ratio=decrease[vid];"
    "[0:v][vid]overlay=0:640:shortest=1[bgvid];"
    "[bgvid][2:v]overlay=0:0:shortest=1[outv]",
    "-map", "[outv]",
    "-map", "1:a",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    final_video, "-y"
]

print("Rendering video with looped persistent overlay...")
subprocess.run(cmd_compose, check=True)
print("Render complete!")

# Extract check frames at 5s, 15s, 30s, 42s
for sec in [5, 15, 30, 42]:
    out_f = os.path.join(OUT_DIR, f"check_frame_{sec:02d}.jpg")
    cmd_f = [
        FFMPEG, "-ss", f"00:00:{sec:02d}", "-i", final_video,
        "-frames:v", "1", out_f, "-y"
    ]
    subprocess.run(cmd_f, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Saved check frame at {sec}s -> {out_f}")
