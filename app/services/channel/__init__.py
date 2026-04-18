"""
Channel Service
Phase 0 - Channel, branch, worker, and cortex management

This service provides:
- Channel lifecycle management
- Branch forking and merging
- Worker execution context
- Cortex context summaries

Status: IMPLEMENTED (internal + runtime APIs)
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ChannelService:
    """
    Channel management service.
    
    Manages communication channels (web, slack, discord, etc.)
    """
    
    def __init__(self):
        self._channels: Dict[str, Dict[str, Any]] = {}
    
    def create_channel(
        self,
        name: str,
        channel_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new channel."""
        import uuid
        channel_id = f"channel-{uuid.uuid4().hex[:12]}"
        
        channel = {
            "id": channel_id,
            "name": name,
            "type": channel_type,
            "config": config or {},
            "enabled": True,
            "created_at": datetime.utcnow(),
        }
        
        self._channels[channel_id] = channel
        logger.info(f"Created channel: {channel_id}")
        return channel
    
    def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel by ID."""
        return self._channels.get(channel_id)
    
    def list_channels(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List all channels."""
        channels = list(self._channels.values())
        if enabled_only:
            channels = [c for c in channels if c.get("enabled", True)]
        return channels
    
    def update_channel(self, channel_id: str, updates: Dict[str, Any]) -> bool:
        """Update channel."""
        if channel_id not in self._channels:
            return False
        self._channels[channel_id].update(updates)
        return True


class BranchService:
    """
    Branch management service.
    
    Manages conversation branches and forking.
    """
    
    def __init__(self):
        self._branches: Dict[str, Dict[str, Any]] = {}
    
    def create_branch(
        self,
        thread_id: str,
        channel_id: str,
        parent_branch_id: Optional[str] = None,
        branch_type: str = "main",
    ) -> Dict[str, Any]:
        """Create a new branch."""
        import uuid
        branch_id = f"branch-{uuid.uuid4().hex[:12]}"
        
        branch = {
            "id": branch_id,
            "thread_id": thread_id,
            "channel_id": channel_id,
            "parent_branch_id": parent_branch_id,
            "branch_type": branch_type,
            "status": "active",
            "metadata": {},
            "created_at": datetime.utcnow(),
        }
        
        self._branches[branch_id] = branch
        logger.info(f"Created branch: {branch_id} for thread: {thread_id}")
        return branch
    
    def get_branch(self, branch_id: str) -> Optional[Dict[str, Any]]:
        """Get branch by ID."""
        return self._branches.get(branch_id)
    
    def list_branches(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List branches for a thread."""
        branches = list(self._branches.values())
        if thread_id:
            branches = [b for b in branches if b["thread_id"] == thread_id]
        return branches
    
    def merge_branch(self, branch_id: str) -> bool:
        """Mark branch as merged."""
        if branch_id not in self._branches:
            return False
        self._branches[branch_id]["status"] = "merged"
        self._branches[branch_id]["merged_at"] = datetime.utcnow()
        return True
    
    def close_branch(self, branch_id: str) -> bool:
        """Close a branch."""
        if branch_id not in self._branches:
            return False
        self._branches[branch_id]["status"] = "closed"
        return True


class WorkerService:
    """
    Worker execution context service.
    
    Manages worker threads for execution.
    """
    
    def __init__(self):
        self._workers: Dict[str, Dict[str, Any]] = {}
    
    def create_worker(
        self,
        branch_id: str,
        worker_type: str = "execution",
        runtime_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new worker."""
        import uuid
        worker_id = f"worker-{uuid.uuid4().hex[:12]}"
        
        worker = {
            "id": worker_id,
            "branch_id": branch_id,
            "worker_type": worker_type,
            "runtime_id": runtime_id,
            "state": {},
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        
        self._workers[worker_id] = worker
        logger.info(f"Created worker: {worker_id}")
        return worker
    
    def get_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get worker by ID."""
        return self._workers.get(worker_id)
    
    def update_worker_state(self, worker_id: str, state: Dict[str, Any]) -> bool:
        """Update worker state."""
        if worker_id not in self._workers:
            return False
        self._workers[worker_id]["state"].update(state)
        return True
    
    def start_worker(self, worker_id: str) -> bool:
        """Mark worker as started."""
        if worker_id not in self._workers:
            return False
        self._workers[worker_id]["status"] = "running"
        self._workers[worker_id]["started_at"] = datetime.utcnow()
        return True
    
    def complete_worker(
        self,
        worker_id: str,
        final_state: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Mark worker as completed."""
        if worker_id not in self._workers:
            return False
        self._workers[worker_id]["status"] = "completed"
        self._workers[worker_id]["completed_at"] = datetime.utcnow()
        if final_state:
            self._workers[worker_id]["state"].update(final_state)
        return True
    
    def fail_worker(self, worker_id: str, error: str) -> bool:
        """Mark worker as failed."""
        if worker_id not in self._workers:
            return False
        self._workers[worker_id]["status"] = "failed"
        self._workers[worker_id]["error"] = error
        self._workers[worker_id]["completed_at"] = datetime.utcnow()
        return True


class CortexService:
    """
    Cortex context service.
    
    Manages context compaction and summaries.
    """
    
    def __init__(self):
        self._summaries: Dict[str, Dict[str, Any]] = {}
    
    def create_summary(
        self,
        thread_id: str,
        tenant_id: str,
        running_summary: str,
        open_loops: List[str],
        tokens_before: int,
        tokens_after: int,
        step: int,
    ) -> Dict[str, Any]:
        """Create a compaction summary."""
        import uuid
        summary_id = f"summary-{uuid.uuid4().hex[:12]}"
        
        summary = {
            "id": summary_id,
            "thread_id": thread_id,
            "tenant_id": tenant_id,
            "running_summary": running_summary,
            "open_loops": open_loops,
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": tokens_before - tokens_after,
            "step": step,
            "created_at": datetime.utcnow(),
        }
        
        self._summaries[summary_id] = summary
        return summary
    
    def get_summary(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get summary by ID."""
        return self._summaries.get(summary_id)
    
    def get_latest_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get latest summary for a thread."""
        thread_summaries = [
            s for s in self._summaries.values() if s["thread_id"] == thread_id
        ]
        if not thread_summaries:
            return None
        return max(thread_summaries, key=lambda s: s["created_at"])
    
    def list_summaries(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List summaries."""
        summaries = list(self._summaries.values())
        if thread_id:
            summaries = [s for s in summaries if s["thread_id"] == thread_id]
        return sorted(summaries, key=lambda s: s["created_at"], reverse=True)


# Global instances
_channel_service: Optional[ChannelService] = None
_branch_service: Optional[BranchService] = None
_worker_service: Optional[WorkerService] = None
_cortex_service: Optional[CortexService] = None


def get_channel_service() -> ChannelService:
    """Get global channel service."""
    global _channel_service
    if _channel_service is None:
        _channel_service = ChannelService()
    return _channel_service


def get_branch_service() -> BranchService:
    """Get global branch service."""
    global _branch_service
    if _branch_service is None:
        _branch_service = BranchService()
    return _branch_service


def get_worker_service() -> WorkerService:
    """Get global worker service."""
    global _worker_service
    if _worker_service is None:
        _worker_service = WorkerService()
    return _worker_service


def get_cortex_service() -> CortexService:
    """Get global cortex service."""
    global _cortex_service
    if _cortex_service is None:
        _cortex_service = CortexService()
    return _cortex_service


__all__ = [
    "ChannelService",
    "BranchService",
    "WorkerService",
    "CortexService",
    "get_channel_service",
    "get_branch_service",
    "get_worker_service",
    "get_cortex_service",
]