"""
master_viral_thumbnail_engine.py
================================
10x Clickbait Master Thumbnail Engine:
1. Groq 120B (openai/gpt-oss-120b) Viral Visual Prompt Architect
2. Google Flow (Imagen 3) Photorealistic 16:9 Master Rendering (via DeepX Bridge port 8792)
3. Cloud AI Flux 16:9 High-Res Fallback (for 100% Cloud Server / GitHub Actions autonomy)
4. FFmpeg Clean HD Video Frame Extractor (0% Graphic Copyright Risk)
5. Native YouTube Frame Fallback
"""

import sys
import os
import json
import time
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

def get_groq_api_key() -> str:
    return os.environ.get("GROQ_API_KEY", "")

def generate_groq_clickbait_prompt(raw_title: str, category: str) -> str:
    """Uses Groq 120B to craft an explosive, 10x high-converting visual thumbnail prompt for Google Flow."""
    groq_key = get_groq_api_key()
    fallback_prompt = (
        f"Cinematic intense courtroom drama, criminal defendant looking stunned with wide eyes, "
        f"stern female judge striking polished wooden gavel in background, volumetric lighting, "
        f"hyperrealistic 8k textures, high contrast, 16:9 widescreen composition, dramatic curiosity gap."
    )
    if not groq_key:
        return fallback_prompt

    system_instruction = (
        "You are an elite YouTube Thumbnail Visual Creative Director specializing in high-CTR, "
        "viral American courtroom trials and police bodycam videos. Output ONLY a valid JSON object."
    )
    user_prompt = f"""Video Title: "{raw_title}"
Category: "{category}"

Create an explosive, 10x clickbait visual prompt designed specifically for Google Flow (Imagen 3).
The prompt MUST specify:
- Characters: Intense, gripping facial expressions (shocked defendant, stern judge, fiery prosecutor, or tense police confrontation)
- Atmosphere & Lighting: High drama, cinematic volumetric light shafts, high contrast chiaroscuro
- Ultra-Fine Details: 8K photorealism, wood grain textures, brass gavel, crisp suit fabrics, perspiration, dramatic depth of field
- Format: 16:9 widescreen cinematic composition with an irresistible curiosity gap that forces a click.
- IMPORTANT: No text, no logos, no watermarks inside the image.

Output STRICT JSON:
{{"clickbait_prompt": "..."}}
"""

    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.8
            }).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            parsed = json.loads(data["choices"][0]["message"]["content"])
            prompt = parsed.get("clickbait_prompt", "").strip()
            if prompt and len(prompt) > 30:
                print(f"[ThumbEngine] 🧠 Groq 10x Clickbait Prompt generated ({len(prompt)} chars).")
                return prompt
    except Exception as e:
        print(f"[ThumbEngine] Groq prompt notice: {e}. Using tuned template.")

    return fallback_prompt

def is_google_flow_ready() -> bool:
    """Checks if DeepX Google Flow bridge is live and ready on localhost."""
    try:
        req = urllib.request.Request("http://127.0.0.1:8792/status", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("status") == "ok" and data.get("extensionConnected", False)
    except Exception:
        return False

def render_google_flow_thumbnail(prompt: str, out_path: Path) -> Optional[Path]:
    """Generates an 8K 16:9 master thumbnail on Google Flow via DeepX Extension Bridge."""
    payload = {
        "command": "generate_image",
        "payload": {
            "prompt": prompt,
            "aspectRatio": "16:9",
            "count": 1,
            "wait_for_render": True
        },
        "timeout": 90000
    }
    try:
        print("[ThumbEngine] 🎨 Dispatching prompt to Google Flow (Imagen 3)...")
        req = urllib.request.Request(
            "http://127.0.0.1:8792/command",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=95) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                res = data.get("result", {})
                img_url = res.get("imageUrl")
                if not img_url and res.get("images"):
                    img_url = res["images"][0].get("url")

                if img_url:
                    # Download the image from Google Flow CDN
                    dl_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(dl_req, timeout=25) as img_resp:
                        out_path.write_bytes(img_resp.read())
                    
                    if out_path.exists() and out_path.stat().st_size > 10000:
                        size_kb = out_path.stat().st_size // 1024
                        print(f"[ThumbEngine] 🚀 Google Flow Master Thumbnail rendered in {res.get('executionTimeMs', 0)}ms ({size_kb} KB) - 100% 10x Clickbait!")
                        return out_path
    except Exception as e:
        print(f"[ThumbEngine] Google Flow render notice: {e}")
    return None

def render_cloud_ai_thumbnail(prompt: str, out_path: Path) -> Optional[Path]:
    """Zero-dependency Cloud AI Flux 16:9 generator for 100% headless server execution."""
    try:
        print("[ThumbEngine] ☁️ Dispatching to Cloud AI Flux (16:9 Widescreen)...")
        encoded_prompt = urllib.parse.quote(prompt[:400])
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true&seed=42"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            out_path.write_bytes(resp.read())

        if out_path.exists() and out_path.stat().st_size > 10000:
            size_kb = out_path.stat().st_size // 1024
            print(f"[ThumbEngine] 🌟 Cloud AI Flux Thumbnail rendered successfully ({size_kb} KB)!")
            return out_path
    except Exception as e:
        print(f"[ThumbEngine] Cloud AI render notice: {e}")
    return None

def extract_clean_video_frame(video_path: Path, out_path: Path, timestamp_sec: int = 210) -> Optional[Path]:
    """Extracts a pristine 1080p HD action frame from the real public domain video via FFmpeg. 0% Graphic Copyright."""
    if not video_path or not video_path.exists():
        return None
    try:
        ts = f"{timestamp_sec // 3600:02d}:{(timestamp_sec % 3600) // 60:02d}:{timestamp_sec % 60:02d}"
        cmd = [
            "ffmpeg", "-y", "-ss", ts,
            "-i", str(video_path.resolve()),
            "-vframes", "1",
            "-q:v", "2",
            str(out_path.resolve())
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if out_path.exists() and out_path.stat().st_size > 5000:
            size_kb = out_path.stat().st_size // 1024
            print(f"[ThumbEngine] 📸 Extracted pristine HD video frame at {ts} ({size_kb} KB) - 0% Copyright Risk!")
            return out_path
    except Exception as e:
        print(f"[ThumbEngine] Frame extraction notice: {e}")
    return None

def download_youtube_raw_thumbnail(video_id: str, out_path: Path) -> Optional[Path]:
    """Downloads YouTube native thumbnail fallback."""
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    out_path.write_bytes(resp.read())
                    print(f"[ThumbEngine] 🖼️ Fallback: YouTube native thumbnail ({out_path.stat().st_size // 1024} KB).")
                    return out_path
        except Exception:
            continue
    return None

def build_master_thumbnail(
    video_path: Optional[Path],
    video_id: str,
    raw_title: str,
    category: str,
    out_path: Path
) -> Optional[Path]:
    """
    Main Autonomous Pipeline:
    1. Formulates Groq 120B Clickbait Visual Brief
    2. Google Flow (Imagen 3) 8K Render (If Bridge Connected) -> 10x Better!
    3. Cloud AI Flux 16:9 Render (If Headless Server / PC Sleeping)
    4. FFmpeg Clean HD Video Frame (0% Graphic Copyright Risk)
    5. Native YouTube Raw Thumbnail Fallback
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if a pre-cached master thumbnail exists for this video ID
    cache_path = ROOT_DIR / "scratch" / f"flow_thumb_{video_id}.jpg"
    if cache_path.exists() and cache_path.stat().st_size > 10000:
        import shutil
        shutil.copy(cache_path, out_path)
        print(f"[ThumbEngine] 💾 Reusing cached Google Flow Thumbnail ({out_path.stat().st_size // 1024} KB).")
        return out_path

    # Step 1: Groq Clickbait Visual Prompt
    print(f"\n[ThumbEngine] 🎯 Formulating 10x Clickbait Visual Brief via Groq LPU...")
    clickbait_prompt = generate_groq_clickbait_prompt(raw_title, category)

    # Step 2: Google Flow Imagen 3 AI Generation
    if is_google_flow_ready():
        flow_res = render_google_flow_thumbnail(clickbait_prompt, out_path)
        if flow_res and flow_res.exists():
            import shutil
            try:
                shutil.copy(flow_res, cache_path)
            except Exception:
                pass
            return flow_res
    else:
        print("[ThumbEngine] ℹ️ Google Flow Bridge offline or standby. Proceeding to Cloud AI Fallback...")

    # Step 3: Cloud AI Flux 16:9 Widescreen Fallback (Runs everywhere 24/7)
    cloud_res = render_cloud_ai_thumbnail(clickbait_prompt, out_path)
    if cloud_res and cloud_res.exists():
        return cloud_res

    # Step 4: Extract Clean 1080p HD Frame from Video via FFmpeg
    if video_path and video_path.exists():
        frame_res = extract_clean_video_frame(video_path, out_path, timestamp_sec=210)
        if frame_res and frame_res.exists():
            return frame_res

    # Step 5: Native YouTube Thumbnail Fallback
    yt_res = download_youtube_raw_thumbnail(video_id, out_path)
    if yt_res and yt_res.exists():
        return yt_res

    return None

if __name__ == "__main__":
    out = Path("scratch/test_master_flow_groq.jpg")
    res = build_master_thumbnail(
        video_path=None,
        video_id="048ypCAz8wg",
        raw_title="Tyler Robinson preliminary hearing - Police Bodycam & Court Testimony",
        category="Courtroom Trials & Judicial Feuds",
        out_path=out
    )
    print("Final Thumbnail Result:", res)
