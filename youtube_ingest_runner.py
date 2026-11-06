import os
import sys
import json
import time
import argparse
import urllib.request
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

DEDUP_VAULT_PATH = PROJECT_ROOT / "storage" / "global_youtube_dedup_vault.json"
CATALOG_PATH = CLUSTER_DIR / "usa_viral_100_catalog.json"
CURATED_PATH = PROJECT_ROOT / "storage" / "first_20_curated_youtube_links.json"

def load_dedup_vault() -> Dict[str, Any]:
    if DEDUP_VAULT_PATH.exists():
        try:
            return json.loads(DEDUP_VAULT_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_to_dedup_vault(video_id: str, metadata: Dict[str, Any]):
    vault = load_dedup_vault()
    vault[video_id] = {
        **metadata,
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    DEDUP_VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEDUP_VAULT_PATH.write_text(json.dumps(vault, indent=2), encoding="utf-8")

def get_channel_info(job_id: int) -> Dict[str, Any]:
    if CATALOG_PATH.exists():
        try:
            cat = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
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
    """Downloads fast 720p H.264 stream via yt-dlp."""
    if not yt_dlp:
        print("[IngestRunner] ❌ Error: yt-dlp is not installed!")
        return None
        
    out_template = str(out_dir / f"ingest_job_{job_id:02d}_%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': out_template,
        'quiet': False,
        'no_warnings': True,
        'merge_output_format': 'mp4'
    }
    
    print(f"[IngestRunner] ⬇️ Ingesting video stream from {video_url}...")
    start_t = time.time()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            # Ensure mp4 extension
            target_path = Path(filename)
            if not target_path.exists():
                alt_path = target_path.with_suffix('.mp4')
                if alt_path.exists():
                    target_path = alt_path
            
            elapsed = time.time() - start_t
            size_mb = target_path.stat().st_size / (1024 * 1024)
            print(f"[IngestRunner] ✓ Download completed in {elapsed:.1f}s: {target_path.name} ({size_mb:.1f} MB)")
            return target_path
    except Exception as e:
        print(f"[IngestRunner] ❌ Download error: {e}")
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

    # 2. Select Video (From Curated List, CLI argument, or Search)
    target_video = None
    vault = load_dedup_vault()
    
    if args.video_url:
        vid_id = args.video_url.split("v=")[-1].split("&")[0]
        target_video = {
            "id": vid_id,
            "url": args.video_url,
            "title": f"Viral Public Docket #{vid_id}",
            "duration_min": 30.0
        }
    elif CURATED_PATH.exists():
        try:
            curated_list = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
            idx = (args.curated_index - 1) if args.curated_index > 0 else (args.job_id - 1) % len(curated_list)
            candidate = curated_list[idx]
            if candidate["id"] in vault:
                print(f"[IngestRunner] ⚠️ Curated candidate {candidate['id']} already in Dedup Vault! Finding next un-ingested...")
                for c in curated_list:
                    if c["id"] not in vault:
                        candidate = c
                        break
            target_video = candidate
        except Exception as e:
            print(f"[IngestRunner] Notice reading curated list: {e}")

    if not target_video:
        print("[IngestRunner] ❌ No target video resolved!")
        sys.exit(1)

    vid_id = target_video["id"]
    print(f"[IngestRunner] 🎯 Selected Target: [{vid_id}] {target_video['title']}")
    print(f"[IngestRunner] ⏱️ Duration:        {target_video.get('duration_min', 0)} mins")

    # 3. Check Deduplication Vault
    if vid_id in vault:
        print(f"[IngestRunner] 🛑 DEDUP VAULT LOCK: Video {vid_id} has already been uploaded! Skipping.")
        sys.exit(0)

    # 4. Download 720p Video Stream
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    video_path = download_youtube_video(target_video["url"], out_dir, args.job_id)
    if not video_path or not video_path.exists():
        print("[IngestRunner] ❌ Failed to download target video!")
        sys.exit(1)

    # 5. Download Original YouTube Thumbnail
    thumb_path = out_dir / f"orig_thumb_{args.job_id}_{vid_id}.jpg"
    thumb_result = download_thumbnail(vid_id, thumb_path)

    # 6. Build SEO & Mid-Roll Chapters
    duration_sec = int(target_video.get("duration_min", 30) * 60)
    ad_chapters = generate_midroll_chapters(duration_sec, ch_info["category"])
    
    clean_title = target_video["title"]
    if len(clean_title) > 88:
        clean_title = clean_title[:85] + "..."

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
            target_channel_id=ch_info.get("id")
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
