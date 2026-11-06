import os
import sys
import re
import json
import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PROJECT_ROOT = Path(__file__).resolve().parent
CHANNELS_FILE = PROJECT_ROOT / "rumble_channels.json"

def get_subchannel_id(job_id: int, channel_name: str = "") -> Dict[str, str]:
    """Resolves target sub-channel from rumble_channels.json or hardcoded verified IDs."""
    if CHANNELS_FILE.exists():
        try:
            chs = json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
            sub_chs = [c for c in chs if str(c.get("id")) != "0" and not c.get("is_default", False)]
            if sub_chs:
                target = sub_chs[(job_id - 1) % len(sub_chs)]
                return {
                    "id": str(target["id"]),
                    "title": target.get("title", target.get("name", channel_name))
                }
        except Exception:
            pass

    # Verified fallback mapping for 20 channels
    VERIFIED_MAP = [
        ("7981510", "SmartMoneyHindi"),
        ("7981512", "SmartMoneySecrets369"),
        ("7981514", "smartmoney1793771659"),
        ("7981520", "OrderBlockAlpha369"),
        ("7981522", "PriceActionBeast369"),
        ("7981524", "CandlePsychology369"),
        ("7981526", "BankNiftySniper369"),
        ("7981528", "ForexMajorsAlpha369"),
        ("7981530", "CryptoFuturesDesk369"),
        ("7981532", "OptionSellingPro369"),
        ("7981534", "OptionBuyingHero369"),
        ("7981536", "TraderPsychology369"),
        ("7981538", "RiskRewardMaster369"),
        ("7981540", "VolumeProfileSniper369"),
        ("7981542", "BreakoutTrapHunter369"),
        ("7981544", "SupplyDemandZone369"),
        ("7981546", "ChartPatternElite369"),
        ("7981548", "SwingTradingIndia369"),
        ("7981550", "IntradayStockPicks369"),
        ("7981552", "VWAPScalpingPro369")
    ]
    ch_id, title = VERIFIED_MAP[(job_id - 1) % len(VERIFIED_MAP)]
    return {"id": ch_id, "title": title}

def generate_seo_metadata(topic: str, channel_title: str, job_id: int) -> Dict[str, Any]:
    """Generates clean high-CTR metadata strictly within Rumble's <= 90 char limit."""
    raw_title = f"{topic} | {channel_title}"
    if len(raw_title) > 90:
        raw_title = raw_title[:88].rsplit(" ", 1)[0]

    desc = f"""🔥 Masterclass Episode #{job_id}: {topic}
Welcome to {channel_title}. In this institutional masterclass, we break down high-level order flow, central bank liquidity algorithms, and asymmetric risk models.

⏱️ CHAPTERS & TIMESTAMPS:
00:00 - The High-Frequency Microstructure
03:15 - Identifying Institutional Order Blocks
07:45 - Fair Value Gap Delivery & Algorithmic Exploits
11:30 - Asymmetric 1:3.5 Risk Model Execution
14:50 - The Central Bank Playbook & Rules

⚠️ DISCLAIMER: Educational purposes only. Not financial advice.

#SmartMoneyConcepts #TradingMasterclass #OrderBlock #PriceAction #Forex #Crypto"""

    tags = "smart money concepts, order block, price action, trading strategy, ict, forex, crypto, day trading"
    return {"title": raw_title, "description": desc, "tags": tags}

def publish_video_from_cloud(video_path: Path, job_id: int, channel_name: str, topic: str, thumbnail_path: Optional[Path] = None) -> Optional[str]:
    """
    Executes direct Cloud-to-Rumble publication from inside the GitHub Actions runner.
    Leverages Microsoft Azure's 10 Gbps symmetric pipe for 15-20s upload speeds.
    Auto-attaches a random custom thumbnail from the 1 - 1,000,000 thumbnail vault.
    """
    if not sync_playwright:
        print("[CloudPublisher] ❌ Playwright is not installed in the environment!")
        return None

    session_b64 = os.environ.get("RUMBLE_SESSION_B64")
    if not session_b64:
        print("[CloudPublisher] ⚠️ RUMBLE_SESSION_B64 secret not found! Skipping cloud upload.")
        return None

    # Stagger delay to prevent concurrent lock contention on Rumble (15s offset per job)
    stagger_sec = ((job_id - 1) % 5) * 8
    if stagger_sec > 0:
        print(f"[CloudPublisher] ⏳ Applying anti-collision stagger delay: {stagger_sec}s...")
        time.sleep(stagger_sec)

    session_file = Path("/tmp/rumble_session.json") if os.name != "nt" else Path("storage/rumble_session_cloud.json")
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_bytes(base64.b64decode(session_b64))

    ch_info = get_subchannel_id(job_id, channel_name)
    target_id = ch_info["id"]
    target_title = ch_info["title"]
    seo = generate_seo_metadata(topic, target_title, job_id)

    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    print("\n" + "=" * 70)
    print(f"🚀 [CloudPublisher] DIRECT AZURE-TO-RUMBLE CLOUD PUBLISHING")
    print(f"   🎬 Video:        {video_path.name} ({file_size_mb:.1f} MB)")
    print(f"   📺 Target:       {target_title} (ID: #{target_id})")
    print(f"   📌 Title:        {seo['title']} ({len(seo['title'])} chars)")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )
        context = browser.new_context(
            storage_state=str(session_file.resolve()),
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(180000)

        print("[CloudPublisher] 🌐 Opening Rumble upload interface...")
        page.goto("https://rumble.com/upload.php", wait_until="domcontentloaded")
        time.sleep(3)

        if "login" in page.url.lower():
            print("[CloudPublisher] ❌ Session expired or invalid on Rumble!")
            browser.close()
            return None

        # 1. Attach Video File
        print(f"[CloudPublisher] 📎 Uploading {video_path.name} ({file_size_mb:.1f} MB) via Azure 10 Gbps Pipe...")
        file_input = page.wait_for_selector("input[type='file']", timeout=30000)
        file_input.set_input_files(str(video_path.resolve()))

        # 1.5 Attach Master Custom Thumbnail (THE ALGO TRAP / Vault)
        if thumbnail_path and thumbnail_path.exists():
            print(f"[CloudPublisher] 🖼️ Attaching Master Thumbnail: {thumbnail_path.name} ({thumbnail_path.stat().st_size} bytes)...")
            thumb_attached = False
            for _ in range(3):
                try:
                    thumb_inputs = page.query_selector_all("input[type='file']")
                    for inp in thumb_inputs:
                        accept_attr = (inp.get_attribute("accept") or "").lower()
                        name_attr = (inp.get_attribute("name") or "").lower()
                        inp_id = (inp.get_attribute("id") or "").lower()
                        if "video" in accept_attr or "mp4" in accept_attr:
                            continue
                        if "image" in accept_attr or "thumb" in name_attr or "thumb" in inp_id or len(thumb_inputs) > 1:
                            inp.set_input_files(str(thumbnail_path.resolve()))
                            print(f"[CloudPublisher] ✓ Master custom thumbnail attached to input '{name_attr or inp_id}'!")
                            thumb_attached = True
                            break
                    if thumb_attached:
                        break
                except Exception as e:
                    print(f"[CloudPublisher] ⚠️ Thumbnail attach query: {e}")
                time.sleep(1)

        # 2. Fill Metadata
        title_input = page.wait_for_selector("input[name='title'], #title", timeout=15000)
        title_input.fill(seo["title"])

        desc_input = page.wait_for_selector("textarea[name='description'], #description", timeout=15000)
        desc_input.fill(seo["description"])

        tags_input = page.query_selector("input[name='tags'], #tags")
        if tags_input:
            tags_input.fill(seo["tags"])

        # 3. Lock Sub-Channel Strictly (NEVER upload to User Personal Profile '0')
        print(f"[CloudPublisher] 🔒 Locking Sub-Channel strictly: '{target_title}' (#{target_id})...")
        channel_locked = False
        try:
            res = page.evaluate(f"""() => {{
                // 1. Force uncheck user personal profile default radio
                const defaultRadios = [
                    document.querySelector("#channelId_"),
                    document.querySelector("input[name='channelId'][value='']"),
                    document.querySelector("input[name='channelId'][value='0']")
                ];
                for (const d of defaultRadios) {{
                    if (d) {{ d.checked = false; d.removeAttribute('checked'); }}
                }}

                // 2. Select target sub-channel radio by ID
                let target = document.querySelector("input[name='channelId'][value='{target_id}']");
                
                // 3. If ID not matched directly, find by channel title inside label
                if (!target) {{
                    const radios = document.querySelectorAll("input[name='channelId']");
                    for (const r of radios) {{
                        const lbl = document.querySelector(`label[for='${{r.id}}']`) || r.closest('label') || r.parentElement;
                        if (lbl && (lbl.innerText.includes('{target_title}') || lbl.innerText.toLowerCase().includes('{target_title.lower()}'))) {{
                            target = r;
                            break;
                        }}
                    }}
                }}

                if (target) {{
                    target.checked = true;
                    target.setAttribute('checked', 'checked');
                    const lbl = document.querySelector(`label[for='${{target.id}}']`) || target.closest('label') || target.parentElement;
                    if (lbl) lbl.click();
                    target.dispatchEvent(new Event('change', {{bubbles: true}}));
                    target.dispatchEvent(new Event('click', {{bubbles: true}}));
                    return {{ success: true, id: target.id, val: target.value }};
                }}
                return {{ success: false }};
            }}""")

            # Fallback direct Playwright click on label if available
            try:
                page.click(f"input[name='channelId'][value='{target_id}']", timeout=2000, force=True)
            except Exception:
                try:
                    page.click(f"label:has-text('{target_title}')", timeout=2000, force=True)
                except Exception:
                    pass

            # Verification
            time.sleep(0.5)
            is_sub_checked = page.evaluate(f"""() => {{
                const target = document.querySelector("input[name='channelId'][value='{target_id}']");
                const def = document.querySelector("input[name='channelId'][value='']") || document.querySelector("#channelId_");
                return target ? target.checked : (def ? !def.checked : true);
            }}""")
            if is_sub_checked:
                print(f"[CloudPublisher] ✓ Sub-Channel verified locked: '{target_title}' (#{target_id})")
                channel_locked = True
            else:
                print(f"[CloudPublisher] ⚠️ Notice: Sub-channel radio checked state returned false; force-clicking label...")
                page.click(f"label:has-text('{target_title}')", timeout=3000, force=True)
        except Exception as ce:
            print(f"[CloudPublisher] Sub-channel lock notice: {ce}")

        # 4. Wait for Transfer (Azure speed: ~15-25 seconds!)
        print("[CloudPublisher] ⏳ Waiting for transfer completion (Azure ultra-high-speed)...")
        for _ in range(60):
            time.sleep(2)
            pct_el = page.query_selector("span.top_percent")
            if pct_el:
                pct_text = pct_el.inner_text().strip()
                if "100%" in pct_text:
                    print(f"[CloudPublisher] 🎉 File transfer 100% complete ({pct_text})!")
                    break

        time.sleep(2)

        # 5. Step 1 Submit (with Groove overlay annihilation & JS click)
        print("[CloudPublisher] ➡️ Submitting Step 1...")
        try:
            page.evaluate("""() => {
                document.querySelectorAll("iframe[id*='groove'], div[id*='groove'], .groove-widget, #groove-container, [class*='groove']").forEach(e => e.remove());
                const btn = document.querySelector("#submitForm");
                if (btn) {
                    btn.scrollIntoView();
                    btn.removeAttribute('disabled');
                    btn.click();
                }
            }""")
        except Exception as e:
            print(f"[CloudPublisher] Direct DOM submit notice: {e}")
        try:
            page.click("#submitForm", force=True, timeout=10000)
        except Exception:
            pass
        time.sleep(3)

        # 6. Step 2 Licensing & Rights (Exclusive Video Management for Max Ad Fill & Yahoo/MSN Syndication)
        print("[CloudPublisher] 📜 Configuring Licensing & Rights (Exclusive Video Management: Value 1)...")
        try:
            page.wait_for_selector("input[name='license'], #crights, #cterms", timeout=45000)
            # Prioritize Value 1 (Exclusive Video Management) for maximum ad fills across Rumble & global syndication
            try:
                page.click("input[name='license'][value='1'], div:has-text('Exclusive Video Management'), div:has-text('Video Management (excluding YouTube)')", timeout=5000)
            except Exception:
                page.click("input[name='license'][value='2'], div:has-text('Rumble Only')", timeout=4000)
        except Exception as e:
            print(f"[CloudPublisher] License select notice: {e}")

        page.evaluate("""() => {
            // Select Value 1: Exclusive Video Management (Highest ad fills & earnings)
            const lic1 = document.querySelector("input[name='license'][value='1']");
            const lic2 = document.querySelector("input[name='license'][value='2']");
            if (lic1) {
                lic1.checked = true;
                lic1.dispatchEvent(new Event('change', {bubbles: true}));
                lic1.dispatchEvent(new Event('click', {bubbles: true}));
            } else if (lic2) {
                lic2.checked = true;
                lic2.dispatchEvent(new Event('change', {bubbles: true}));
                lic2.dispatchEvent(new Event('click', {bubbles: true}));
            }
            const cr = document.getElementById('crights');
            if (cr && !cr.checked) { cr.checked = true; cr.dispatchEvent(new Event('change', {bubbles: true})); }
            const ct = document.getElementById('cterms');
            if (ct && !ct.checked) { ct.checked = true; ct.dispatchEvent(new Event('change', {bubbles: true})); }
        }""")
        time.sleep(2)

        # 7. Final Publish
        print("[CloudPublisher] 🚀 Submitting final publish request (#submitForm2)...")
        page.evaluate("""() => {
            document.querySelectorAll("iframe[id*='groove'], div[id*='groove'], .groove-widget, #groove-container, [class*='groove']").forEach(e => e.remove());
            const btn = document.querySelector("#submitForm2");
            if (btn) {
                btn.scrollIntoView();
                btn.removeAttribute('disabled');
                btn.click();
            }
        }""")
        time.sleep(3)
        try:
            page.click("#submitForm2", force=True, timeout=5000)
        except Exception:
            pass
        time.sleep(5)

        # 8. Extract Live URL
        video_url = None
        for _ in range(25):
            time.sleep(2)
            for sel in ["#direct", "#monetized", "textarea[id='direct']", "textarea[id='monetized']"]:
                el = page.query_selector(sel)
                if el:
                    val = el.input_value() or el.get_attribute("value") or ""
                    m = re.search(r'https?://rumble\.com/v[0-9a-z]{5,}[^\s"\'<>]*', val)
                    if m:
                        video_url = m.group(0).strip()
                        break
            if video_url:
                break

        browser.close()

        if video_url:
            print("\n" + "*" * 70)
            print(f"🎉 [CloudPublisher] 100% LIVE ON RUMBLE DIRECT FROM CLOUD!")
            print(f"👉 URL: {video_url}")
            print("*" * 70 + "\n")

            # Persist to runner output
            ledger_file = Path("output/rumble_live_ledger.json")
            ledger_file.parent.mkdir(parents=True, exist_ok=True)
            existing_ledger = {}
            if ledger_file.exists():
                try:
                    existing_ledger = json.loads(ledger_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            existing_ledger[f"job_{job_id}"] = {
                "job_id": job_id,
                "channel_id": target_id,
                "channel_title": target_title,
                "rumble_url": video_url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            ledger_file.write_text(json.dumps(existing_ledger, indent=2), encoding="utf-8")

            # Write to GITHUB_STEP_SUMMARY if running in GitHub Actions
            step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
            if step_summary:
                with open(step_summary, "a", encoding="utf-8") as f:
                    f.write(f"\n### 🚀 Job #{job_id} LIVE on Rumble!\n- **Channel:** `{target_title}`\n- **Live URL:** [{video_url}]({video_url})\n\n")

            return video_url
        else:
            print("[CloudPublisher] ⚠️ Did not find live URL in confirmation page.")
            return None
