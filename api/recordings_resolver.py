"""
Resolve animation requests from pre-recorded MP4 files in api/recordings.
No moviepy or heavy dependencies - only file matching and copy.
Covers ALL flashcard step titles and descriptions from the demo/default routines.
"""
import os
import shutil
import time
import logging

RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")

# Video files that are already in api/recordings/
FALLBACK_FILES = {}

# Keyword (in prompt) -> filename in api/recordings/ (longer phrases matched first)
PROMPT_TO_VIDEO = {
    # ── Brush Teeth ──────────────────────────────────────────────────────────
    "brush teeth flashcard":          "brushing your teeth.mp4",
    "brushing your teeth":            "brushing your teeth.mp4",
    "toothbrush and toothpaste":      "brushing your teeth.mp4",
    "use your toothbrush":            "brushing your teeth.mp4",
    "use toothbrush":                 "brushing your teeth.mp4",
    "brush for two minutes":          "brushing your teeth.mp4",
    "brush your teeth":               "brushing your teeth.mp4",
    "brushing teeth":                 "brushing your teeth.mp4",
    "brush teeth":                    "brushing your teeth.mp4",
    "dental hygiene":                 "brushing your teeth.mp4",
    "toothbrush":                     "brushing your teeth.mp4",
    "toothpaste":                     "brushing your teeth.mp4",
    "teeth":                          "brushing your teeth.mp4",
    "tooth":                          "brushing your teeth.mp4",
    "brush":                          "brushing your teeth.mp4",
    # ── Wake Up ──────────────────────────────────────────────────────────────
    "open eyes and stretch":          "wakingup.mp4",
    "open your eyes and sit up":      "wakingup.mp4",
    "open your eyes and stretch":     "wakingup.mp4",
    "sit up in bed":                  "wakingup.mp4",
    "open your eyes":                 "wakingup.mp4",
    "waking up":                      "wakingup.mp4",
    "wake up":                        "wakingup.mp4",
    "morning":                        "wakingup.mp4",
    "stretch":                        "wakingup.mp4",
    "alarm":                          "wakingup.mp4",
    "wake":                           "wakingup.mp4",
    # ── Get Dressed / Change Clothes ─────────────────────────────────────────
    "put on your favorite outfit":    "changing clothes.mp4",
    "put on clothes":                 "changing clothes.mp4",
    "changing clothes":               "changing clothes.mp4",
    "change clothes":                 "changing clothes.mp4",
    "get dressed":                    "changing clothes.mp4",
    "put on outfit":                  "changing clothes.mp4",
    "favorite outfit":                "changing clothes.mp4",
    "outfit":                         "changing clothes.mp4",
    "clothes":                        "changing clothes.mp4",
    "dress":                          "changing clothes.mp4",
    "shirt":                          "changing clothes.mp4",
    "wear":                           "changing clothes.mp4",
    # ── Eat Breakfast ─────────────────────────────────────────────────────────
    "enjoy a healthy meal":           "Eating breakfast.mp4",
    "eating breakfast":               "Eating breakfast.mp4",
    "eat breakfast":                  "Eating breakfast.mp4",
    "healthy meal":                   "Eating breakfast.mp4",
    "breakfast":                      "Eating breakfast.mp4",
    "lunch":                          "Eating breakfast.mp4",
    "dinner":                         "Eating breakfast.mp4",
    "food":                           "Eating breakfast.mp4",
    "meal":                           "Eating breakfast.mp4",
    "eat":                            "Eating breakfast.mp4",
    # ── Put on Pajamas / Night Clothes ───────────────────────────────────────
    "change into comfy pjs":          "night clothes.mp4",
    "change into comfy":              "night clothes.mp4",
    "put on pajamas":                 "night clothes.mp4",
    "night clothes":                  "night clothes.mp4",
    "comfy pjs":                      "night clothes.mp4",
    "pyjamas":                        "night clothes.mp4",
    "pajamas":                        "night clothes.mp4",
    "sleepwear":                      "night clothes.mp4",
    "night":                          "night clothes.mp4",
    "pjs":                            "night clothes.mp4",
    # ── Read a Book ───────────────────────────────────────────────────────────
    "pick a favorite story":          "reading a book.mp4",
    "pick a fun story":               "reading a book.mp4",
    "reading a book":                 "reading a book.mp4",
    "favorite story":                 "reading a book.mp4",
    "read a book":                    "reading a book.mp4",
    "fun story":                      "reading a book.mp4",
    "reading":                        "reading a book.mp4",
    "story":                          "reading a book.mp4",
    "book":                           "reading a book.mp4",
    "read":                           "reading a book.mp4",
}


def resolve_recording(prompt: str, out_dir: str, filename_prefix: str = "animation") -> str | None:
    """
    If a matching MP4 exists in api/recordings, copy it to out_dir and return path.
    Returns None if no match or any error (serverless-safe).
    """
    try:
        if not prompt or not isinstance(prompt, str):
            return None
        if not os.path.isdir(RECORDINGS_DIR):
            try:
                os.makedirs(RECORDINGS_DIR, exist_ok=True)
            except OSError:
                pass
            return None

        prompt_lower = prompt.lower().strip()
        matched_file = None

        # 1. Explicit keyword mapping (longer phrases first)
        for keyword, video_file in sorted(PROMPT_TO_VIDEO.items(), key=lambda x: -len(x[0])):
            if keyword in prompt_lower:
                candidate = os.path.join(RECORDINGS_DIR, video_file)
                if os.path.isfile(candidate):
                    matched_file = video_file
                    break
                fallback = FALLBACK_FILES.get(video_file)
                if fallback:
                    candidate_fb = os.path.join(RECORDINGS_DIR, fallback)
                    if os.path.isfile(candidate_fb):
                        matched_file = fallback
                        break

        if matched_file:
            src = os.path.join(RECORDINGS_DIR, matched_file)
            ts = int(time.time())
            safe = "".join(c for c in prompt_lower if c.isalnum() or c in ("-", "_"))[:40]
            dest_name = f"{filename_prefix}-{safe}-{ts}.mp4"
            dest_path = os.path.join(out_dir, dest_name)
            try:
                os.makedirs(out_dir, exist_ok=True)
            except OSError:
                pass
            shutil.copy2(src, dest_path)
            logging.info("Serving recording: %s -> %s", src, dest_path)
            return dest_path

        # 2. Scan folder: match by filename tokens
        for fname in os.listdir(RECORDINGS_DIR):
            if not fname.lower().endswith(".mp4"):
                continue
            base = fname[:-4].replace("_", " ").replace("-", " ")
            if base in prompt_lower or any(word in prompt_lower for word in base.split() if len(word) > 2):
                src = os.path.join(RECORDINGS_DIR, fname)
                if os.path.isfile(src):
                    ts = int(time.time())
                    safe = "".join(c for c in prompt_lower if c.isalnum() or c in ("-", "_"))[:40]
                    dest_name = f"{filename_prefix}-{safe}-{ts}.mp4"
                    dest_path = os.path.join(out_dir, dest_name)
                    try:
                        os.makedirs(out_dir, exist_ok=True)
                    except OSError:
                        pass
                    shutil.copy2(src, dest_path)
                    logging.info("Serving recording (scan): %s -> %s", src, dest_path)
                    return dest_path
    except OSError as e:
        logging.warning("Recordings resolve failed: %s", e)
    except Exception as e:
        logging.warning("Recordings resolve error: %s", e)
    return None
