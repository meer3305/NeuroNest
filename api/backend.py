"""
FastAPI app for RoutineAI API. Loaded by api/index.py so the Vercel
entry point only exposes `app` (avoids Handler/issubclass runtime error).

Video resolution strategy:
  1. Prompt matched to a LOCAL pre-recorded MP4 in api/recordings/
     -> returns {"video_path": "/api/recordings/<filename>", "source": "local"}
  2. No local file -> matched to a curated YOUTUBE embed URL
     -> returns {"video_path": "https://www.youtube.com/embed/<VIDEO_ID>", "source": "youtube"}
  3. Nothing found -> 404
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from urllib.parse import unquote

app = FastAPI(title="RoutineAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(API_DIR, "recordings")

# ---------------------------------------------------------------------------
# LOCAL recordings: prompt keywords -> filename in api/recordings/
# Longer phrases matched first (sorted by key length desc at runtime).
# Covers ALL flashcard titles & descriptions from the demo store.
# ---------------------------------------------------------------------------
PROMPT_TO_LOCAL_VIDEO = {
    # ── Brush Teeth (both morning & night routines) ──────────────────────────
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

    # ── Wake Up (morning) ────────────────────────────────────────────────────
    "open eyes and stretch":          "wakingup.mp4",
    "open your eyes and sit up":      "wakingup.mp4",
    "open your eyes and stretch":     "wakingup.mp4",
    "sit up in bed":                  "wakingup.mp4",
    "open your eyes":                 "wakingup.mp4",
    "waking up":                      "wakingup.mp4",
    "wake up":                        "wakingup.mp4",
    "morning":                        "wakingup.mp4",
    "stretch":                        "wakingup.mp4",
    "wake":                           "wakingup.mp4",
    "alarm":                          "wakingup.mp4",

    # ── Get Dressed / Change Clothes (morning) ───────────────────────────────
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

    # ── Eat Breakfast ────────────────────────────────────────────────────────
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

    # ── Read a Book (night) ──────────────────────────────────────────────────
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

# ---------------------------------------------------------------------------
# YOUTUBE fallback: curated child-friendly educational videos.
# Sources: ChuChu TV, Super Simple Songs, Blippi, Dave & Ava, etc.
# These video IDs are well-known kids' channels.
# ---------------------------------------------------------------------------
PROMPT_TO_YOUTUBE = {
    # ── Wash Hands ───────────────────────────────────────────────────────────
    # "Wash Your Hands" - Super Simple Songs (very popular kids channel)
    "wash your hands":  "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "wash hands":       "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "hand washing":     "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "handwashing":      "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "clean hands":      "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "soap":             "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",

    # ── Take a Bath ──────────────────────────────────────────────────────────
    # "Bath Song" - ChuChu TV Nursery Rhymes
    "take a bath":      "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bath time":        "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bathing":          "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "shower":           "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bath":             "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "scrub":            "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",

    # ── Go to Sleep / Bedtime ────────────────────────────────────────────────
    # "Go To Sleep" - Super Simple Songs
    "turn off lights":  "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "go to sleep":      "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "good sleep":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "bedtime":          "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "goodnight":        "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "good night":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "lights off":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "sleep":            "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",

    # ── Play with Toys ───────────────────────────────────────────────────────
    # "Toy Song" - Dave & Ava
    "play with toys":   "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playing with":     "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "play time":        "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playtime":         "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playing":          "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",

    # ── Clean Up Toys ────────────────────────────────────────────────────────
    # "Clean Up" - Super Simple Songs
    "clean up toys":    "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "clean up":         "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "put away toys":    "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "tidy up":          "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "tidy":             "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",

    # ── Make Bed ─────────────────────────────────────────────────────────────
    # "Making My Bed" - Blippi
    "make the bed":     "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    "make bed":         "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    "making bed":       "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    "making my bed":    "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",

    # ── Pack Backpack / Go to School ─────────────────────────────────────────
    # "Going to School" - ChuChu TV
    "pack backpack":    "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    "school bag":       "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    "backpack":         "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    "go to school":     "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",

    # ── Put on Shoes ─────────────────────────────────────────────────────────
    # "Shoes Song" - Super Simple Songs
    "put on shoes":     "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    "tie shoes":        "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    "shoes":            "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    "laces":            "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",

    # ── Drink Water ──────────────────────────────────────────────────────────
    # "Drink Water" - Kids health habits
    "drink water":      "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
    "hydrate":          "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
    "water":            "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
}


def _match_prompt(prompt: str, mapping: dict) -> str | None:
    """Return matching value for the first keyword found in prompt (longest key first)."""
    pl = prompt.lower().strip()
    for keyword, value in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if keyword in pl:
            return value
    # Word-by-word fallback
    words = [w for w in pl.replace(".", " ").replace(",", " ").split() if len(w) >= 4]
    for word in words:
        for keyword, value in mapping.items():
            if word in keyword:
                return value
    return None


@app.get("/")
def read_root():
    return {"status": "Online", "message": "RoutineAI API is working!", "recordings": RECORDINGS_DIR}


@app.get("/api/health")
@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/recordings/{filename}")
@app.get("/recordings/{filename}")
async def get_recording(filename: str):
    name = os.path.basename(unquote(filename))
    file_path = os.path.join(RECORDINGS_DIR, name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {name}")
    return FileResponse(file_path, media_type="video/mp4")


@app.post("/api/generate-animation")
@app.post("/generate-animation")
async def generate_animation(
    prompt: str = Query(default="", description="Flashcard title + description text"),
):
    """
    Resolve a video for the given flashcard step prompt.

    Priority:
      1. Local recording from api/recordings/ (user's own recordings).
      2. Curated YouTube embed URL for child-friendly educational content.
      3. 404 if nothing matches.

    Returns:
      {"video_path": <url>, "source": "local" | "youtube"}
    """
    try:
        # 1. Local recording
        local_fname = _match_prompt(prompt, PROMPT_TO_LOCAL_VIDEO)
        if local_fname:
            file_path = os.path.join(RECORDINGS_DIR, local_fname)
            if os.path.isfile(file_path):
                logging.info("Serving local recording '%s' for prompt: %s", local_fname, prompt)
                return {"video_path": f"/api/recordings/{local_fname}", "source": "local"}
            else:
                logging.warning("Matched '%s' but file missing on disk.", local_fname)

        # 2. YouTube fallback
        yt_url = _match_prompt(prompt, PROMPT_TO_YOUTUBE)
        if yt_url:
            logging.info("Serving YouTube video for prompt: %s", prompt)
            return {"video_path": yt_url, "source": "youtube"}

        # 3. Not found
        raise HTTPException(
            status_code=404,
            detail=(
                "No video found for this step. "
                "Supported steps: wake up, brush teeth, get dressed, eat breakfast, "
                "read a book, put on pajamas / night clothes, wash hands, take a bath, "
                "go to sleep, play with toys, clean up toys, make bed, pack backpack, "
                "put on shoes."
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("generate_animation error")
        raise HTTPException(status_code=500, detail=str(e))
