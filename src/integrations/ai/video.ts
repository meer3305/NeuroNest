/**
 * Request a step video from the backend.
 *
 * The API matches the prompt to:
 *   1. A local pre-recorded MP4 in api/recordings/ (user's own recordings).
 *   2. A curated YouTube embed URL for child-friendly educational content.
 *
 * Use VITE_BACKEND_URL for local server (e.g. http://localhost:8001).
 * On Vercel, the API is served at /api/generate-animation.
 *
 * Returns { video_path, source } where source is "local" | "youtube".
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "";

export interface AnimationResult {
  /** URL to play: either a server path (/api/recordings/...) or a YouTube embed URL */
  video_path: string;
  /** "local" = user's own recording MP4, "youtube" = embedded YouTube video */
  source?: "local" | "youtube";
}

export async function requestGenerateAnimation(
  prompt: string
): Promise<AnimationResult> {
  const base = BACKEND_URL ? BACKEND_URL.replace(/\/$/, "") : "";
  const path = "/api/generate-animation";
  const url = base
    ? `${base}${path}?prompt=${encodeURIComponent(prompt)}`
    : `${path}?prompt=${encodeURIComponent(prompt)}`;

  const res = await fetch(url, { method: "POST" });

  if (!res.ok) {
    const text = await res.text();
    let message = text;
    try {
      const j = JSON.parse(text) as { detail?: string };
      if (typeof j.detail === "string") message = j.detail;
    } catch {
      /* use text as-is */
    }
    const isServerlessError =
      res.status >= 500 ||
      /FUNCTION_INVOCATION_FAILED|invocation failed|A server error has occurred/i.test(message);
    if (isServerlessError) {
      message =
        'Video service isn\'t available on this deployment. Run locally with "npm run server" + "npm run dev" for videos to work.';
    }
    throw new Error(message || `Failed to generate video (${res.status})`);
  }

  return res.json() as Promise<AnimationResult>;
}

/** Returns true if the video URL is a YouTube embed link */
export function isYouTubeEmbed(url: string): boolean {
  return url.includes("youtube.com/embed") || url.includes("youtu.be");
}
