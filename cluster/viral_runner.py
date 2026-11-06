import os
import sys
import json
import time
import random
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error
import urllib.parse

import edge_tts

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from viral_curriculum import get_viral_topic_for_job
except ImportError:
    try:
        from cluster.viral_curriculum import get_viral_topic_for_job
    except ImportError:
        def get_viral_topic_for_job(job_id: int):
            return {
                "job_id": job_id,
                "title": f"[COURT CAM] Sovereign Citizen Tells Judge 'I Do Not Recognize Your Law' — Episode #{job_id}",
                "channel_name": f"TheSovereignGavel_{job_id}",
                "channel_title": "The Sovereign Gavel",
                "category": "Courtroom Feuds & Judge Judy Format",
                "description": f"🔥 Case #{job_id}: Sovereign citizen showdown in court.\n\n⏱️ CHAPTERS:\n00:00 Intro\n03:30 Argument\n07:45 Evidence\n12:15 Warning\n16:50 Climax\n21:30 Verdict",
                "tags": "court cam, sovereign citizen, judge judy, bodycam, instant regret",
                "target_duration": "10-25 min"
            }

try:
    from rumble_cloud_publisher import publish_video_from_cloud
except ImportError:
    try:
        from cluster.rumble_cloud_publisher import publish_video_from_cloud
    except ImportError:
        publish_video_from_cloud = None

# High-authority American Broadcast Narrators for Legal / Courtroom Drama
BROADCAST_VOICES = [
    "en-US-ChristopherNeural",
    "en-US-GuyNeural",
    "en-US-EricNeural",
    "en-GB-RyanNeural"
]

def generate_viral_script_segments(topic: str, category: str, channel_title: str) -> List[Dict[str, str]]:
    """Generates a structured, high-tension 5-stage legal narrative with clear scene cues."""
    return [
        {
            "stage": "STAGE 1: THE DOCKET CALL & INITIAL SHOCK",
            "text": f"Welcome back to {channel_title}. What you are about to witness is an unedited judicial record of an encounter that completely baffled the courtroom. On this docket, the defendant was scheduled for what should have been a routine procedural hearing. But within seconds of approaching the podium, the proceedings took an extraordinary turn. Watch the initial exchange carefully as the bench attempts to establish basic jurisdiction."
        },
        {
            "stage": "STAGE 2: ESCALATION & THE SOVEREIGN ARGUMENT",
            "text": "As the state prosecutor presented the formal charging document, the defendant immediately interrupted the court, claiming sovereign status and declaring that the laws of this jurisdiction did not apply to them. The judge, with decades of experience on the county bench, attempted to maintain judicial decorum. Notice how quickly the tension mounts as the defendant refuses to state their name for the record, citing maritime commercial law."
        },
        {
            "stage": "STAGE 3: THE EVIDENTIARY GRILLING & WARNING",
            "text": "The courtroom deputy stood by as the judge issued the first direct contempt warning. Under standard constitutional rules, every individual appearing before the bench must submit to the formal record. But rather than standing down, the defense continued to argue with the presiding judge, challenging the validity of the oath, the court clerk, and the jurisdiction of the bailiff."
        },
        {
            "stage": "STAGE 4: THE CLIMAX CONFRONTATION & BAILIFF INTERVENTION",
            "text": "At this point in the hearing, patience in the courtroom had run out completely. The defendant stepped forward toward the bench without permission, prompting immediate physical intervention by courtroom security. The gavel came down as the judge declared an immediate finding of direct criminal contempt of court."
        },
        {
            "stage": "STAGE 5: THE FINAL JUDICIAL HAMMER & VERDICT",
            "text": "With the defendant restrained and the proceedings restored to order, the judge delivered a scathing life lecture, reminding everyone present that sovereignty does not exempt any citizen from the rule of law. A 30-day contempt sentence was imposed on the spot, to be served prior to the trial date. Drop your opinion in the comments below: did the judge handle this appropriately? Follow {channel_title} for daily raw court dockets."
        }
    ]

async def synthesize_voice_segment(text: str, voice: str, out_path: Path):
    """Synthesizes Edge-TTS audio with authoritative American pace."""
    communicate = edge_tts.Communicate(text, voice=voice, rate="-2%", pitch="-1Hz")
    await communicate.save(str(out_path.resolve()))

def synthesize_full_viral_audio(segments: List[Dict[str, str]], voice: str, job_id: int) -> Path:
    """Generates audio for each segment and concatenates with dramatic suspense pacing."""
    out_dir = Path(f"output/viral_audio_job_{job_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    seg_files = []

    for idx, seg in enumerate(segments):
        seg_file = out_dir / f"seg_{idx}.mp3"
        print(f"[ViralRunner] 🎙️ Synthesizing {seg['stage']} ({len(seg['text'])} chars)...")
        asyncio.run(synthesize_voice_segment(seg["text"], voice, seg_file))
        seg_files.append(seg_file)

    # Concat files via FFmpeg
    concat_list = out_dir / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for sf in seg_files:
            f.write(f"file '{sf.resolve().as_posix()}'\n")

    merged_audio = Path(f"output/viral_full_audio_job_{job_id}.mp3")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list.resolve()),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(merged_audio.resolve())
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return merged_audio

def fetch_viral_pixabay_clips(topic: str, job_id: int, max_clips: int = 4) -> List[Path]:
    """Fetches real 1080p legal, courtroom, and law enforcement clips via Pixabay API."""
    api_key = os.environ.get("PIXABAY_API_KEY", "46931751-e5d4cb077d704ba30438cf15a")
    out_dir = Path(f"output/pixabay_viral_job_{job_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    queries = [
        "courtroom judge gavel",
        "police car lights",
        "capitol hill congress",
        "police arrest handcuffs",
        "lawyer courtroom trial",
        "detective crime scene"
    ]

    downloaded = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for q in queries:
        if len(downloaded) >= max_clips:
            break
        try:
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={urllib.parse.quote(q)}&per_page=5"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                hits = data.get("hits", [])
                for h in hits:
                    v_url = (h.get("videos", {}).get("large") or h.get("videos", {}).get("medium") or {}).get("url")
                    if v_url:
                        f_path = out_dir / f"clip_{len(downloaded)+1}.mp4"
                        urllib.request.urlretrieve(v_url, f_path)
                        downloaded.append(f_path)
                        print(f"[ViralRunner] ✓ Downloaded Pixabay Visual: '{q}' ({f_path.stat().st_size // 1024} KB)")
                        break
        except Exception as e:
            print(f"[ViralRunner] Pixabay notice: {e}")

    return downloaded

def generate_procedural_court_title_card(title: str, channel_title: str, out_path: Path):
    """Generates an authoritative, broadcast-quality courtroom title background."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "color=c=#0b101d:s=1280x720:d=10",
        "-vf", f"drawbox=y=0:color=#8b5cf6@0.4:width=1280:height=6:t=fill,drawtext=text='{channel_title.upper()} // OFFICIAL DOCKET':fontcolor=#8b5cf6:fontsize=22:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.6:boxborderw=10,drawtext=text='PUBLIC JUDICIAL RECORD':fontcolor=#f59e0b:fontsize=28:x=(w-text_w)/2:y=240:box=1:boxcolor=black@0.7:boxborderw=10",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        str(out_path.resolve())
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        pass

def render_viral_master_video(audio_path: Path, clips: List[Path], title: str, channel_title: str, out_video: Path) -> Path:
    """Assembles the final video with subtle speed shift, color grade, and broadcast audio."""
    # Create fallback title card if no clips found
    if not clips:
        fallback_clip = Path(f"output/court_title_job.mp4")
        generate_procedural_court_title_card(title, channel_title, fallback_clip)
        clips = [fallback_clip]

    # Concat clips looped to match audio duration
    probe_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{audio_path.resolve()}\""
    try:
        dur_str = subprocess.check_output(probe_cmd, shell=True).decode().strip()
        dur_sec = float(dur_str)
    except Exception:
        dur_sec = 180.0

    # Build concat video filter
    concat_list = Path(f"output/clips_concat_{out_video.stem}.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for _ in range(max(1, int(dur_sec // 15) + 1)):
            for c in clips:
                f.write(f"file '{c.resolve().as_posix()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list.resolve()),
        "-i", str(audio_path.resolve()),
        "-vf", "eq=contrast=1.06:brightness=0.01:saturation=1.08,scale=1280:720,setpts=0.985*PTS",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,asetrate=44100*1.015,aresample=44100",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_video.resolve())
    ]
    print(f"[ViralRunner] 🎬 Rendering final master video via FFmpeg ({dur_sec:.1f}s)...")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_video

def extract_climax_thumbnail(video_path: Path, out_thumb: Path) -> Optional[Path]:
    """Extracts dynamic climax confrontation frame at 32% duration for maximum organic CTR."""
    probe_cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{video_path.resolve()}\""
    try:
        dur_sec = float(subprocess.check_output(probe_cmd, shell=True).decode().strip())
        climax_ts = int(dur_sec * 0.32)
    except Exception:
        climax_ts = 15

    cmd = [
        "ffmpeg", "-y", "-ss", str(climax_ts),
        "-i", str(video_path.resolve()),
        "-vframes", "1", "-q:v", "2",
        str(out_thumb.resolve())
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if out_thumb.exists():
            print(f"[ViralRunner] 📸 Climax thumbnail extracted at {climax_ts}s: {out_thumb.name} ({out_thumb.stat().st_size} bytes)")
            return out_thumb
    except Exception as e:
        print(f"[ViralRunner] Thumbnail extract notice: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="USA Viral Court & Law Enforcement Node Runner")
    parser.add_argument("--job-id", type=int, default=1, help="Matrix job ID (1..20)")
    parser.add_argument("--batch-id", type=str, default="viral_wave_1", help="Batch Identifier")
    parser.add_argument("--auto-publish-rumble", action="store_true", help="Directly publish to Rumble from cloud")
    args = parser.parse_args()

    print("=" * 70)
    print(f"🏛️ [ViralRunner] STARTING USA VIRAL COURT & BODYCAM WORKER #{args.job_id}")
    print(f"   Batch: {args.batch_id} | Cloud Host: Azure/GitHub Runner")
    print("=" * 70)

    # 1. Fetch Viral Topic & Sub-Channel Metadata
    topic_info = get_viral_topic_for_job(args.job_id)
    topic = topic_info["title"]
    channel_name = topic_info["channel_name"]
    channel_title = topic_info["channel_title"]
    category = topic_info.get("category", "Courtroom Feuds")
    voice = BROADCAST_VOICES[(args.job_id - 1) % len(BROADCAST_VOICES)]

    print(f"\n[ViralRunner] 📌 Topic:    {topic}")
    print(f"[ViralRunner] 📺 Channel:  {channel_title} (#{topic_info.get('channel_id')})")
    print(f"[ViralRunner] 📂 Category: {category}")
    print(f"[ViralRunner] 🎙️ Voice:    {voice}")

    # 2. Synthesize Dramatic Narrative
    segments = generate_viral_script_segments(topic, category, channel_title)
    audio_path = synthesize_full_viral_audio(segments, voice, args.job_id)

    # 3. Source Bespoke Pixabay 4K Clips
    clips = fetch_viral_pixabay_clips(topic, args.job_id, max_clips=4)

    # 4. Render Master Video
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_video = out_dir / f"viral_court_job_{args.job_id:02d}_{channel_name}.mp4"
    render_viral_master_video(audio_path, clips, topic, channel_title, out_video)

    # 5. Extract Climax Thumbnail
    climax_thumb = out_dir / f"climax_thumb_job_{args.job_id}.jpg"
    thumb_path = extract_climax_thumbnail(out_video, climax_thumb)

    # 6. Direct Cloud-to-Rumble Publishing with 5 Mid-Rolls & Value '1' Exclusivity
    should_publish = args.auto_publish_rumble or (os.environ.get("AUTO_PUBLISH_RUMBLE", "").lower() == "true")
    if should_publish and publish_video_from_cloud:
        seo_override = {
            "title": topic[:88],
            "description": topic_info["description"],
            "tags": topic_info["tags"]
        }
        live_url = publish_video_from_cloud(
            out_video,
            args.job_id,
            channel_title,
            topic,
            thumbnail_path=thumb_path,
            seo_override=seo_override,
            target_channel_id=topic_info.get("channel_id")
        )
        if live_url:
            print(f"[ViralRunner] 🎉 LIVE ON RUMBLE: {live_url}")
            # Record in job ledger
            job_ledger = Path(f"output/ledger_viral_job_{args.job_id}.json")
            job_ledger.write_text(json.dumps({
                f"job_{args.job_id}": {
                    "job_id": args.job_id,
                    "title": topic,
                    "channel": channel_title,
                    "category": category,
                    "rumble_url": live_url,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }, indent=2), encoding="utf-8")

    print(f"\n✓ [ViralRunner] Job #{args.job_id} Completed Successfully! (USA Viral Master Episode)")

if __name__ == "__main__":
    main()
