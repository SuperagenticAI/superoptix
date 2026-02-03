"""Episodic memory implementation for storing experiences and episodes."""

import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .memory_backends import MemoryBackend, SQLiteBackend


@dataclass
class Episode:
    """Represents a single episode in memory."""

    id: str
    title: str
    description: str
    start_time: str
    end_time: Optional[str]
    status: str  # 'active', 'completed', 'failed'
    context: Dict[str, Any]
    events: List[Dict[str, Any]]
    outcome: Optional[Dict[str, Any]]
    tags: List[str]
    importance_score: float
    created_at: str
    updated_at: str


class EpisodicMemory:
    """Episodic memory for storing experiences, episodes, and temporal sequences."""

    def __init__(self, backend: Optional[MemoryBackend] = None):
        """
        Initialize episodic memory.

        Args:
            backend: Storage backend (defaults to SQLite)
        """
        self.backend = backend or SQLiteBackend()
        self._lock = threading.RLock()
        self._active_episodes = {}  # In-memory tracking of active episodes

    def start_episode(
        self,
        title: str,
        description: str = "",
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        importance_score: float = 1.0,
    ) -> str:
        """
        Start a new episode.

        Args:
            title: Episode title
            description: Episode description
            context: Initial context
            tags: Episode tags
            importance_score: Importance score (0.0 - 1.0)

        Returns:
            Episode ID
        """
        try:
            with self._lock:
                episode_id = str(uuid.uuid4())
                current_time = datetime.now().isoformat()

                episode = Episode(
                    id=episode_id,
                    title=title,
                    description=description,
                    start_time=current_time,
                    end_time=None,
                    status="active",
                    context=context or {},
                    events=[],
                    outcome=None,
                    tags=tags or [],
                    importance_score=importance_score,
                    created_at=current_time,
                    updated_at=current_time,
                )

                # Store episode
                key = f"episode:{episode_id}"
                success = self.backend.store(key, asdict(episode))

                if success:
                    self._active_episodes[episode_id] = episode
                    self._update_episode_index(episode_id, tags or [])

                return episode_id if success else None

        except Exception as e:
            print(f"Error starting episode: {e}")
            return None

    def add_event(
        self,
        episode_id: str,
        event_type: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Add an event to an active episode.

        Args:
            episode_id: Episode ID
            event_type: Type of event
            description: Event description
            data: Event data
            timestamp: Event timestamp (defaults to now)

        Returns:
            Success status
        """
        try:
            with self._lock:
                episode = self.get_episode(episode_id)
                if not episode or episode.status != "active":
                    return False

                event = {
                    "id": str(uuid.uuid4()),
                    "type": event_type,
                    "description": description,
                    "data": data or {},
                    "timestamp": timestamp or datetime.now().isoformat(),
                }

                episode.events.append(event)
                episode.updated_at = datetime.now().isoformat()

                # Update storage
                key = f"episode:{episode_id}"
                success = self.backend.store(key, asdict(episode))

                if success:
                    self._active_episodes[episode_id] = episode

                return success

        except Exception as e:
            print(f"Error adding event to episode: {e}")
            return False

    def end_episode(
        self,
        episode_id: str,
        outcome: Optional[Dict[str, Any]] = None,
        status: str = "completed",
    ) -> bool:
        """
        End an active episode.

        Args:
            episode_id: Episode ID
            outcome: Episode outcome
            status: Final status ('completed', 'failed', etc.)

        Returns:
            Success status
        """
        try:
            with self._lock:
                episode = self.get_episode(episode_id)
                if not episode:
                    return False

                episode.end_time = datetime.now().isoformat()
                episode.status = status
                episode.outcome = outcome
                episode.updated_at = datetime.now().isoformat()

                # Update storage
                key = f"episode:{episode_id}"
                success = self.backend.store(key, asdict(episode))

                if success:
                    # Remove from active episodes
                    self._active_episodes.pop(episode_id, None)

                return success

        except Exception as e:
            print(f"Error ending episode: {e}")
            return False

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get episode by ID."""
        try:
            with self._lock:
                # Check active episodes first
                if episode_id in self._active_episodes:
                    return self._active_episodes[episode_id]

                # Check storage
                key = f"episode:{episode_id}"
                episode_data = self.backend.retrieve(key)

                if episode_data:
                    return Episode(**episode_data)

                return None

        except Exception as e:
            print(f"Error getting episode: {e}")
            return None

    def get_active_episodes(self) -> List[Episode]:
        """Get all active episodes."""
        try:
            with self._lock:
                return list(self._active_episodes.values())
        except Exception as e:
            print(f"Error getting active episodes: {e}")
            return []

    def search_episodes(
        self,
        query: str = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> List[Episode]:
        """
        Search episodes by various criteria.

        Args:
            query: Text query for title/description
            tags: Filter by tags
            status: Filter by status
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum results

        Returns:
            List of matching episodes
        """
        try:
            with self._lock:
                all_keys = self.backend.keys("episode:*")
                results = []

                for key in all_keys:
                    episode_data = self.backend.retrieve(key)
                    if not episode_data:
                        continue

                    episode = Episode(**episode_data)

                    # Apply filters
                    if status and episode.status != status:
                        continue

                    if tags:
                        episode_tags = set(episode.tags)
                        if not episode_tags.intersection(set(tags)):
                            continue

                    if start_date:
                        if episode.start_time < start_date:
                            continue

                    if end_date:
                        if episode.end_time and episode.end_time > end_date:
                            continue

                    if query:
                        query_lower = query.lower()
                        if (
                            query_lower not in episode.title.lower()
                            and query_lower not in episode.description.lower()
                        ):
                            continue

                    results.append(episode)

                # Sort by importance and recency
                results.sort(
                    key=lambda x: (x.importance_score, x.start_time), reverse=True
                )
                return results[:limit]

        except Exception as e:
            print(f"Error searching episodes: {e}")
            return []

    def get_recent_episodes(self, days: int = 7, limit: int = 20) -> List[Episode]:
        """Get recent episodes within the specified number of days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            return self.search_episodes(start_date=cutoff_date, limit=limit)
        except Exception as e:
            print(f"Error getting recent episodes: {e}")
            return []

    def get_episodes_by_tags(self, tags: List[str], limit: int = 20) -> List[Episode]:
        """Get episodes by tags."""
        try:
            return self.search_episodes(tags=tags, limit=limit)
        except Exception as e:
            print(f"Error getting episodes by tags: {e}")
            return []

    def get_episode_timeline(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of events for an episode."""
        try:
            episode = self.get_episode(episode_id)
            if not episode:
                return []

            timeline = []

            # Add start event
            timeline.append(
                {
                    "type": "episode_start",
                    "description": f"Started episode: {episode.title}",
                    "timestamp": episode.start_time,
                    "data": {"context": episode.context},
                }
            )

            # Add all events
            timeline.extend(episode.events)

            # Add end event if episode is completed
            if episode.end_time:
                timeline.append(
                    {
                        "type": "episode_end",
                        "description": f"Ended episode with status: {episode.status}",
                        "timestamp": episode.end_time,
                        "data": {"outcome": episode.outcome},
                    }
                )

            # Sort by timestamp
            timeline.sort(key=lambda x: x["timestamp"])
            return timeline

        except Exception as e:
            print(f"Error getting episode timeline: {e}")
            return []

    def get_episode_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Analyze episodes to identify patterns."""
        try:
            with self._lock:
                all_episodes = self.search_episodes(
                    limit=1000
                )  # Get many episodes for analysis

                patterns = []

                # Pattern 1: Most common tags
                tag_counts = {}
                for episode in all_episodes:
                    for tag in episode.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

                if tag_counts:
                    common_tags = sorted(
                        tag_counts.items(), key=lambda x: x[1], reverse=True
                    )[:5]
                    patterns.append(
                        {
                            "type": "common_tags",
                            "description": "Most frequently used episode tags",
                            "data": common_tags,
                        }
                    )

                # Pattern 2: Success/failure rates
                status_counts = {}
                for episode in all_episodes:
                    if episode.status != "active":
                        status_counts[episode.status] = (
                            status_counts.get(episode.status, 0) + 1
                        )

                if status_counts:
                    patterns.append(
                        {
                            "type": "success_rates",
                            "description": "Episode completion status distribution",
                            "data": status_counts,
                        }
                    )

                # Pattern 3: Average episode duration
                durations = []
                for episode in all_episodes:
                    if episode.end_time:
                        start = datetime.fromisoformat(episode.start_time)
                        end = datetime.fromisoformat(episode.end_time)
                        duration = (end - start).total_seconds()
                        durations.append(duration)

                if durations:
                    avg_duration = sum(durations) / len(durations)
                    patterns.append(
                        {
                            "type": "average_duration",
                            "description": "Average episode duration in seconds",
                            "data": {
                                "average_seconds": avg_duration,
                                "sample_size": len(durations),
                            },
                        }
                    )

                return patterns[:limit]

        except Exception as e:
            print(f"Error getting episode patterns: {e}")
            return []

    def update_episode_context(
        self, episode_id: str, context_updates: Dict[str, Any]
    ) -> bool:
        """Update episode context."""
        try:
            with self._lock:
                episode = self.get_episode(episode_id)
                if not episode:
                    return False

                episode.context.update(context_updates)
                episode.updated_at = datetime.now().isoformat()

                # Update storage
                key = f"episode:{episode_id}"
                success = self.backend.store(key, asdict(episode))

                if success and episode_id in self._active_episodes:
                    self._active_episodes[episode_id] = episode

                return success

        except Exception as e:
            print(f"Error updating episode context: {e}")
            return False

    def delete_episode(self, episode_id: str) -> bool:
        """Delete an episode."""
        try:
            with self._lock:
                episode = self.get_episode(episode_id)
                if not episode:
                    return False

                # Remove from indices
                self._remove_from_episode_index(episode_id, episode.tags)

                # Remove from active episodes
                self._active_episodes.pop(episode_id, None)

                # Delete from storage
                key = f"episode:{episode_id}"
                return self.backend.delete(key)

        except Exception as e:
            print(f"Error deleting episode: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get episodic memory statistics."""
        try:
            with self._lock:
                all_keys = self.backend.keys("episode:*")
                total_episodes = len(all_keys)
                active_episodes = len(self._active_episodes)

                if total_episodes == 0:
                    return {
                        "total_episodes": 0,
                        "active_episodes": 0,
                        "completed_episodes": 0,
                        "avg_importance": 0,
                        "total_events": 0,
                    }

                # Collect detailed statistics
                completed_episodes = 0
                total_events = 0
                importance_scores = []
                status_counts = {}

                for key in all_keys:
                    episode_data = self.backend.retrieve(key)
                    if episode_data:
                        episode = Episode(**episode_data)
                        if episode.status != "active":
                            completed_episodes += 1

                        total_events += len(episode.events)
                        importance_scores.append(episode.importance_score)

                        status = episode.status
                        status_counts[status] = status_counts.get(status, 0) + 1

                avg_importance = (
                    sum(importance_scores) / len(importance_scores)
                    if importance_scores
                    else 0
                )

                return {
                    "total_episodes": total_episodes,
                    "active_episodes": active_episodes,
                    "completed_episodes": completed_episodes,
                    "status_distribution": status_counts,
                    "avg_importance": avg_importance,
                    "total_events": total_events,
                    "avg_events_per_episode": total_events / total_episodes
                    if total_episodes > 0
                    else 0,
                }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def _update_episode_index(self, episode_id: str, tags: List[str]):
        """Update episode index for tags."""
        try:
            for tag in tags:
                key = f"episode_tag_index:{tag}"
                current_ids = self.backend.retrieve(key) or []
                if episode_id not in current_ids:
                    current_ids.append(episode_id)
                    self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error updating episode index: {e}")

    def _remove_from_episode_index(self, episode_id: str, tags: List[str]):
        """Remove from episode index."""
        try:
            for tag in tags:
                key = f"episode_tag_index:{tag}"
                current_ids = self.backend.retrieve(key) or []
                if episode_id in current_ids:
                    current_ids.remove(episode_id)
                    self.backend.store(key, current_ids)
        except Exception as e:
            print(f"Error removing from episode index: {e}")

    def clear(self):
        """Clear all episodic memory."""
        try:
            with self._lock:
                # Clear all episodes
                episode_keys = self.backend.keys("episode:*")
                for key in episode_keys:
                    self.backend.delete(key)

                # Clear indices
                index_keys = self.backend.keys("episode_tag_index:*")
                for key in index_keys:
                    self.backend.delete(key)

                # Clear active episodes
                self._active_episodes.clear()

        except Exception as e:
            print(f"Error clearing episodic memory: {e}")
