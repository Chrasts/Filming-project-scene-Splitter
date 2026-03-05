from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# 1) INPUT: cleaned xlsx
BASE_DIR = Path(__file__).resolve().parent
IN_XLSX = str(REPO_ROOT / "data" / "scenosled_input.xlsx")

# 2) OUTPUT: directory for per-character files
OUT_DIR = str(REPO_ROOT / "output" / "characters")

# 3) Expected column names
SCENE_COL = "cislo_obrazu"
DATE_COL = "den"
CHARS_COL = "postavy"
COST_COL = "kostymy"
PLACE_COL = "misto"
PLOT_COL = "dej"

# 4) Regex helpers:
#    - DAY_RE extracts shooting day number from text like "DEN 3" / "DAY 3"
#    - SCENE_RE extracts scene number + optional letter suffix from e.g. "12A"
DAY_RE = re.compile(r"\b(?:DEN|DAY)\s*(\d+)\b", re.IGNORECASE)
SCENE_RE = re.compile(r"^\s*(\d+)\s*([A-Za-z]?)")


# 5) Normalize cells 
def norm(x) -> str:
    return re.sub(
        r"\s+",
        " ",
        ("" if x is None else str(x)).replace("\n", " ").replace("\r", " "),
    ).strip()


# 6) Parse day number from DATE_COL, use a large fallback so unknown days sort last
def parse_day_num(text: str) -> int:
    m = DAY_RE.search(norm(text))
    return int(m.group(1)) if m else 10**9


# 7) Convert day number into a clean label used in outputs
def day_to_label(text: str) -> str:
    n = parse_day_num(text)
    return f"DAY {n}" if n != 10**9 else ""


# 8) Build a stable sort key for scene ordering
def parse_scene_key(scene: str) -> tuple[int, str]:
    m = SCENE_RE.match(norm(scene))
    return (int(m.group(1)), (m.group(2) or "").upper()) if m else (10**9, "")


# 9) Make a safe filename for Windows/macOS/Linux
def safe_filename(name: str, max_len: int = 120) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "_", norm(name))
    return (name or "UNKNOWN")[:max_len]


# 10) Split character list from one cell into unique names
def split_characters(cell: str) -> list[str]:
    parts = [norm(p) for p in norm(cell).split(",")]
    parts = [p for p in parts if p]

    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        k = p.lower()
        if k not in seen:
            out.append(p)
            seen.add(k)
    return out


# 11) Main pipeline: load -> normalize -> parse days/scenes -> split chars -> export per character
def build_character_breakdowns(in_xlsx: str, out_dir: str) -> None:

    # 11.1) Read xlsx as strings, replace NaNs and normalize all cells
    df = pd.read_excel(in_xlsx, dtype=str).fillna("")
    for c in df.columns:
        df[c] = df[c].map(norm)

    # 11.2) Validate required columns exist
    required = [SCENE_COL, DATE_COL, CHARS_COL, COST_COL, PLACE_COL, PLOT_COL]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Found: {list(df.columns)}")

    # 11.3) Add helper columns for sorting and membership tests
    df["__day_num"] = df[DATE_COL].map(parse_day_num)
    df["den"] = df[DATE_COL]
    df["__scene_key"] = df[SCENE_COL].map(parse_scene_key)
    df["__chars"] = df[CHARS_COL].map(split_characters)

    # 11.4) Build unique character list
    uniq: dict[str, str] = {}
    for lst in df["__chars"]:
        for nm in lst:
            uniq.setdefault(nm.lower(), nm)

    # 11.5) Ensure output directory exists
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 11.6) For each character filter rows -> sort -> select columns -> write xlsx
    for ch in uniq.values():
        key = ch.lower()

        # Keep rows where this character is present in the parsed list
        sub = df[
            df["__chars"].map(lambda lst, k=key: k in (x.lower() for x in lst))
        ].copy()
        if sub.empty:
            continue

        # Sort by shooting day then scene key
        sub = sub.sort_values(["__day_num", "__scene_key"], kind="stable")

        # Keep only the columns intended for costume breakdown usage
        sub = sub[["den", SCENE_COL, COST_COL, PLACE_COL, PLOT_COL]]

        # Export one xlsx per character
        sub.to_excel(out_path / f"{safe_filename(ch)}.xlsx", index=False)



def main() -> None:
    build_character_breakdowns(IN_XLSX, OUT_DIR)


if __name__ == "__main__":

    main()
