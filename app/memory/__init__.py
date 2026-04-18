"""
Memory Module
Runtime Architecture v2 - Memory abstraction layers

Exports:
- types: Memory type definitions
- working_memory: Redis hot working memory
- episodic_memory: Event/history memory
- semantic_memory: Vector/semantic retrieval (SingleStore adapter)
- checkpoints: Postgres checkpoint persistence
- cortex: Briefing/cross-thread summaries
- compaction: Context budget and compaction service
"""
from app.memory.types import (
    MemoryType,
    MemoryStatus,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    CortexMemory,
    CheckpointMemory,
    # Cortex types
    CortexCategory,
    TypedMemory,
    CompactionSummary,
)

from app.memory.working_memory import (
    WorkingMemoryStore,
    get_working_memory,
    REDIS_AVAILABLE as WORKING_REDIS_AVAILABLE,
)

from app.memory.episodic_memory import (
    EpisodicMemoryStore,
    get_episodic_memory,
)

from app.memory.semantic_memory import (
    SemanticMemoryStore,
    get_semantic_memory,
)

from app.memory.checkpoints import (
    CheckpointStore,
    get_checkpoint_store,
)

from app.memory.cortex import (
    CortexStore,
    get_cortex_store,
)

from app.memory.compaction import (
    CompactionService,
    get_compaction_service,
    CONTEXT_BUDGETS,
    COMPACTION_THRESHOLD_RATIO,
    CHECKPOINT_INTERVAL,
)

__all__ = [
    # Types
    "MemoryType",
    "MemoryStatus", 
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "CortexMemory",
    "CheckpointMemory",
    # Cortex types
    "CortexCategory",
    "TypedMemory",
    "CompactionSummary",
    # Working Memory
    "WorkingMemoryStore",
    "get_working_memory",
    "WORKING_REDIS_AVAILABLE",
    # Episodic Memory
    "EpisodicMemoryStore",
    "get_episodic_memory",
    # Semantic Memory
    "SemanticMemoryStore",
    "get_semantic_memory",
    # Checkpoints
    "CheckpointStore",
    "get_checkpoint_store",
    # Cortex
    "CortexStore",
    "get_cortex_store",
    # Compaction
    "CompactionService",
    "get_compaction_service",
    "CONTEXT_BUDGETS",
    "COMPACTION_THRESHOLD_RATIO",
    "CHECKPOINT_INTERVAL",
]
