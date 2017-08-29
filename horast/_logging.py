"""Default logging mechanism for music_metadata_sync module."""

import logging
import os

logging.basicConfig(
    level=getattr(logging, os.environ.get('LOGGING_LEVEL', 'warning').upper(), logging.WARNING))
