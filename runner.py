import os
import sys
import json
import time
import random
import asyncio
import argparse
import subprocess
from pathlib import Path
import urllib.request

import edge_tts
import requests

# 🎬 100% PURE FINANCIAL & TRADING ASSET POOL (Verified Pixabay 4K / 1080p direct URLs)
TRADING_ASSET_URLS = [
    # Hero: Candlestick, Bloomberg, Order Books, Trader Desks
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2021/04/12/70845-536486027_large.mp4", "name": "candlestick_wave.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2023/10/24/186358-877894520_large.mp4", "name": "bloomberg_screen.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2020/09/16/50130-460456184_large.mp4", "name": "crypto_trader_desk.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2023/06/15/167295-837090885_large.mp4", "name": "trading_chart_analysis.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2022/11/06/137958-768297746_large.mp4", "name": "mobile_trade_execution.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2023/11/02/187515-880629731_large.mp4", "name": "global_market_matrix.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2021/08/04/83897-584067963_large.mp4", "name": "neon_candlestick_depth.mp4"},
    {"type": "hero", "url": "https://cdn.pixabay.com/video/2020/05/25/40149-425026909_large.mp4", "name": "currency_depth_hologram.mp4"},
    
    # Bridge: Wall Street Floors, High-Frequency Server Corridors, Financial Skylines, Currency
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2020/02/14/32338-392150379_large.mp4", "name": "wallstreet_floor.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2022/10/18/135398-761917719_large.mp4", "name": "server_fiber_corridor.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2021/04/18/71378-538605068_large.mp4", "name": "enterprise_datacenter.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2020/04/10/35658-408107954_large.mp4", "name": "server_racks_blinking.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2022/03/17/111059-689849265_large.mp4", "name": "financial_district_night.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2023/04/14/158784-817650393_large.mp4", "name": "financial_skyline_aerial.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2020/07/04/43834-437500589_large.mp4", "name": "counting_usd_cash.mp4"},
    {"type": "bridge", "url": "https://cdn.pixabay.com/video/2021/05/11/73775-548906378_large.mp4", "name": "physical_gold_bitcoin.mp4"}
]

# 8 High-Retention English Psychological Trading Topics
ENGLISH_TOPIC_REGISTRY = [
    {
        "title": "Why 99% Of Traders Fail: The Market Maker Liquidity Trap Explained",
        "voice": "en-US-ChristopherNeural",
        "channel": "SmartMoneyAlpha"
    },
    {
        "title": "The Order Block Playbook: How Central Banks Accumulate Billions Discreetly",
        "voice": "en-US-GuyNeural",
        "channel": "OrderBlockElite"
    },
    {
        "title": "Fair Value Gaps Revealed: Exploiting Institutional Price Delivery Inefficiencies",
        "voice": "en-GB-RyanNeural",
        "channel": "FairValueGapHQ"
    },
    {
        "title": "London & New York Killzones: How Algorithms Hunt Retail Stop-Losses At Open",
        "voice": "en-US-EricNeural",
        "channel": "KillzoneSniper"
    },
    {
        "title": "The 1:3 Asymmetric Risk Model: Why 35% Win Rate Generates Millions",
        "voice": "en-US-ChristopherNeural",
        "channel": "RiskRewardMaster"
    },
    {
        "title": "Dark Pools And Iceberg Orders: Reading Hidden Institutional Footprints",
        "voice": "en-US-GuyNeural",
        "channel": "InstitutionalFlow"
    },
    {
        "title": "Candlestick Psychology: What High-Frequency Market Makers Hide Behind The Wicks",
        "voice": "en-GB-RyanNeural",
        "channel": "CandlePsychology"
    },
    {
        "title": "The Top 1% Trader Mindset: Eliminating Cognitive Bias In High-Stakes Execution",
        "voice": "en-US-EricNeural",
        "channel": "TopOnePercentTrader"
    }
]

def generate_groq_script(topic: str, groq_key: str) -> dict:
    print(f"\n[1/5] Generating 12-Min Script with Groq API for: {topic}...")
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json",
        "User-Agent": "Moneyprinter-Cluster/1.0"
    }
    
    prompt = f"""Write an elite, deeply analytical 12-minute financial documentary script on the topic: '{topic}'.
Structure it strictly into 8 numbered acts:
Act 1: The Retail Mirage & Cognitive Trap
Act 2: Auction Mechanics & Level 2 Order Book Reality
Act 3: Incontrovertible Institutional Footprints (Displacement & Volume)
Act 4: Fair Value Gap Mechanics & Inefficiency Mitigation
Act 5: Session Timing & Algorithmic Killzones (London/NY Opens)
Act 6: The 3-Step Sniper Execution Model
Act 7: Asymmetric Mathematics (1:3 Risk-to-Reward Dominance)
Act 8: The Top 1% Institutional Trader Mindset

Write strictly spoken voiceover prose without emojis, speaker names, or stage directions. Total words: 1,800 to 2,200 words."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a master institutional trading documentary scriptwriter like Michael Lewis and Ray Dalio. Write immersive spoken narrative."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            print(f"✓ Script generated successfully ({len(content.split())} words)!")
            return {"topic": topic, "content": content}
    except Exception as e:
        print(f"[!] Groq error: {e}. Using built-in masterclass blueprint.")
        return {"topic": topic, "content": generate_fallback_script(topic)}

def generate_fallback_script(topic: str) -> str:
    paragraphs = []
    for act in range(1, 9):
        paragraphs.append(
            f"=== Act {act} ===\n"
            f"In the institutional financial markets, retail traders operate under a profound mathematical illusion. "
            f"When you place an order on your retail broker, you are not trading against another individual. "
            f"You are providing exit liquidity to algorithmic market makers operating with nanosecond fiber optics and multi-billion dollar capital reserves. "
            f"Every standard technical indicator taught in retail trading books—whether it is a support line, a resistance level, or a moving average—is an engineered liquidity pool. "
            f"The central bank algorithms and institutional dark pools are programmed to sweep these equal highs and equal lows before the genuine price expansion begins. "
            f"To achieve statistical longevity in this environment, you must stop trading chart patterns and begin tracking the mechanical footprint of institutional accumulation."
        )
    return "\n\n".join(paragraphs)

async def synthesize_audio_async(text: str, voice: str, out_path: Path):
    print(f"\n[2/5] Synthesizing Studio Neural Audio ({voice})...")
    # Clean headings
    clean_lines = [l for l in text.splitlines() if not l.startswith("===")]
    clean_text = " ".join(clean_lines)
    
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(str(out_path))
    print(f"✓ Studio audio generated: {out_path.name} ({out_path.stat().st_size / 1e6:.1f} MB)")

def download_assets(pool_dir: Path):
    print(f"\n[3/5] Pre-caching Verified Pure Financial 4K/1080p Clips...")
    pool_dir.mkdir(parents=True, exist_ok=True)
    hero_clips = []
    bridge_clips = []

    for item in TRADING_ASSET_URLS:
        dest = pool_dir / item["name"]
        if not dest.exists() or dest.stat().st_size < 100000:
            try:
                r = requests.get(item["url"], stream=True, timeout=15)
                if r.status_code == 200:
                    with open(dest, "wb") as f:
                        for chunk in r.iter_content(chunk_size=65536):
                            if chunk:
                                f.write(chunk)
                    print(f"  + Cached: {item['name']} ({dest.stat().st_size / 1e6:.1f} MB)")
            except Exception as e:
                print(f"  ! Skip: {item['name']} ({e})")
        if dest.exists() and dest.stat().st_size > 100000:
            if item["type"] == "hero":
                hero_clips.append(dest)
            else:
                bridge_clips.append(dest)

    return hero_clips, bridge_clips

def render_masterclass_video(audio_path: Path, hero_clips: list, bridge_clips: list, topic: str, out_path: Path):
    print(f"\n[4/5] Executing Waveform Retention Video Assembly (0 Charts)...")
    temp_dir = Path("temp_render")
    segs_dir = temp_dir / "segments"
    segs_dir.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Get audio duration
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)]
    res = subprocess.run(probe_cmd, capture_output=True, text=True)
    total_dur = float(json.loads(res.stdout).get("format", {}).get("duration", 600.0))
    print(f"✓ Total Duration: {total_dur:.1f}s ({total_dur/60:.1f} minutes)")

    # Build Waveform Manifest: Hero (4.5 - 6.0s), Bridge (1.6 - 2.4s)
    cuts = []
    curr_t = 0.0
    c_idx = 0
    headlines = [
        f"★ {topic.upper()} ★",
        "INSTITUTIONAL LIQUIDITY SWEEP DETECTED",
        "LEVEL 2 ORDER BOOK DEPTH & RESTING ASKS",
        "DISPLACEMENT CANDLE: +1500% VOLUME FOOTPRINT",
        "FAIR VALUE GAP (FVG): INEFFICIENCY MITIGATION",
        "LONDON & NY KILLZONES PEAK VOLUME",
        "3-STEP SNIPER EXECUTION MODEL ACTIVE",
        "ASYMMETRIC RISK MATHEMATICS: 1:3 RATIO",
        "TOP 1% INSTITUTIONAL TRADER MINDSET"
    ]

    while curr_t < total_dur - 0.5:
        is_hero = (c_idx % 3 == 0)
        dur = round(random.uniform(4.2, 5.8) if is_hero else random.uniform(1.6, 2.4), 2)
        if curr_t + dur > total_dur:
            dur = round(total_dur - curr_t, 2)
        cuts.append({
            "idx": c_idx,
            "start": curr_t,
            "end": curr_t + dur,
            "dur": dur,
            "is_hero": is_hero,
            "headline": headlines[c_idx % len(headlines)]
        })
        curr_t += dur
        c_idx += 1

    # Build Kinetic Gold ASS subtitles
    ass_path = temp_dir / "kinetic.ass"
    header = """[Script Info]
Title: Masterclass Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,42,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,3.5,2,2,40,40,85,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []
    for c in cuts:
        m1, s1 = divmod(c["start"], 60)
        h1, m1 = divmod(m1, 60)
        cs1 = int((s1 - int(s1)) * 100)
        t_start = f"{int(h1)}:{int(m1):02d}:{int(s1):02d}.{cs1:02d}"

        m2, s2 = divmod(c["end"], 60)
        h2, m2 = divmod(m2, 60)
        cs2 = int((s2 - int(s2)) * 100)
        t_end = f"{int(h2)}:{int(m2):02d}:{int(s2):02d}.{cs2:02d}"

        dialogues.append(f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{c['headline']}")
    ass_path.write_text(header + "\n".join(dialogues) + "\n", encoding="utf-8")

    # Render segments
    print(f"✓ Rendering {len(cuts)} cuts with FFmpeg...")
    concat_list = temp_dir / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f_out:
        for c in cuts:
            seg_file = segs_dir / f"seg_{c['idx']:04d}.mp4"
            pool = hero_clips if c["is_hero"] else bridge_clips
            src_clip = pool[c["idx"] % len(pool)]
            
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{(c['idx'] * 1.5) % 8.0:.2f}",
                "-i", str(src_clip),
                "-t", f"{c['dur']:.2f}",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                "-an", str(seg_file)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            safe_p = str(seg_file.resolve()).replace("\\", "/")
            f_out.write(f"file '{safe_p}'\n")

    # Lossless concat
    silent_full = temp_dir / "silent_full.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(silent_full)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Multiplex with ASS subtitles and audio
    print(f"\n[5/5] Final Multiplexing & Kinetic Subtitle Burn...")
    ass_esc = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    composite_cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_full),
        "-i", str(audio_path),
        "-vf", f"subtitles='{ass_esc}'",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]
    subprocess.run(composite_cmd, check=True)
    print(f"\n🎉 MASTERCLASS COMPLETED: {out_path} ({out_path.stat().st_size / 1e6:.1f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Distributed Cluster Node Runner")
    parser.add_argument("--job-id", type=int, default=1, help="Matrix job ID (1..20)")
    parser.add_argument("--batch-id", type=str, default="batch_001", help="Batch Identifier")
    parser.add_argument("--groq-key", type=str, default=os.getenv("GROQ_API_KEY", ""))
    args = parser.parse_args()

    topic_item = ENGLISH_TOPIC_REGISTRY[(args.job_id - 1) % len(ENGLISH_TOPIC_REGISTRY)]
    topic = topic_item["title"]
    voice = topic_item["voice"]
    channel = topic_item["channel"]

    print("=" * 70)
    print(f"🚀 DISTRIBUTED CLUSTER RUNNER | Job #{args.job_id} | Batch: {args.batch_id}")
    print(f"📺 Target Channel: {channel}")
    print(f"🎙️ Voice Profile:  {voice}")
    print(f"🎯 Master Topic:   {topic}")
    print("=" * 70)

    # 1. Script
    script_data = generate_groq_script(topic, args.groq_key)

    # 2. Audio
    audio_path = Path(f"output/audio_job_{args.job_id}.mp3")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_audio_async(script_data["content"], voice, audio_path))

    # 3. Clips
    hero_clips, bridge_clips = download_assets(Path("assets/trading_clips"))

    # 4. Final Render
    out_video = Path(f"output/masterclass_job_{args.job_id:02d}_{channel}.mp4")
    render_masterclass_video(audio_path, hero_clips, bridge_clips, topic, out_video)

    print(f"\n[✓] Job #{args.job_id} Completed Successfully!")

if __name__ == "__main__":
    main()
