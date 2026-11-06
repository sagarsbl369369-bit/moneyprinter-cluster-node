import json
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = PROJECT_ROOT / "cluster" / "usa_viral_100_catalog.json"

def get_viral_catalog() -> List[Dict[str, Any]]:
    if CATALOG_PATH.exists():
        try:
            return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

# High-converting American SEO Title Templates for Rumble Algorithm
TITLE_TEMPLATES = [
    "[COURT CAM] Sovereign Citizen Tells Judge 'I Do Not Recognize Your Law' — INSTANT REGRET",
    "Cop Realizes Entitled Driver Is Actually A Federal Prosecutor (RAW BODYCAM)",
    "Judge GIVES UP After Defendant Tries To Fire 5th Lawyer In 10 Minutes",
    "Senator RED-FACED As Witness DROPS Bombshell Evidence In Heated Hearing",
    "Contempt Of Court: Defendant Gets 30 Days Immediately After Disrespecting Bench",
    "Field Sobriety Test Gone Completely Wrong: Suspect Tries Gymnastics (BODYCAM)",
    "Small Claims Chaos: Landlord Brings Shocking Secret Audio Recording To Court",
    "Bailiff Forced To Restrain Defendant After Shocking Contempt Outburst",
    "Whistleblower STUNS Congressional Hearing With Unsealed Internal Memos",
    "Sovereign Citizen Refuses To Step Out Of Vehicle — Window Broken (RAW)",
    "Watch What Happens When Criminal Thinks He Can Outsmart Veteran Detective",
    "Zoom Court Disasters: Defendant Shows Up To Hearing While Driving Suspended",
    "Judge Delivers Epic 10-Minute Lecture To Repeat Offender Before Sentencing",
    "Traffic Court Smackdown: Driver Argues With Speed Radar Video And Loses",
    "State Trooper Intercepts High-Speed Contraband Run On Interstate (K9 Alert)"
]

def get_viral_topic_for_job(job_id: int) -> Dict[str, Any]:
    catalog = get_viral_catalog()
    if not catalog:
        ch = {"id": 101, "name": "TheSovereignGavel", "title": "The Sovereign Gavel", "category": "Courtroom"}
    else:
        ch = catalog[(job_id - 1) % len(catalog)]

    title_idx = (job_id - 1) % len(TITLE_TEMPLATES)
    title = TITLE_TEMPLATES[title_idx]

    # Maximize Rumble Mid-Roll Ad Placements with 5 Structured Breaks
    desc = f"""🔥 VIRAL CASE EPISODE #{job_id}: {title}
Presented exclusively by {ch['title']}. Raw, unfiltered public record proceedings and frontline encounters.

💬 COMMUNITY DISCUSSION QUESTION:
Did the judge/officer handle this situation appropriately, or did they cross the line? Share your legal opinion in the comments below!

🔔 Follow {ch['title']} for daily unfiltered public records, court cams, and bodycam releases.

⏱️ OFFICIAL CHAPTERS & EPISODE TIMESTAMPS:
00:00 - Introduction & Formal Docket Call
03:30 - Initial Resistance & High-Tension Confrontation
07:45 - Key Evidence & Cross-Examination Breakdown
12:15 - Escalation & Contempt Warning
16:50 - Decisive Climax & Bailiff / Law Enforcement Action
21:30 - Final Ruling, Sentence & Legal Analysis

⚖️ LEGAL DISCLAIMER & PUBLIC RECORD NOTICE:
This video presents unedited judicial public records, government committee broadcasts, and official FOIA law enforcement releases for educational, journalistic, and archival transparency under the First Amendment and applicable US Public Records laws.

#CourtCam #SovereignCitizen #PoliceBodycam #InstantRegret #SenateHearing #TrueCrime #LawAndOrder"""

    tags = ", ".join(ch.get("tags", ["court cam", "sovereign citizen", "bodycam", "instant regret", "public records"]))

    return {
        "job_id": job_id,
        "channel_id": str(ch["id"]),
        "channel_name": ch["name"],
        "channel_title": ch["title"],
        "category": ch.get("category", "Courtroom & Public Records"),
        "title": title,
        "description": desc,
        "tags": tags,
        "ad_density_mode": "MAX_MIDROLL_EXCLUSIVE",
        "target_duration": ch.get("target_duration", "15-25 min")
    }

if __name__ == "__main__":
    t = get_viral_topic_for_job(1)
    print("Sample Viral Topic Metadata:")
    print("Title:", t["title"])
    print("Channel:", t["channel_title"])
    print("Ad Mode:", t["ad_density_mode"])
    print("Duration Target:", t["target_duration"])
