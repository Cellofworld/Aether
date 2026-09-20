"""Streaming service for video files."""
import os
import logging
from pathlib import Path
from typing import Optional, AsyncGenerator
from fastapi import Request, Response, HTTPException

logger = logging.getLogger(__name__)


class StreamService:
    """Service for handling video streaming."""
    
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    async def stream_file(
        self, 
        request: Request, 
        file_path: Path
    ) -> Response:
        """
        Stream a file with support for HTTP Range requests.
        This enables seeking and efficient streaming.
        """
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_size = file_path.stat().st_size
        
        # Get range header
        range_header = request.headers.get("range")
        
        if range_header:
            return await self._stream_range(request, file_path, file_size)
        else:
            return await self._stream_full(file_path, file_size)
    
    async def _stream_range(
        self,
        request: Request,
        file_path: Path,
        file_size: int
    ) -> Response:
        """Handle ranged requests for seeking support."""
        range_header = request.headers.get("range")
        
        # Parse range header (e.g., "bytes=0-1048575")
        try:
            range_str = range_header.replace("bytes=", "")
            start_str, end_str = range_str.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            
            # Validate range
            start = max(0, min(start, file_size - 1))
            end = max(start, min(end, file_size - 1))
            
        except (ValueError, IndexError):
            # Invalid range, return full file
            return await self._stream_full(file_path, file_size)
        
        # Calculate content length
        content_length = end - start + 1
        
        # Create response with appropriate headers
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": self._get_content_type(file_path),
        }
        
        return Response(
            status_code=206,  # Partial Content
            content=self._file_generator(file_path, start, end),
            headers=headers
        )
    
    async def _stream_full(
        self,
        file_path: Path,
        file_size: int
    ) -> Response:
        """Stream entire file."""
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": self._get_content_type(file_path),
        }
        
        return Response(
            status_code=200,
            content=self._file_generator(file_path, 0, file_size - 1),
            headers=headers
        )
    
    def _file_generator(
        self,
        file_path: Path,
        start: int,
        end: int
    ) -> bytes:
        """Generator to read file in chunks."""
        try:
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = end - start + 1
                
                while remaining > 0:
                    chunk_size = min(self.CHUNK_SIZE, remaining)
                    chunk = f.read(chunk_size)
                    
                    if not chunk:
                        break
                    
                    yield chunk
                    remaining -= len(chunk)
                    
        except Exception as e:
            logger.error(f"Error streaming file {file_path}: {e}")
            raise
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get MIME type based on file extension."""
        mime_types = {
            ".mp4": "video/mp4",
            ".mkv": "video/x-matroska",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".m4v": "video/x-m4v",
        }
        
        ext = file_path.suffix.lower()
        return mime_types.get(ext, "application/octet-stream")
    
    async def generate_hls_playlist(
        self,
        video_file: any,
        request: Request
    ) -> Optional[str]:
        """
        Generate HLS master playlist.
        Returns m3u8 content or None if transcoding is not available.
        """
        # Check if transcoding is enabled
        from app.core.config import settings
        
        if not settings.TRANSCODING_ENABLED:
            return None
        
        # For now, return a simple playlist pointing to direct stream
        # In production, this would trigger FFmpeg transcoding
        base_url = str(request.base_url).rstrip("/")
        media_id = video_file.media_id
        
        playlist = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=8000000,RESOLUTION=1920x1080
{base_url}/api/playback/stream/{media_id}
"""
        
        return playlist
