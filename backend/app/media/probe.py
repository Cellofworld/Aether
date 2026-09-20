"""Video file probing using ffprobe."""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

async def probe_video_file(file_path: str) -> Dict[str, Any]:
    """
    Probe a video file using ffprobe to get technical details.
    
    Returns dict with:
    - duration
    - width, height
    - codec
    - bitrate
    - framerate
    - audio_streams
    - subtitle_streams
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.warning(f"ffprobe failed for {file_path}: {stderr.decode()}")
            return {}
        
        data = json.loads(stdout.decode())
        
        # Extract format info
        format_info = data.get("format", {})
        duration = float(format_info.get("duration", 0))
        bitrate = int(format_info.get("bit_rate", 0))
        
        # Extract stream info
        video_stream = None
        audio_streams = []
        subtitle_streams = []
        
        for stream in data.get("streams", []):
            codec_type = stream.get("codec_type")
            
            if codec_type == "video" and video_stream is None:
                video_stream = stream
            elif codec_type == "audio":
                audio_streams.append({
                    "index": stream.get("index", 0),
                    "codec": stream.get("codec_name", ""),
                    "language": _get_language(stream),
                    "channels": stream.get("channels", 0),
                    "bitrate": int(stream.get("bit_rate", 0)),
                    "title": stream.get("tags", {}).get("title", "")
                })
            elif codec_type == "subtitle":
                subtitle_streams.append({
                    "index": stream.get("index", 0),
                    "codec": stream.get("codec_name", ""),
                    "language": _get_language(stream),
                    "is_forced": stream.get("disposition", {}).get("forced", 0) == 1
                })
        
        result = {
            "duration": duration,
            "bitrate": bitrate,
            "audio_streams": audio_streams,
            "subtitle_streams": subtitle_streams
        }
        
        # Add video-specific info
        if video_stream:
            result.update({
                "width": video_stream.get("width", 0),
                "height": video_stream.get("height", 0),
                "codec": video_stream.get("codec_name", ""),
                "framerate": _parse_framerate(video_stream.get("r_frame_rate", "0/1")),
                "has_hdr": _detect_hdr(video_stream)
            })
        
        return result
        
    except FileNotFoundError:
        logger.error("ffprobe not found. Please install ffmpeg.")
        return {}
    except Exception as e:
        logger.error(f"Error probing {file_path}: {e}", exc_info=True)
        return {}


def _get_language(stream: Dict) -> str:
    """Extract language code from stream tags."""
    tags = stream.get("tags", {})
    return tags.get("language", "unk")


def _parse_framerate(rate_str: str) -> float:
    """Parse framerate string like '24000/1001' to float."""
    if not rate_str or "/" not in rate_str:
        return 0.0
    
    try:
        num, den = map(int, rate_str.split("/"))
        if den == 0:
            return 0.0
        return round(num / den, 3)
    except (ValueError, ZeroDivisionError):
        return 0.0


def _detect_hdr(stream: Dict) -> bool:
    """Detect if video has HDR metadata."""
    # Check for transfer characteristics indicating HDR
    color_transfer = stream.get("color_transfer", "")
    color_primaries = stream.get("color_primaries", "")
    
    hdr_indicators = [
        "smpte2084",  # PQ (HDR10, Dolby Vision)
        "arib-std-b67",  # HLG
        "bt2020"  # Often associated with HDR
    ]
    
    return any(ind in color_transfer.lower() or ind in color_primaries.lower() 
               for ind in hdr_indicators)


async def get_thumbnail(file_path: str, timestamp: float = 5.0) -> Optional[bytes]:
    """
    Generate a thumbnail from a video file at given timestamp.
    Returns JPEG bytes or None on failure.
    """
    cmd = [
        "ffmpeg",
        "-ss", str(timestamp),
        "-i", file_path,
        "-vframes", "1",
        "-vf", "scale=320:-1",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-"
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        stdout, _ = await process.communicate()
        
        if process.returncode == 0 and stdout:
            return stdout
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")
        return None
