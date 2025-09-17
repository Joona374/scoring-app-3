# leijonat_slots_scraper.py
from __future__ import annotations

import os

env = os.environ.get("ENV", "development")  # default to development
if env != "LOCAL":
    # Force Playwright to use the slug-bundled browsers, not the default cache
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/render/project/src/.playwright")
    # Make absolutely sure it doesn't try headless_shell
    os.environ["PLAYWRIGHT_CHROMIUM_USE_HEADLESS_SHELL"] = "0"
    # (Optional) Quiet host checks on slim containers
    # os.environ.setdefault("PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS", "1")

import asyncio
import re
from typing import Dict, Literal, Optional, Tuple
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
import glob


# --- Public config ---
Side = Literal["home", "away"]

# Site's position codes inside element ids like: {side}-roster-p-<line>-<code>
POSCODE_TO_SLOT: Dict[int, str] = {12: "LW", 3: "C", 13: "RW", 2: "LD", 11: "RD"}
DEFAULT_LINES = [1, 2, 3, 4, 5]  # line 5 often hosts extras (13th F / 7th D)

# Breakpoint-specific containers (only one is visible at a time)
ROSTER_ROOTS = ["#xl-game-rosters", "#lg-game-rosters", "#md-game-rosters", "#sm-game-rosters"]

# Suffix tags in text: (AM)=starting goalie, (H)=extra forward, (P)=extra defense
TAG_RX = re.compile(r"\((AM|H|P)\)\s*$", re.IGNORECASE)


# -----------------------
# Name parsing / formatting
# -----------------------
def _split_lines(raw: str) -> list[str]:
    raw = raw.replace("\r", "")
    parts = [p.strip() for p in raw.split("\n")]
    return [p for p in parts if p]

def _title_keep_accents(s: str) -> str:
    # Title-case but keep ÅÄÖ etc. Python's .title() preserves accents fine.
    return s.title()

def _format_first_last(parts: list[str]) -> str:
    """
    Convert ["SURNAME","Firstname", "Middle"] → "Firstname Middle Surname"
    If first token is ALL CAPS, treat it as surname; otherwise just join as-is.
    """
    if not parts:
        return ""
    first = parts[0]
    others = parts[1:]
    if first.isupper():  # Surname in caps (common here)
        surname = _title_keep_accents(first)
        given = " ".join(_title_keep_accents(p) for p in others).strip()
        if given:
            return f"{given} {surname}".strip()
        return surname
    # Fallback: title-case everything in order
    return " ".join(_title_keep_accents(p) for p in parts).strip()

def _parse_cell(raw: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (name, tag). Tag in {'AM','H','P',None}.
    - Drop leading jersey numbers (often duplicated).
    - Build name from remaining non-number lines.
    - Peel trailing (AM|H|P).
    - Format as 'Firstname Lastname'.
    """
    parts = _split_lines(raw)

    # Drop up to two leading jersey numbers (e.g., "25", "25 25")
    for _ in range(2):
        if parts and re.fullmatch(r"\d{1,2}", parts[0]):
            parts.pop(0)

    if not parts:
        return None, None

    # Non-number tokens usually: [SURNAME, Given(, More...)]
    non_num = [p for p in parts if not re.fullmatch(r"\d{1,2}", p)]
    if not non_num:
        return None, None

    text = " ".join(non_num).strip()

    # Extract and strip trailing (AM|H|P)
    tag = None
    m = TAG_RX.search(text)
    if m:
        tag = m.group(1).upper()
        text = TAG_RX.sub("", text).strip()

    # Rebuild from original line tokens for better spacing (SURNAME on its own line)
    if len(non_num) >= 2:
        # Preserve line grouping when possible: ["SURNAME","Firstname"...]
        first_two_like_lines = [non_num[0]] + non_num[1:]
        name = _format_first_last(first_two_like_lines)
    else:
        name = _format_first_last(non_num)

    # Final cleanup: remove any lingering leading number, collapse spaces
    name = re.sub(r"^\d{1,2}\s+", "", name or "").strip()
    name = re.sub(r"\s+", " ", name)
    return (name if name else None), tag


# -----------------------
# Page helpers
# -----------------------
async def _accept_cookies(page) -> None:
    # Static wait so Cookiebot can render
    await page.wait_for_timeout(2000)
    try:
        btn = page.locator("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        if await btn.count() > 0:
            await btn.click()
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
            except PWTimeout:
                pass
    except Exception:
        pass

async def _ensure_kokoonpanot(page) -> None:
    try:
        link = page.get_by_role("link", name="Kokoonpanot", exact=False)
        if await link.count() > 0:
            await link.first.click()
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except PWTimeout:
                pass
        else:
            node = page.locator("text=Kokoonpanot")
            if await node.count() > 0:
                await node.first.click()
    except Exception:
        pass

async def _find_roster_frame(page, side: Side):
    """Find the frame (or main doc) that contains #{side}-roster-p-* nodes."""
    sel = f'[id^="{side}-roster-p-"]'
    if await page.locator(sel).count() > 0:
        return page.main_frame
    for fr in page.frames:
        try:
            if await fr.locator(sel).count() > 0:
                return fr
        except Exception:
            continue
    return None

async def _find_visible_roster_root(frame):
    """Pick the roster container for the active breakpoint."""
    root_locator = frame.locator(", ".join(ROSTER_ROOTS))
    count = await root_locator.count()
    for i in range(count):
        c = root_locator.nth(i)
        try:
            if await c.is_visible():
                return c
        except Exception:
            continue
    return root_locator.first  # fallback

async def _visible_player_text(root, elem_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Read a player cell from the visible roster root, handling duplicate IDs across breakpoints.
    Returns (name, tag).
    """
    loc = root.locator(f"#{elem_id}")
    n = await loc.count()
    if n == 0:
        return None, None

    # Prefer visible node if duplicates exist
    for i in range(n):
        el = loc.nth(i)
        try:
            if await el.is_visible():
                raw = await el.inner_text()
                return _parse_cell(raw)
        except Exception:
            continue

    # Fallback: first
    try:
        raw = await loc.first.inner_text()
        return _parse_cell(raw)
    except Exception:
        return None, None


# -----------------------
# Scrape workflow
# -----------------------
async def scrape_team_slots(url: str, side: Side) -> Dict[str, str]:
    """
    Returns a dict like:
      {
        "LW1": "Firstname Lastname",
        "C1":  "...",
        "RW1": "...",
        "LD1": "...",
        "RD1": "...",
        ...,
        "G1":  "...",    # starter
        "G2":  "..."     # backup
        "LW5": "...",    # 13th forward, if present (from p-4-2 with (H))
        "LD5": "..."     # 7th defense, if present (from p-4-2 with (P))
      }
    """
    results: Dict[str, str] = {}

    try:
        if env == "LOCAL":
            chrome_path = None  # use default
        else:
        # Find the exact chrome binary we baked into the slug during BUILD
            base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/render/project/src/.playwright")
            candidates = glob.glob(os.path.join(base, "chromium-*", "chrome-linux", "chrome"))
            if not candidates:
                raise RuntimeError(
                    f"No Chromium found under {base}. Did your BUILD step run "
                    f"`python -m playwright install chromium` with PLAYWRIGHT_BROWSERS_PATH set?"
                )
            chrome_path = candidates[0]

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                executable_path=chrome_path,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            ctx = await browser.new_context()
            page = await ctx.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await _accept_cookies(page)
            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except PWTimeout:
                pass

            await _ensure_kokoonpanot(page)

            roster_frame = await _find_roster_frame(page, side)
            if roster_frame is None:
                # One retry after a short delay
                await page.wait_for_timeout(1200)
                roster_frame = await _find_roster_frame(page, side)

            if roster_frame is None:
                await ctx.close(); await browser.close()
                return results  # empty

            visible_root = await _find_visible_roster_root(roster_frame)

            # --- Skaters ---
            for line in DEFAULT_LINES:
                for code, slot in POSCODE_TO_SLOT.items():
                    elem_id = f"{side}-roster-p-{line}-{code}"
                    name, tag = await _visible_player_text(visible_root, elem_id)
                    name = clean_suffixes_from_name(name)

                    # Special extra slot always rendered at p-4-2:
                    #   (H) => 13th forward  -> map to LW5
                    #   (P) => 7th defense   -> map to LD5
                    if line == 4 and code == 2 and name:
                        if tag == "H":
                            results["5-LW"] = name
                            continue
                        elif tag == "P":
                            results["4-LD"] = name
                            continue

                    if name:
                        results[f"{line}-{slot}"] = name

            # --- Goalies (deterministic ids) ---
            # starter: line 1, pos 1 -> G1
            # backup : line 2, pos 1 -> G2
            for (line, label) in ((1, "1-G"), (2, "2-G")):
                g_id = f"{side}-roster-p-{line}-1"
                name, _ = await _visible_player_text(visible_root, g_id)
                if name:
                    clean_name = clean_suffixes_from_name(name)
                    results[label] = clean_name

            await ctx.close()
            await browser.close()

        return results
    except Exception as e:
        print(f"Error scraping roster {e}")
        return {}

def clean_suffixes_from_name(name: str):
    if not name:
        return name
    
    position_indicators = [" (H) ", " (Am) ", " (P) "]
    for pos in position_indicators:
        if pos in name:
            name = name.replace(pos, " ")
    return name
        

def scrape_slots(url: str, user_is_home: bool) -> Dict[str, str]:
    side: Side = "home" if user_is_home else "away"
    return asyncio.run(scrape_team_slots(url, side))


# -----------------------
# CLI
# -----------------------
if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 3:
        print("Usage: python leijonat_slots_scraper.py <game_url> <home|away>")
        raise SystemExit(1)
    url = sys.argv[1]
    side_arg = sys.argv[2].strip().lower()
    if side_arg not in {"home", "away"}:
        print("Second arg must be 'home' or 'away'")
        raise SystemExit(1)

    data = asyncio.run(scrape_team_slots(url, side_arg))  # type: ignore
    print(json.dumps(data, ensure_ascii=False, indent=2))
