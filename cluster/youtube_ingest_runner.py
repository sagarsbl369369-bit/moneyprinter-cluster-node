import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
CLUSTER_DIR = Path(__file__).resolve().parent
if str(CLUSTER_DIR) not in sys.path:
    sys.path.insert(0, str(CLUSTER_DIR))

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from rumble_cloud_publisher import publish_video_from_cloud, get_subchannel_id
except ImportError:
    try:
        from cluster.rumble_cloud_publisher import publish_video_from_cloud, get_subchannel_id
    except ImportError:
        publish_video_from_cloud = None
        get_subchannel_id = None

try:
    from viral_runner import (
        generate_viral_script_segments,
        synthesize_full_viral_audio,
        fetch_viral_pixabay_clips,
        render_viral_master_video,
        extract_climax_thumbnail,
        BROADCAST_VOICES
    )
except ImportError:
    try:
        from cluster.viral_runner import (
            generate_viral_script_segments,
            synthesize_full_viral_audio,
            fetch_viral_pixabay_clips,
            render_viral_master_video,
            extract_climax_thumbnail,
            BROADCAST_VOICES
        )
    except ImportError:
        BROADCAST_VOICES = ["en-US-ChristopherNeural", "en-US-GuyNeural"]
        generate_viral_script_segments = None

def get_curated_path() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent / "first_20_curated_youtube_links.json",
        Path(__file__).resolve().parent / "storage" / "first_20_curated_youtube_links.json",
        PROJECT_ROOT / "storage" / "first_20_curated_youtube_links.json"
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def get_catalog_path() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent / "usa_viral_100_catalog.json",
        Path(__file__).resolve().parent / "cluster" / "usa_viral_100_catalog.json",
        PROJECT_ROOT / "cluster" / "usa_viral_100_catalog.json"
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def load_dedup_vault() -> Dict[str, Any]:
    vault_candidates = [
        Path(__file__).resolve().parent / "global_youtube_dedup_vault.json",
        Path(__file__).resolve().parent / "storage" / "global_youtube_dedup_vault.json",
        PROJECT_ROOT / "storage" / "global_youtube_dedup_vault.json"
    ]
    for p in vault_candidates:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}

def save_to_dedup_vault(video_id: str, metadata: Dict[str, Any]):
    vault = load_dedup_vault()
    vault[video_id] = {
        **metadata,
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    # Save to all accessible locations
    paths = [
        Path(__file__).resolve().parent / "global_youtube_dedup_vault.json",
        PROJECT_ROOT / "storage" / "global_youtube_dedup_vault.json"
    ]
    for p in paths:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(vault, indent=2), encoding="utf-8")
        except Exception:
            pass

def get_channel_info(job_id: int) -> Dict[str, Any]:
    c_path = get_catalog_path()
    if c_path and c_path.exists():
        try:
            cat = json.loads(c_path.read_text(encoding="utf-8"))
            if cat:
                return cat[(job_id - 1) % len(cat)]
        except Exception:
            pass
    return {
        "id": job_id,
        "name": f"USAViralDesk_{job_id}",
        "title": f"USA Viral Desk #{job_id}",
        "category": "Courtroom Feuds & Gavel-to-Gavel Dockets"
    }

def download_thumbnail(video_id: str, out_path: Path) -> Optional[Path]:
    """Downloads highest available thumbnail from YouTube CDN."""
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    out_path.write_bytes(resp.read())
                    print(f"[IngestRunner] 🖼️ Downloaded original thumbnail from {url} ({out_path.stat().st_size // 1024} KB)")
                    return out_path
        except Exception:
            continue
    return None

def generate_midroll_chapters(duration_sec: int, category: str) -> str:
    """Generates structured chapter cues every 6 minutes to maximize Rumble mid-roll ad fills."""
    interval = 360  # 6 minutes
    total_chapters = max(1, duration_sec // interval)
    
    chapter_themes = [
        "Case Opening & Formal Docket Call",
        "Initial Statements & High-Tension Objections",
        "Key Evidentiary Review & Frontline Breakdown",
        "Heated Cross-Examination & Warning",
        "Unsealed Records & Crucial Evidence",
        "Climax Confrontation & Security / Bailiff Action",
        "Closing Arguments & Witness Retraction",
        "Final Judicial Hammer & Official Verdict"
    ]
    
    lines = ["\n⏱️ OFFICIAL CHAPTERS & AD CUE TIMESTAMPS:"]
    for i in range(total_chapters + 1):
        cur_sec = i * interval
        if cur_sec > duration_sec:
            break
        mins = cur_sec // 60
        secs = cur_sec % 60
        theme = chapter_themes[i % len(chapter_themes)]
        lines.append(f"{mins:02d}:{secs:02d} - {theme} (Part {i+1})")
        
    return "\n".join(lines)

def download_youtube_video(video_url: str, out_dir: Path, job_id: int) -> Optional[Path]:
    """Downloads fast 720p H.264 stream via yt-dlp with Node.js n-challenge solving."""
    if not yt_dlp:
        print("[IngestRunner] ❌ Error: yt-dlp is not installed!")
        return None
        
    out_template = str(out_dir / f"ingest_job_{job_id:02d}_%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestvideo*+bestaudio/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web', 'tv']
            }
        },
        'outtmpl': out_template,
        'quiet': False,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'remote_components': ['ejs:github'],
        'js_runtimes': {'node': {}}
    }

    # Detect node binary across Windows, Ubuntu Linux, and macOS
    node_cmd = shutil.which("node") or shutil.which("nodejs")
    if not node_cmd:
        for p in ["/usr/bin/node", "/usr/local/bin/node", r"C:\Users\Sagar Agarwal\.gemini\antigravity\bin\node.cmd"]:
            if Path(p).exists():
                node_cmd = p
                break
    if node_cmd:
        ydl_opts['js_runtimes'] = {'node': {'path': str(node_cmd)}}
        print(f"[IngestRunner] ⚡ Linked Node.js JS challenge solver: {node_cmd}")

    # Pass 1: Clean stream without datacenter cookie invalidation
    cookie_file = None
    cookie_candidates = [
        Path("youtube_cookies.txt"),
        Path("storage/youtube_cookies.txt"),
        PROJECT_ROOT / "storage" / "youtube_cookies.txt"
    ]
    for c in cookie_candidates:
        if c.exists() and c.stat().st_size > 100:
            cookie_file = str(c.resolve())
            break

    print(f"[IngestRunner] ⬇️ Ingesting video stream from {video_url}...")
    start_t = time.time()
    
    # Try first with clean datacenter-friendly options (no stale cookie rejection)
    for attempt, use_cookie in enumerate([False, True], 1):
        attempt_opts = dict(ydl_opts)
        if use_cookie and cookie_file:
            attempt_opts['cookiefile'] = cookie_file
            print(f"[IngestRunner] 🍪 Pass {attempt}: Retrying with authenticated session cookies...")
        elif attempt > 1:
            break

        try:
            with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                target_path = Path(filename)
                if not target_path.exists():
                    for ext in [".mp4", ".mkv", ".webm"]:
                        alt = target_path.with_suffix(ext)
                        if alt.exists():
                            target_path = alt
                            break
                
                if target_path.exists() and target_path.stat().st_size > 1000000:
                    elapsed = time.time() - start_t
                    size_mb = target_path.stat().st_size / (1024 * 1024)
                    print(f"[IngestRunner] ✓ Real Video Download completed in {elapsed:.1f}s: {target_path.name} ({size_mb:.1f} MB)")
                    return target_path
        except Exception as e:
            print(f"[IngestRunner] ⚠️ Pass {attempt} notice: {e}")
            if not use_cookie and cookie_file:
                continue
            break

    print(f"[IngestRunner] ❌ Failed to download {video_url}")
    return None

def main():
    parser = argparse.ArgumentParser(description="YouTube-to-Rumble Viral Ingestion Engine")
    parser.add_argument("--job-id", type=int, default=1, help="Matrix Runner Job ID (1..20)")
    parser.add_argument("--video-url", type=str, default="", help="Direct YouTube URL override")
    parser.add_argument("--curated-index", type=int, default=0, help="1-based index from curated list")
    parser.add_argument("--auto-publish-rumble", action="store_true", help="Auto-publish to Rumble")
    args = parser.parse_args()

    print("=" * 70)
    print(f"🏛️ [IngestRunner] VIRAL YOUTUBE-TO-RUMBLE WORKER #{args.job_id}")
    print(f"   Mode: Public Record / FOIA Ingestion | Zero-Duplication Protected")
    print("=" * 70)

    # 1. Resolve Target Channel
    ch_info = get_channel_info(args.job_id)
    print(f"[IngestRunner] 📺 Target Channel: {ch_info['title']} ({ch_info.get('handle', ch_info['name'])})")
    print(f"[IngestRunner] 📂 Category:       {ch_info['category']}")

    # 2. Select Video & Download Real Stream (with genuine candidate fallback)
    vault = load_dedup_vault()
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    target_video = None
    video_path = None

    if args.video_url:
        vid_id = args.video_url.split("v=")[-1].split("&")[0]
        c = {
            "id": vid_id,
            "url": args.video_url,
            "title": f"Viral Public Docket #{vid_id}",
            "duration_min": 30.0
        }
        if vid_id not in vault:
            v_path = download_youtube_video(c["url"], out_dir, args.job_id)
            if v_path and v_path.exists() and v_path.stat().st_size > 1000000:
                target_video = c
                video_path = v_path

    if not video_path:
        curated_path = get_curated_path()
        curated_list = []
        if curated_path and curated_path.exists():
            try:
                curated_list = json.loads(curated_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        if curated_list:
            start_idx = (args.curated_index - 1) if args.curated_index > 0 else (args.job_id - 1)
            candidate_indices = [(start_idx + i) % len(curated_list) for i in range(len(curated_list))]
            for c_idx in candidate_indices:
                candidate = curated_list[c_idx]
                if candidate["id"] in vault:
                    continue
                print(f"[IngestRunner] 🎯 Trying Candidate: [{candidate['id']}] {candidate['title']}")
                v_path = download_youtube_video(candidate["url"], out_dir, args.job_id)
                if v_path and v_path.exists() and v_path.stat().st_size > 1000000:
                    target_video = candidate
                    video_path = v_path
                    break
                else:
                    print(f"[IngestRunner] ⚠️ Candidate [{candidate['id']}] stream unavailable. Advancing to next genuine candidate...")

    if not video_path or not target_video:
        print("[IngestRunner] ❌ Error: No genuine YouTube video stream could be downloaded.")
        print("[IngestRunner] 🛑 Strict Channel Authenticity Enforced: Skipping this job (ZERO FAKE AI SYNTHETIC VIDEOS).")
        sys.exit(1)

    vid_id = target_video["id"]
    print(f"[IngestRunner] ✓ LOCKED TARGET: [{vid_id}] {target_video['title']}")
    print(f"[IngestRunner] ⏱️ Duration:      {target_video.get('duration_min', 0)} mins")

    clean_title = target_video["title"]
    if len(clean_title) > 88:
        clean_title = clean_title[:85] + "..."

    # Master 10x Clickbait Thumbnail Engine (Google Flow / Flux AI / Saturated Climax Frame)
    thumb_path = out_dir / f"master_thumb_{args.job_id}_{vid_id}.jpg"
    thumb_result = None
    try:
        from master_viral_thumbnail_engine import build_master_thumbnail
        thumb_result = build_master_thumbnail(video_path, vid_id, clean_title, ch_info["category"], thumb_path)
    except Exception as te:
        print(f"[IngestRunner] Master thumb notice: {te}. Extracting 1080p climax frame with FFmpeg...")

    if not thumb_result or not Path(thumb_result).exists():
        try:
            dur_sec = int(target_video.get("duration_min", 30) * 60)
            sample_sec = max(60, int(dur_sec * 0.15))
            m = sample_sec // 60
            s = sample_sec % 60
            ts_str = f"00:{m:02d}:{s:02d}"
            # Extract vibrant, high-contrast 1080p frame with FFmpeg
            cmd = [
                "ffmpeg", "-y", "-ss", ts_str, "-i", str(video_path),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,eq=contrast=1.18:saturation=1.25",
                "-vframes", "1", "-q:v", "2", str(thumb_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            if thumb_path.exists() and thumb_path.stat().st_size > 10000:
                thumb_result = thumb_path
                print(f"[IngestRunner] 🖼️ Extracted 1080p Saturated Climax Thumbnail ({thumb_path.stat().st_size // 1024} KB)!")
        except Exception as fe:
            print(f"[IngestRunner] Frame extract notice: {fe}")

    if not thumb_result or not Path(thumb_result).exists():
        thumb_result = download_thumbnail(vid_id, thumb_path)

    # 5. Build 10x Groq SEO & Mid-Roll Chapters (with anti-429 jitter & retries)
    duration_min = target_video.get("duration_min", 30.0)
    groq_key = os.environ.get("GROQ_API_KEY", "")
    seo_res = None
    if groq_key:
        time.sleep((args.job_id % 6) * 2 + 1)
        for attempt in range(3):
            try:
                prompt = f"""You are a World-Class Viral Media Director & American Courtroom/Police Bodycam SEO Expert.
Generate high-converting, 10x better than human SEO metadata for this YouTube public record video:
Raw Title: "{target_video['title']}"
Target Channel: "{ch_info['title']}"
Category: "{ch_info['category']}"
Duration: {duration_min} minutes

Generate strict JSON with:
1. "viral_title": Under 88 characters. High CTR, explosive tension, captivating.
2. "viral_description": High-engagement description with explosive legal summary, discussion question to drive comments, and official 6-minute mid-roll chapter timestamps up to {int(duration_min)} mins.
3. "high_cpm_tags": 8-12 comma separated viral tags for maximum US advertiser CPM.
"""
                payload = {
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {"role": "system", "content": "You are a master viral SEO metadata engine. Output valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7
                }
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    seo_res = json.loads(data["choices"][0]["message"]["content"])
                    print(f"[IngestRunner] 🧠 Groq 10x SEO Title: {seo_res.get('viral_title')}")
                    break
            except urllib.error.HTTPError as he:
                if he.code == 429:
                    wait_sec = 4 * (attempt + 1)
                    print(f"[IngestRunner] Groq HTTP 429 Rate Limit. Backing off {wait_sec}s (Attempt {attempt+1}/3)...")
                    time.sleep(wait_sec)
                    continue
                else:
                    print(f"[IngestRunner] Groq SEO HTTP Error {he.code}: {he}")
                    break
            except Exception as ge:
                print(f"[IngestRunner] Groq SEO notice: {ge}")
                break

    if seo_res and seo_res.get("viral_title"):
        clean_title = seo_res["viral_title"][:88].strip()
        description = seo_res["viral_description"]
        tags = seo_res["high_cpm_tags"]
    else:
        duration_sec = int(duration_min * 60)
        ad_chapters = generate_midroll_chapters(duration_sec, ch_info["category"])
        description = f"""🔥 VIRAL PUBLIC DOCKET: {target_video['title']}
Presented exclusively by {ch_info['title']}. Raw, unfiltered public record proceeding released under US Public Sunshine & Freedom of Information laws.

💬 DISCUSSION QUESTION:
Did the judge, officer, or committee handle this situation appropriately? Share your legal analysis in the comments below!

🔔 Follow {ch_info['title']} for daily unfiltered public records, court cams, and bodycam releases.
{ad_chapters}
"""
        tags = f"{ch_info['name'].lower()}, public record, court cam, bodycam, foia, raw uncut, rumble viral, usa legal"

    seo_override = {
        "title": clean_title,
        "description": description,
        "tags": tags
    }

    # 7. Publish to Rumble (with Value '1' Exclusivity & Sub-Channel Lock)
    should_publish = args.auto_publish_rumble or (os.environ.get("AUTO_PUBLISH_RUMBLE", "").lower() == "true")
    live_url = None
    if should_publish and publish_video_from_cloud:
        print(f"[IngestRunner] 🚀 Dispatching to Rumble Cloud Publisher...")
        live_url = publish_video_from_cloud(
            video_path,
            args.job_id,
            ch_info["title"],
            clean_title,
            thumbnail_path=thumb_result,
            seo_override=seo_override,
            target_channel_id=None
        )

    if live_url:
        print(f"[IngestRunner] 🎉 LIVE ON RUMBLE: {live_url}")
        # Commit to Dedup Vault
        save_to_dedup_vault(vid_id, {
            "title": target_video["title"],
            "url": target_video["url"],
            "channel_title": ch_info["title"],
            "channel_id": ch_info.get("id"),
            "rumble_url": live_url,
            "duration_min": target_video.get("duration_min", 0)
        })
        # Record in job ledger
        job_ledger = Path(f"output/ledger_viral_job_{args.job_id}.json")
        job_ledger.write_text(json.dumps({
            f"job_{args.job_id}": {
                "job_id": args.job_id,
                "video_id": vid_id,
                "title": clean_title,
                "channel": ch_info["title"],
                "category": ch_info["category"],
                "rumble_url": live_url,
                "youtube_source": target_video["url"],
                "status": "LIVE"
            }
        }, indent=2), encoding="utf-8")
    else:
        print("[IngestRunner] ⚠️ Live URL not returned (or auto-publish disabled).")

    # 8. Clean up local MP4 to save runner disk space
    try:
        if video_path.exists():
            video_path.unlink()
            print(f"[IngestRunner] 🧹 Cleaned up local video file {video_path.name} to preserve runner disk space.")
    except Exception:
        pass

    print("[IngestRunner] 🏁 Worker finished successfully!")

if __name__ == "__main__":
    main()
