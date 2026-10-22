import os
from pathlib import Path

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}


class AudioUtils:
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        ext = Path(filename).suffix.lower()
        return ext in ALLOWED_EXTENSIONS

    @staticmethod
    def estimate_duration_seconds(file_path: str | Path, file_size_bytes: int) -> float:
        """
        Estimates audio duration in seconds based on header or average audio bitrate (128 kbps).
        """
        path = Path(file_path)
        if not path.exists():
            return 0.0

        ext = path.suffix.lower()

        # If WAV file, read duration from standard 44-byte WAV header
        if ext == ".wav" and file_size_bytes > 44:
            try:
                with open(path, "rb") as f:
                    header = f.read(44)
                    if header[:4] == b"RIFF" and header[8:12] == b"WAVE":
                        # byte rate at offset 28 (4 bytes little-endian)
                        byte_rate = int.from_bytes(header[28:32], byteorder="little")
                        if byte_rate > 0:
                            data_size = file_size_bytes - 44
                            return round(data_size / byte_rate, 2)
            except Exception:
                pass

        # Standard estimate at ~128 kbps (16,000 bytes per second)
        avg_byte_rate = 16000
        duration = file_size_bytes / avg_byte_rate
        return round(max(5.0, duration), 2)
