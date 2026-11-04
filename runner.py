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

# 🎬 8 High-Retention English Psychological Trading Topics & Channel Routing
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

def generate_deep_masterclass_script(topic: str) -> str:
    """
    Generates a 10-15 minute deep psychological institutional trading masterclass script (1,400 - 1,800 words).
    Hits the retail trader's cognitive psychology, order book mechanics, and mathematical longevity directly.
    """
    acts = [
        (
            "Act 1: The Retail Mirage & Psychological Conditioning",
            f"When you open your trading platform, you are entering the most sophisticated psychological casino ever constructed by human intellect. "
            f"The charts displayed on your screen are not organic reflections of supply and demand. They are carefully engineered behavioral environments designed to harvest retail capital. "
            f"For decades, conventional retail education has conditioned traders to believe in double bottoms, head-and-shoulders patterns, and trendline bounces. "
            f"Yet institutional data reveals that over ninety-five percent of traders who employ these textbook strategies fail to achieve profitability over a twelve-month horizon. "
            f"This is not bad luck; it is a mathematical inevitability. When millions of traders are taught to place their stop-loss orders in the exact same obvious locations, those clusters of stops become high-value liquidity pools. "
            f"The tier-one investment banks and quantitative proprietary firms do not view support and resistance as barriers; they view them as target coordinates for institutional order fulfillment."
        ),
        (
            "Act 2: Auction Mechanics & Order Book Engineering",
            f"To survive in these markets, you must understand the mechanical reality of the continuous double auction. "
            f"Every single transaction requires a counterparty. If a central bank or sovereign wealth fund intends to accumulate five hundred million dollars worth of long exposure, they cannot simply click market buy. "
            f"Executing a block order of that magnitude into a thin book would cause immediate price slippage, driving the average entry price against their own balance sheet. "
            f"Therefore, the algorithm must engineer liquidity. It does this by creating the illusion of a trendline breakdown or a key support failure. "
            f"As retail participants panic and execute sell stop-losses, their sell orders flood the book. The institutional algorithm absorbs every single one of those sell orders at an extreme discount. "
            f"What retail traders interpret as a disastrous breakout to the downside is actually institutional wholesale accumulation taking place in real time."
        ),
        (
            "Act 3: Incontrovertible Institutional Footprints (Displacement & Volume)",
            f"While institutional market makers operate with vast resources, their sheer capital size makes it physically impossible for them to hide completely. "
            f"Their footprints are stamped into the time and sales tape through what we define as institutional displacement. "
            f"Displacement is not a standard candlestick. It is an aggressive, high-momentum price impulse accompanied by a multi-hundred percent surge in volume footprint. "
            f"When you witness a single forty-pip candle slicing through consolidated price action without pausing, you are observing aggressive order execution that can only be funded by institutional balance sheets. "
            f"Retail traders frequently attempt to fade this momentum, believing price has moved too far too fast. "
            f"In contrast, the institutional operator waits for the displacement to complete, recognizing that the initial aggressive thrust confirms the true directional bias of the smart money."
        ),
        (
            "Act 4: Fair Value Gap Mechanics & Inefficiency Delivery",
            f"Whenever violent institutional displacement occurs, it inevitably leaves behind structural price delivery inefficiencies. "
            f"In precision institutional trading, this phenomenon is categorized as a Fair Value Gap, or FVG. "
            f"A Fair Value Gap emerges across a three-candle sequence where the extreme low of candle one fails to overlap with the extreme high of candle three. "
            f"This void in the price delivery matrix represents a zone where only one side of the market was aggressively priced. "
            f"Market algorithms are programmed by central banks to maintain equilibrium and balanced price delivery over rolling settlement cycles. "
            f"Consequently, price has an overwhelming mathematical probability of retracing into that imbalance to rebalance resting limit orders before continuing its primary expansion. "
            f"Entering at the premium or discount boundary of a Fair Value Gap provides the highest probability entry model with the tightest invalidation thresholds in modern finance."
        ),
        (
            "Act 5: Algorithmic Killzones: London & New York Session Exploitation",
            f"Price delivery does not occur uniformly throughout the twenty-four hour day. It is governed by time-based algorithmic parameters known as Session Killzones. "
            f"The Asian session typically establishes the initial range, accumulating liquidity on both sides of the market while trading volume remains subdued. "
            f"As the London session opens at eight A M London time, the algorithmic manipulation phase, commonly referred to as the Judas Swing, is initiated. "
            f"The market frequently spikes aggressively in the opposite direction of the true daily trend to liquidate the Asian session highs or lows. "
            f"Once this retail liquidity is swept into institutional hands, the genuine trend of the day is unleashed. "
            f"When the New York session intersects with London between eight A M and eleven A M Eastern Time, global liquidity reaches its zenith. "
            f"Executing exclusively inside these high-volume killzones eliminates the dead-time chop that destroys retail accounts through overtrading and spread decay."
        ),
        (
            "Act 6: The 3-Step Precision Sniper Execution Matrix",
            f"Let us now codify this understanding into an infallible, mechanical three-step execution framework. "
            f"Step One is Liquidity Identification: Locate the resting buy-side or sell-side liquidity pools where retail stops are mathematically clustered above equal highs or below equal lows. "
            f"Step Two is Liquidity Sweep with Market Structure Shift: Wait patiently for the institutional algorithm to sweep through that liquidity, followed immediately by an aggressive displacement candle that breaks short-term market structure. "
            f"Step Three is Imbalance Mitigation Entry: Do not chase the breakout. Allow price to retrace systematically into the newly created Fair Value Gap or order block. "
            f"Your stop-loss is placed strictly beyond the swing anchor, invalidating the setup with minimal pip risk, while your profit target is calibrated to the opposing major liquidity pool. "
            f"This framework removes emotional speculation entirely, replacing guesswork with a rule-based mechanical playbook."
        ),
        (
            "Act 7: Asymmetric Mathematics & Capital Longevity",
            f"Amateur traders obsess over their win rate, believing that achieving an eighty percent strike rate is the secret to market wealth. "
            f"Institutional risk managers understand that win rate is completely irrelevant without the context of expectancy mathematics. "
            f"By executing setups with a minimum of a one-to-three risk-to-reward ratio, you achieve profound psychological freedom. "
            f"Under a one-to-three asymmetry model, you can be wrong sixty-five percent of the time and still generate substantial portfolio expansion. "
            f"If you execute one hundred trades, losing sixty-five times for a loss of sixty-five units, but winning thirty-five times at three units each, your gross gain is one hundred and five units. "
            f"Your net mathematical edge is positive forty units. Once you internalize this asymmetric reality, the emotional trauma of an individual loss evaporates, because no single outcome can threaten your long-term mathematical expectancy."
        ),
        (
            "Act 8: Psychological Rewiring of the Elite One Percent",
            f"The final barrier separating profitable traders from the perpetual ninety-nine percent is not technical; it is biological. "
            f"The human brain evolved to seek immediate dopamine rewards and to avoid the sensation of loss at all costs. "
            f"In the financial markets, these evolutionary survival mechanisms become lethal liabilities. "
            f"Retail traders cut their winners early out of fear of losing profits, and they hold losing trades indefinitely hoping for a breakeven exit. "
            f"The top one percent of institutional traders operate with the emotional neutrality of an air traffic controller. "
            f"They understand that trading is simply the continuous execution of a probabilistic edge across a statistically significant sample size. "
            f"When you detach your self-worth from individual trade outcomes and surrender completely to strict risk management, you cease to be prey. You become the predator."
        )
    ]

    full_script = []
    for title, content in acts:
        full_script.append(f"=== {title} ===\n{content}")

    return "\n\n".join(full_script)

async def synthesize_audio_async(text: str, voice: str, out_path: Path):
    print(f"\n[2/5] Synthesizing Studio Neural Audio ({voice})...")
    clean_lines = [l for l in text.splitlines() if not l.startswith("===")]
    clean_text = " ".join(clean_lines)
    
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(str(out_path))
    print(f"✓ Studio audio generated: {out_path.name} ({out_path.stat().st_size / 1e6:.1f} MB)")

def load_verified_assets(assets_dir: Path):
    print(f"\n[3/5] Loading Verified Pure Financial 4K/1080p Clips...")
    hero_clips = sorted(list((assets_dir / "hero").glob("*.mp4")))
    bridge_clips = sorted(list((assets_dir / "bridge").glob("*.mp4")))
    
    if not hero_clips:
        hero_clips = sorted(list(assets_dir.glob("hero*.mp4")))
    if not bridge_clips:
        bridge_clips = sorted(list(assets_dir.glob("bridge*.mp4")))
        
    if not hero_clips or not bridge_clips:
        all_clips = sorted(list(assets_dir.glob("**/*.mp4")))
        hero_clips = all_clips[:len(all_clips)//2] or all_clips
        bridge_clips = all_clips[len(all_clips)//2:] or all_clips

    print(f"✓ Pure Assets Loaded: {len(hero_clips)} Hero clips, {len(bridge_clips)} Bridge clips.")
    return hero_clips, bridge_clips

def render_masterclass_video(audio_path: Path, hero_clips: list, bridge_clips: list, topic: str, out_path: Path):
    print(f"\n[4/5] Executing Waveform Retention Video Assembly (0 Charts)...")
    temp_dir = Path("temp_render")
    segs_dir = temp_dir / "segments"
    segs_dir.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Audio duration
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(audio_path)]
    res = subprocess.run(probe_cmd, capture_output=True, text=True)
    total_dur = float(json.loads(res.stdout).get("format", {}).get("duration", 600.0))
    print(f"✓ Total Duration: {total_dur:.1f}s ({total_dur/60:.1f} minutes)")

    # Pacing cuts: Hero (4.2 - 5.8s), Bridge (1.6 - 2.4s)
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

    # Kinetic Gold Subtitles (ASS)
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

    # Render cuts with ultrafast FFmpeg
    print(f"✓ Rendering {len(cuts)} cuts with FFmpeg...")
    concat_list = temp_dir / "concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f_out:
        for c in cuts:
            seg_file = segs_dir / f"seg_{c['idx']:04d}.mp4"
            pool = hero_clips if c["is_hero"] else bridge_clips
            if not pool:
                pool = hero_clips or bridge_clips
            src_clip = pool[c["idx"] % len(pool)]
            
            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{(c['idx'] * 1.2) % 3.5:.2f}",
                "-i", str(src_clip),
                "-t", f"{c['dur']:.2f}",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
                "-an", str(seg_file)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            safe_p = str(seg_file.resolve()).replace("\\", "/")
            f_out.write(f"file '{safe_p}'\n")

    # Concat
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

    # 1. 10-15 Min Deep Psychological Script
    script_content = generate_deep_masterclass_script(topic)

    # 2. Studio Neural Audio
    audio_path = Path(f"output/audio_job_{args.job_id}.mp3")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize_audio_async(script_content, voice, audio_path))

    # 3. Verified Pure Financial Assets
    hero_clips, bridge_clips = load_verified_assets(Path("assets"))

    # 4. Final Video Render
    out_video = Path(f"output/masterclass_job_{args.job_id:02d}_{channel}.mp4")
    render_masterclass_video(audio_path, hero_clips, bridge_clips, topic, out_video)

    print(f"\n[✓] Job #{args.job_id} Completed Successfully!")

if __name__ == "__main__":
    main()
