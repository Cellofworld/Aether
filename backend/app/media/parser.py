import re
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

# Regex patterns for media detection
PATTERNS = {
    "movie": [
        # Movie.Name.2024.1080p.mkv
        r"^(?P<title>.+?)[\s._-]+(?P<year>\d{4})[\s._-]+(?P<resolution>\d{3,4}p)?",
        # Movie Name (2024).mkv
        r"^(?P<title>.+?)\s*\((?P<year>\d{4})\)",
    ],
    "series": [
        # Show.Name.S01E01.mkv
        r"(?P<title>.+?)[\s._-]*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})",
        # Show.Name.1x01.mkv
        r"(?P<title>.+?)[\s._-]*(?P<season>\d{1,2})x(?P<episode>\d{1,2})",
        # Show.Name.E01.mkv (Anime style often)
        r"(?P<title>.+?)[\s._-]*E(?P<episode>\d{1,2})",
        # [Group] Anime - 01 [1080p].mkv
        r"\[(?P<group>.+?)\]\s*(?P<title>.+?)[\s._-]+(?P<episode>\d{2,3})",
    ],
    "resolution": [
        r"(2160|4K)[\s._-]?(HDR|DV|DOVI)?",
        r"(1080|720|480)[\s._-]?p",
    ],
    "codec": [
        r"(HEVC|H\.?265|X265)",
        r"(AVC|H\.?264|X264)",
        r"(VP9|AV1)",
    ],
    "audio": [
        r"(AAC|AC3|EAC3|DTS|TrueHD|FLAC)[\s._-]?(\d\.?\d)?",
    ]
}

def parse_filename(filename: str, path: str = "") -> Dict[str, Any]:
    """
    Parses a filename to extract metadata like title, year, season, episode.
    Returns a dictionary with extracted data.
    """
    file_path = Path(path) if path else Path(filename)
    name = file_path.stem
    extension = file_path.suffix.lower()
    
    result = {
        "original_name": name,
        "type": "unknown", # movie, series, episode
        "title": "",
        "year": None,
        "season": None,
        "episode": None,
        "resolution": None,
        "codec": None,
        "is_anime": False,
        "group": None,
        "confidence": 0.0
    }

    # Check extension validity roughly
    valid_exts = ['.mkv', '.mp4', '.avi', '.mov', '.webm', '.m4v']
    if extension not in valid_exts:
        return result

    # Try Series patterns first (more specific)
    for pattern in PATTERNS["series"]:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            groups = match.groupdict()
            result["type"] = "series"
            result["title"] = groups.get("title", "").replace(".", " ").strip()
            
            if "season" in groups and groups["season"]:
                result["season"] = int(groups["season"])
            if "episode" in groups and groups["episode"]:
                result["episode"] = int(groups["episode"])
            
            if "group" in groups and groups["group"]:
                result["is_anime"] = True
                result["group"] = groups["group"]
            
            result["confidence"] = 0.9
            break

    # If not series, try Movie patterns
    if result["type"] == "unknown":
        for pattern in PATTERNS["movie"]:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                result["type"] = "movie"
                result["title"] = groups.get("title", "").replace(".", " ").strip()
                if "year" in groups and groups["year"]:
                    result["year"] = int(groups["year"])
                result["confidence"] = 0.8
                break
    
    # Fallback: If still unknown, assume movie with filename as title
    if result["type"] == "unknown":
        result["type"] = "movie"
        result["title"] = name.replace(".", " ").strip()
        result["confidence"] = 0.3

    # Extract technical details from full path/name
    full_string = f"{name} {path}"
    
    for res_pattern in PATTERNS["resolution"]:
        if re.search(res_pattern, full_string, re.IGNORECASE):
            m = re.search(res_pattern, full_string, re.IGNORECASE)
            if m:
                val = m.group(0).upper()
                if "4K" in val or "2160" in val:
                    result["resolution"] = "4K"
                elif "1080" in val:
                    result["resolution"] = "1080p"
                elif "720" in val:
                    result["resolution"] = "720p"
                else:
                    result["resolution"] = val
                break

    for codec_pattern in PATTERNS["codec"]:
        if re.search(codec_pattern, full_string, re.IGNORECASE):
            m = re.search(codec_pattern, full_string, re.IGNORECASE)
            if m:
                val = m.group(0).upper()
                if "HEVC" in val or "H.265" in val or "X265" in val:
                    result["codec"] = "HEVC"
                elif "AVC" in val or "H.264" in val:
                    result["codec"] = "H.264"
                else:
                    result["codec"] = val
                break

    return result

def find_subtitle_files(video_path: Path) -> Dict[str, Path]:
    """
    Finds subtitle files next to the video file.
    Returns dict: { language_code: path }
    """
    subtitles = {}
    parent = video_path.parent
    stem = video_path.stem
    
    # Common subtitle extensions
    sub_exts = ['.srt', '.vtt', '.ass', '.ssa']
    
    # Patterns to look for: Movie.en.srt, Movie.ru.srt, Movie.srt
    for f in parent.iterdir():
        if f.suffix.lower() in sub_exts and f.is_file():
            fname = f.stem
            lang = "unk"
            
            # Check if filename starts with video stem
            if fname.startswith(stem):
                remainder = fname[len(stem):]
                # Extract language code (e.g., .en, .ru)
                lang_match = re.search(r'[._-]([a-z]{2,3})', remainder, re.IGNORECASE)
                if lang_match:
                    lang = lang_match.group(1).lower()
                elif remainder:
                    lang = remainder.strip("._-").lower()
                else:
                    lang = "xx" # Default/Unknown
                
                subtitles[lang] = f.resolve()
            elif fname == stem:
                subtitles["xx"] = f.resolve()
                
    return subtitles
