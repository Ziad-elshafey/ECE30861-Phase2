"""Download models from HuggingFace and datasets from other sources."""
import tempfile
from typing import Optional
from huggingface_hub import snapshot_download
import logging

logger = logging.getLogger(__name__)

# Suppress verbose HuggingFace Hub logs (downloading/copying/indexing messages)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub.file_download").setLevel(logging.WARNING)


class ModelDownloader:
    """Download models from various sources."""

    @staticmethod
    def download_huggingface_model(
        model_id: str,
        cache_dir: Optional[str] = None
    ) -> str:
        """
        Download a model from HuggingFace.

        Args:
            model_id: HuggingFace model ID
                     (e.g., "google-bert/bert-base-uncased")
            cache_dir: Directory to cache the download

        Returns:
            Path to downloaded model directory
        """
        try:
            if cache_dir is None:
                cache_dir = tempfile.mkdtemp(prefix="hf_model_")

            logger.info(f"Downloading {model_id} from HuggingFace...")

            model_path = snapshot_download(
                repo_id=model_id,
                cache_dir=cache_dir,
            )

            logger.info(f"Download complete: {model_path}")
            return model_path

        except Exception as e:
            logger.error(f"Failed to download model {model_id}: {e}")
            raise
