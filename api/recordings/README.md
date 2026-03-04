# Pre-recorded animation videos

Place MP4 files here. Flashcard step titles and descriptions are matched to these filenames:

## Current recordings (already present)

| File | Flashcard step | Matched keywords |
|------|----------------|-----------------|
| `wakingup.mp4` | Wake up | wake up, morning, open eyes, stretch, sit up |
| `brushing your teeth.mp4` | Brush Teeth | brush teeth, toothbrush, toothpaste, brush for two minutes |
| `changing clothes.mp4` | Get Dressed | get dressed, change clothes, put on clothes, outfit |
| `Eating breakfast.mp4` | Eat Breakfast | eat breakfast, breakfast, healthy meal, food |
| `night clothes.mp4` | Put on Pajamas | pajamas, night clothes, comfy PJs, sleepwear |
| `reading a book.mp4` | Read a Book | read a book, story, book, reading |

## Steps WITHOUT local recordings → YouTube fallback

For these steps, a curated YouTube video is used automatically:

| Step | YouTube video |
|------|--------------|
| Wash Hands | "Wash Your Hands" - Super Simple Songs |
| Take a Bath | "Bath Song" - ChuChu TV |
| Go to Sleep | "Go To Sleep" - Super Simple Songs |
| Play with Toys | Kids toys educational video |
| Clean Up Toys | "Clean Up" - Super Simple Songs |
| Make Bed | Kids bedroom routine |
| Pack Backpack | Going to school video |
| Put on Shoes | Shoes song |

## Adding your own recordings

To add a recording for a missing step:
1. Drop the MP4 file in this folder with a descriptive name (e.g., `wash hands.mp4`)
2. Add an entry in `api/recordings_resolver.py` in the `PROMPT_TO_VIDEO` dict
3. Add the same entry in `api/backend.py` in `PROMPT_TO_LOCAL_VIDEO`

Use these exact filenames shown above OR add your own with matching entries in the resolver.
