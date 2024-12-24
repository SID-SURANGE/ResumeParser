# standard library imports
import os
import logging

# third party imports
from fastapi import UploadFile

# local imports
from configs.config import APP_CONFIG
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


async def save_upload_file(file: UploadFile) -> str:
    """
    Saves uploaded file to temporary directory.

    Args:
        file (UploadFile): File to be saved

    Returns:
        str: Path where file is saved

    Raises:
        IOError: If file saving fails
    """
    os.makedirs(APP_CONFIG["TEMP_DIR"], exist_ok=True)
    file_path = os.path.join(APP_CONFIG["TEMP_DIR"], file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error(f"Saving to temp directory failed with error {e}")

    return file_path
