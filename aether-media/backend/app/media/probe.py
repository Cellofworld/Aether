"""
Media probing utilities using FFprobe.

Provides functions to extract technical metadata from video files.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


async def probe_video_file(file_path: str) -> Dict[str, Any]:
    """
    Probe a video file using ffprobe to extract technical metadata.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        Dictionary with technical metadata
    """
    result = {
        "duration": None,
        "container": None,
        "video_codec": None,
        "audio_codec": None,
        "resolution": None,
        "width": None,
        "height": None,
        "bitrate": None,
        "framerate": None,
        "hdr": False,
        "audio_tracks": [],
        "subtitle_tracks": [],
    }
    
    try:
        # Run ffprobe command
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.warning(f"ffprobe failed for {file_path}: {stderr.decode()}")
            return result
            
        data = json.loads(stdout.decode())
        
        # Extract format info
        format_info = data.get("format", {})
        result["container"] = format_info.get("format_name", "").split(",")[0]
        result["duration"] = float(format_info.get("duration", 0)) or None
        result["bitrate"] = int(format_info.get("bit_rate", 0)) // 1000 or None
        
        # Extract stream info
        streams = data.get("streams", [])
        
        audio_tracks = []
        subtitle_tracks = []
        
        for stream in streams:
            codec_type = stream.get("codec_type")
            
            if codec_type == "video":
                result["video_codec"] = stream.get("codec_name")
                result["width"] = stream.get("width")
                result["height"] = stream.get("height")
                
                if result["width"] and result["height"]:
                    result["resolution"] = f"{result['width']}x{result['height']}"
                    
                # Framerate
                fps = stream.get("r_frame_rate", "")
                if fps and "/" in fps:
                    num, den = fps.split("/")
                    if int(den) > 0:
                        result["framerate"] = round(int(num) / int(den), 2)
                        
                # HDR detection
                color_transfer = stream.get("color_transfer", "")
                color_primaries = stream.get("color_primaries", "")
                field_order = stream.get("field_order", "")
                
                hdr_indicators = ["smpte2084", "arib-std-b67", "bt2020nc"]
                if any(ind in color_transfer.lower() for ind in hdr_indicators):
                    result["hdr"] = True
                if "bt2020" in color_primaries.lower():
                    result["hdr"] = True
                    
            elif codec_type == "audio":
                track_info = {
                    "index": stream.get("index"),
                    "codec": stream.get("codec_name"),
                    "language": stream.get("tags", {}).get("language", "und"),
                    "channels": stream.get("channels"),
                    "sample_rate": stream.get("sample_rate"),
                    "bitrate": int(stream.get("bit_rate", 0)) // 1000 if stream.get("bit_rate") else None,
                    "title": stream.get("tags", {}).get("title"),
                }
                audio_tracks.append(track_info)
                
            elif codec_type == "subtitle":
                track_info = {
                    "index": stream.get("index"),
                    "codec": stream.get("codec_name"),
                    "language": stream.get("tags", {}).get("language", "und"),
                    "title": stream.get("tags", {}).get("title"),
                    "forced": stream.get("tags", {}).get("forced", "0") == "1",
                    "default": stream.get("disposition", {}).get("default", 0) == 1,
                }
                subtitle_tracks.append(track_info)
        
        result["audio_tracks"] = audio_tracks
        result["subtitle_tracks"] = subtitle_tracks
        
        # Set primary audio codec
        if audio_tracks:
            result["audio_codec"] = audio_tracks[0].get("codec")
            
    except FileNotFoundError:
        logger.error(f"ffprobe not found. Please install ffmpeg.")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ffprobe output for {file_path}: {e}")
    except Exception as e:
        logger.exception(f"Error probing file {file_path}: {e}")
    
    return result


def get_container_from_extension(filepath: str) -> str:
    """
    Get container format from file extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Container format name
    """
    ext_map = {
        ".mkv": "matroska",
        ".mp4": "mp4",
        ".avi": "avi",
        ".mov": "mov",
        ".webm": "webm",
        ".m4v": "mp4",
        ".wmv": "wmv",
        ".flv": "flv",
    }
    
    ext = Path(filepath).suffix.lower()
    return ext_map.get(ext, ext.lstrip("."))


async def get_media_duration(file_path: str) -> Optional[float]:
    """
    Get duration of a media file.
    
    Args:
        file_path: Path to the media file
        
    Returns:
        Duration in seconds or None
    """
    result = await probe_video_file(file_path)
    return result.get("duration")


async def check_file_exists_and_readable(file_path: str) -> bool:
    """
    Check if a file exists and is readable.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file exists and is readable
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        if not path.is_file():
            return False
        # Try to read first few bytes
        with open(path, 'rb') as f:
            f.read(1024)
        return True
    except (OSError, IOError):
        return False
