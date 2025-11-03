"""Local filesystem storage backend for artifacts.

Handles storing, retrieving, and managing model artifacts locally.
Can be swapped out for S3/cloud storage later.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class LocalStorageBackend:
    """Local filesystem storage for artifacts."""

    def __init__(self, base_path: str = "storage/artifacts"):
        """Initialize local storage backend.

        Args:
            base_path: Base directory for storing artifacts
        """
        self.base_path = Path(base_path)
        self.models_path = self.base_path / "models"
        self.metadata_path = self.base_path / "metadata.json"

        # Create directories if they don't exist
        self.models_path.mkdir(parents=True, exist_ok=True)

        # Initialize metadata file if needed
        if not self.metadata_path.exists():
            self._save_metadata({})

    def store_artifact(
        self,
        artifact_id: str,
        artifact_path: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Store an artifact in local storage.

        Args:
            artifact_id: Unique identifier for the artifact
            artifact_path: Path to the artifact file to store
            metadata: Artifact metadata (model name, scores, etc.)

        Returns:
            Storage info with file path and metadata
        """
        try:
            source = Path(artifact_path)
            if not source.exists():
                raise FileNotFoundError(f"Artifact file not found: {artifact_path}")

            # Generate storage filename
            ext = source.suffix  # .zip, .tar.gz, etc.
            filename = f"{artifact_id}{ext}"
            destination = self.models_path / filename

            # Copy artifact to storage
            logger.info(
                f"Storing artifact {artifact_id} to {destination}"
            )
            shutil.copy2(source, destination)

            # Create storage record
            storage_info = {
                "artifact_id": artifact_id,
                "filename": filename,
                "file_path": str(destination),
                "file_size_bytes": destination.stat().st_size,
                "stored_at": datetime.utcnow().isoformat(),
                "metadata": metadata,
            }

            # Update metadata index
            self._add_to_metadata(storage_info)

            logger.info(
                f"Successfully stored artifact {artifact_id} "
                f"({storage_info['file_size_bytes']} bytes)"
            )

            return storage_info

        except Exception as e:
            logger.error(f"Error storing artifact {artifact_id}: {e}")
            raise

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact metadata.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Artifact metadata or None if not found
        """
        metadata = self._load_metadata()

        for record in metadata.get("artifacts", []):
            if record["artifact_id"] == artifact_id:
                return record

        logger.warning(f"Artifact not found: {artifact_id}")
        return None

    def list_artifacts(
        self, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """
        List all stored artifacts.

        Args:
            limit: Maximum number of artifacts to return
            offset: Offset for pagination

        Returns:
            Dictionary with artifacts list and pagination info
        """
        metadata = self._load_metadata()
        all_artifacts = metadata.get("artifacts", [])

        # Sort by stored_at descending (newest first)
        sorted_artifacts = sorted(
            all_artifacts,
            key=lambda x: x.get("stored_at", ""),
            reverse=True
        )

        # Paginate
        total = len(sorted_artifacts)
        paginated = sorted_artifacts[offset:offset + limit]

        return {
            "artifacts": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }

    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact from storage.

        Args:
            artifact_id: Artifact identifier

        Returns:
            True if deleted successfully, False if not found
        """
        try:
            artifact_info = self.get_artifact(artifact_id)
            if not artifact_info:
                return False

            # Delete file
            file_path = Path(artifact_info["file_path"])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted artifact file: {file_path}")

            # Remove from metadata
            metadata = self._load_metadata()
            metadata["artifacts"] = [
                a for a in metadata.get("artifacts", [])
                if a["artifact_id"] != artifact_id
            ]
            self._save_metadata(metadata)

            logger.info(f"Successfully deleted artifact {artifact_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting artifact {artifact_id}: {e}")
            return False

    def search_artifacts(
        self, query: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search artifacts by model name or metadata.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum results to return

        Returns:
            List of matching artifacts
        """
        metadata = self._load_metadata()
        results = []
        query_lower = query.lower()

        for artifact in metadata.get("artifacts", []):
            model_name = artifact.get("metadata", {}).get("model_name", "")
            if query_lower in model_name.lower():
                results.append(artifact)

            if len(results) >= limit:
                break

        logger.info(f"Search query '{query}' found {len(results)} artifacts")
        return results

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata index from disk."""
        try:
            if self.metadata_path.exists():
                with open(self.metadata_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")

        return {"artifacts": []}

    def _save_metadata(self, data: Dict[str, Any]) -> None:
        """Save metadata index to disk."""
        try:
            with open(self.metadata_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def _add_to_metadata(self, storage_info: Dict[str, Any]) -> None:
        """Add artifact to metadata index."""
        metadata = self._load_metadata()

        # Avoid duplicates
        metadata["artifacts"] = [
            a for a in metadata.get("artifacts", [])
            if a["artifact_id"] != storage_info["artifact_id"]
        ]

        # Add new artifact
        metadata["artifacts"].append(storage_info)

        # Keep last 100 artifacts (prevent metadata bloat)
        if len(metadata["artifacts"]) > 100:
            metadata["artifacts"] = metadata["artifacts"][-100:]

        self._save_metadata(metadata)


# Singleton instance
_storage = None


def get_storage(
    base_path: str = "storage/artifacts",
) -> LocalStorageBackend:
    """Get or create storage backend singleton."""
    global _storage
    if _storage is None:
        _storage = LocalStorageBackend(base_path)
    return _storage
