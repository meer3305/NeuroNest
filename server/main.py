import os
import logging
from dotenv import load_dotenv

# Load env before importing modules that read env at import time
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Routine Bright Animation Backend")

BACKEND_CORS_ORIGIN = os.getenv("BACKEND_CORS_ORIGIN", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[BACKEND_CORS_ORIGIN, "http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated videos and recordings as static files so the frontend can play them
VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)
app.mount("/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

# Recordings resolver: use MP4s from server/recordings (no moviepy dependency)
from recordings_resolver import resolve_recording

# ---------------------------------------------------------------------------
# YouTube fallback: curated child-friendly educational videos.
# Used when no local recording matches the prompt.
# ---------------------------------------------------------------------------
PROMPT_TO_YOUTUBE = {
    # Wash Hands - Super Simple Songs "Wash Your Hands"
    "wash your hands":  "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "wash hands":       "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "hand washing":     "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "handwashing":      "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "clean hands":      "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    "soap":             "https://www.youtube.com/embed/mDsVDdR8DkY?autoplay=1&rel=0",
    # Take a Bath - ChuChu TV "Bath Song"
    "take a bath":      "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bath time":        "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bathing":          "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "shower":           "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "bath":             "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    "scrub":            "https://www.youtube.com/embed/8yGfKQS3BSI?autoplay=1&rel=0",
    # Go to Sleep - Super Simple Songs "Go To Sleep"
    "turn off lights":  "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "go to sleep":      "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "good sleep":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "bedtime":          "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "goodnight":        "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "good night":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "lights off":       "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    "sleep":            "https://www.youtube.com/embed/xkJh5MGXSI8?autoplay=1&rel=0",
    # Play with Toys - Dave & Ava "Toys Song"
    "play with toys":   "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playing with":     "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "play time":        "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playtime":         "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    "playing":          "https://www.youtube.com/embed/TLBynnONy3E?autoplay=1&rel=0",
    # Clean Up - Super Simple Songs "Clean Up"
    "clean up toys":    "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "clean up":         "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "put away toys":    "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "tidy up":          "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    "tidy":             "https://www.youtube.com/embed/6lXCLEY_nkU?autoplay=1&rel=0",
    # Make Bed
    "make the bed":     "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    "make bed":         "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    "making bed":       "https://www.youtube.com/embed/Jh6nLuZZnng?autoplay=1&rel=0",
    # Pack Backpack
    "pack backpack":    "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    "school bag":       "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    "backpack":         "https://www.youtube.com/embed/nHbTTjkLJeE?autoplay=1&rel=0",
    # Put on Shoes
    "put on shoes":     "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    "tie shoes":        "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    "shoes":            "https://www.youtube.com/embed/HGD1RbK5Gqw?autoplay=1&rel=0",
    # Drink Water
    "drink water":      "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
    "hydrate":          "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
    "water":            "https://www.youtube.com/embed/jspPaGJvK9k?autoplay=1&rel=0",
}


def _match_youtube(prompt: str) -> str | None:
    pl = prompt.lower().strip()
    for keyword, url in sorted(PROMPT_TO_YOUTUBE.items(), key=lambda x: -len(x[0])):
        if keyword in pl:
            return url
    return None


@app.post("/generate-animation")
async def generate_animation_endpoint(
    prompt: str = Query(..., description="Flashcard text, e.g., 'Brush your teeth'"),
    request: Request = None,
):
    """
    Return a video URL by matching the prompt to:
    1. Pre-recorded MP4s in server/recordings/ (user's own recordings).
    2. Curated YouTube embed URLs for child-friendly educational content.
    """
    try:
        # 1. Try local recordings
        local_path = resolve_recording(prompt, VIDEOS_DIR, filename_prefix="animation")
        if local_path:
            base = str(request.base_url).rstrip("/") if request else ""
            filename = os.path.basename(local_path)
            public_url = f"{base}/videos/{filename}" if base else f"/videos/{filename}"
            return {"video_path": public_url, "source": "local"}

        # 2. Try YouTube fallback
        yt_url = _match_youtube(prompt)
        if yt_url:
            logging.info("Serving YouTube video for prompt: %s", prompt)
            return {"video_path": yt_url, "source": "youtube"}

        # 3. Not found
        logging.warning("No video match for prompt: %s", prompt)
        raise HTTPException(
            status_code=404,
            detail=(
                "No video found for this step. "
                "Try phrases like: 'wake up', 'brush teeth', 'get dressed', 'eat breakfast', "
                "'read a book', 'night clothes', 'wash hands', 'take a bath', 'go to sleep', "
                "'play with toys', 'clean up toys'."
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error in /generate-animation endpoint")
        raise HTTPException(status_code=500, detail=str(e))