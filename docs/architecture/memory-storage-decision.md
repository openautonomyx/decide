# Memory & Storage Decision Matrix

This document recommends the storage layer architecture for each memory/state category in Runtime Architecture v2. It is additive and does not replace the existing transactional/control-plane model.

---

## 1. Purpose

The purpose of this decision matrix is to:

1. **Separate concerns** - Working memory, episodic memory, semantic memory, operational memory, and audit have different access patterns, lifetimes, and durability requirements
2. **Enable scaling** - Different storage backends optimize for different workload characteristics
3. **Preserve control-plane truth** - The transactional DB remains the authoritative source for workflow state
4. **Support Retrieval-Augmented Generation** - Hybrid vector + keyword retrieval for knowledge grounding
5. **Enable LangGraph orchestration** - Working memory and checkpoint storage must support rapid state mutation

---

## 2. What Remains Unchanged

The following remain in the existing transactional Postgres database:

| Entity | Table | Why |
|--------|-------|-----|
| Employee | employee | HR truth, RBAC |
| Agent | agent | Governance truth |
| Product/Project/Group | collaboration_* | Business model |
| Task/Milestone/Reminder | workflow_* | Operational truth |
| ExecutionRequest | execution_request | Control plane |
| ApprovalRequest | approval_request | Audit trail |
| DecisionRecord | decision_record | Policy outcomes |
| OverrideRecord | override_record | Override audit |
| ResponsibilityAssignment | responsibility_assignment | Delegation audit |
| UsageRecord | usage_record | Billing truth |
| TenantPolicy | tenant_policy | Policy truth |

**No control-plane entities move to Redis or vector stores.**

---

## 3. Storage Options Considered

### Redis

| Aspect | Assessment |
|--------|-----------|
| **Strengths** | Sub-millisecond latency, native pub/sub, sorted sets, streams, TTL support, hash maps |
| **Weaknesses** | Persistence is secondary (RDB/AOF), limited query capability, memory-bound |
| **Best for** | Hot cache, session state, rate limiting, simple pub/sub |
| **Vector** | Yes (Redis VSS), but secondary to main purpose |
| **Cost** | Memory-bound, scales vertically |

### SingleStore (formerly MemSQL)

| Aspect | Assessment |
|--------|-----------|
| **Strengths** | HTAP (hybrid transactional/analytical), vector search built-in, MySQL wire protocol, auto-scaling |
| **Weaknesses** | Managed-only (no self-hosted), less flexibility than pure vector DBs |
| **Best for** | Primary vector store + hybrid retrieval |
| **Vector** | Yes, native vector type |
| **Cost** | Managed, scales horizontally |

### SurrealDB

| Aspect | Assessment |
|--------|-----------|
| **Strengths** | Graph-native, embedded or standalone, flexible schema, real-time |
| **Weaknesses** | Smaller ecosystem, less mature for production AI workloads |
| **Best for** | Memory-graph experimentation only |
| **Vector** | Native, but limited ecosystem |
| **Cost** | Can be self-hosted or managed |

### Postgres (Existing)

| Aspect | Assessment |
|--------|-----------|
| **Strengths** | Already deployed, ACID compliant, rich query, mature, FK relationships |
| **Weaknesses** | No native vector, pgvector is extension |
| **Best for** | All control-plane truth, audit, workflow state |
| **Vector** | Requires pgvector extension |
| **Cost** | Already in use |

### What We Don't Consider Yet

| Option | Why Excluded |
|--------|------------|
| **Kafka** | Not required for Phase 1; sync request flow is sufficient |
| **Airflow** | Not required for Phase 1; LangGraph handles orchestration |
| **Camunda** | Not required; existing workflow model is sufficient |

---

## 4. Recommendation Summary

| Layer | Primary Storage | Notes |
|-------|--------------|-------|
| **Working memory** | Redis | Hot, mutable, TTL-based session state |
| **Episodic memory** | Postgres + Redis | Events logged to Postgres, hot cache in Redis |
| **Semantic memory** | SingleStore | Primary vector + hybrid retrieval |
| **Operational memory** | Postgres | Authoritative, ACID truth |
| **Cortex memory** | Redis + Postgres | Checkpoints to Postgres, briefs cached in Redis |
| **Vector retrieval** | SingleStore | Primary vector store |
| **Checkpoints** | Postgres | Persistence, durability |
| **Audit/history** | Postgres | Authoritative trace |

---

## 5. Decision Matrix by Memory/State Category

### 5.1 Working Memory

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Redis |
| **Schema** | Hash maps per thread_id, JSON for complex state |
| **TTL** | Session timeout (30 min default) |
| **Durability** | Not required; rebuildable from Postgres checkpoints |
| **Example keys** | `working:{thread_id}`, `context:{session_id}` |
| **Why** | Sub-millisecond access, native hash/map support |

### 5.2 Episodic Memory

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Postgres (authoritative) + Redis (hot cache) |
| **Schema** | Event log table in Postgres; Redis LRU cache |
| **TTL** | Postgres: indefinitely; Redis: 24 hours |
| **Durability** | Postgres is authoritative |
| **Example events** | tool_call, agent_turn, decision, user_input |
| **Why** | Audit requirements + fast replay |

### 5.3 Semantic Memory

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | SingleStore (primary vector) + Postgres (metadata) |
| **Schema** | SingleStore table with vector column; Postgres for entity FK |
| **TTL** | No TTL; managed deletion |
| **Durability** | SingleStore persistence |
| **Example** | user_preferences, org_facts, reusable_snippets |
| **Why** | Hybrid search (keyword + vector) |

### 5.4 Operational Memory

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Postgres only |
| **Schema** | Existing tables unchanged |
| **TTL** | No TTL; explicit operations |
| **Durability** | Required ACID |
| **Examples** | task, milestone, reminder, escalation, approval_request |
| **Why** | Control-plane truth; FK relationships required |

### 5.5 Cortex Memory

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Redis (hot briefs) + Postgres (checkpoints) |
| **Schema** | Redis: JSON briefs per thread; Postgres: checkpoint tables |
| **TTL** | Redis: 7 days; Postgres: 30 days default |
| **Durability** | Postgres for recovery |
| **Example** | briefing, thread_summary, pending_actions |
| **Why** | Fast access for current briefs; durable for recovery |

### 5.6 Vector Retrieval Layer

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | SingleStore (primary) |
| **Schema** | Vector table with HNSW index |
| **TTL** | No TTL; explicit deletion |
| **Durability** | SingleStore persistence |
| **Example** | knowledge_base, document_summaries, project_docs |
| **Why** | Native hybrid search, scales horizontally |

### 5.7 Compaction Checkpoints

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Postgres (durable) + Redis (hot cache) |
| **Schema** | New cortex_memory table; Redis LRU |
| **TTL** | Postgres: configurable; Redis: session |
| **Durability** | Postgres is primary |
| **Example** | thread_checkpoint, branch_checkpoint |
| **Why** | Long-running recovery requires durability |

### 5.8 Audit/History Layer

| Requirement | Recommendation |
|-------------|--------------|
| **Storage** | Postgres only |
| **Schema** | Existing tables unchanged |
| **TTL** | Retention policy (typically 7 years) |
| **Durability** | Required for compliance |
| **Example** | approval_request, execution_history |
| **Why** | Authoritative trace for compliance |

---

## 6. Recommended Default Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   LangGraph  │    │   Runtime  │    │    API      │  │
│  │  Orchestrator│    │   Adapters │    │   Layer     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                          │                              │
│          ┌───────────────┼───────────────┐               │
│          ▼               ▼               ▼               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │   Redis     │ │ SingleStore │ │  Postgres  │ │
│  │ (Hot)      │ │ (Vector)   │ │(Operational)│ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
│       │              │               │               │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  │
│  │Working │  │Semantic │  │Control  │  │
│  │Memory  │  │Memory   │  │Plane   │  │
│  │Cache  │  │(vector) │  │Truth   │  │
│  └───────┘  └─────────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1 (Implementation)

| Component | Implementation |
|-----------|--------------|
| Working memory | Redis with session TTL |
| Episodic cache | Redis LRU cache over Postgres |
| Semantic vector | SingleStore with HNSW |
| Operational | Postgres (existing) |
| Checkpoints | Postgres new table |
| Audit | Postgres (existing) |

### Phase 2 (Future)

| Component | Implementation | Trigger |
|-----------|--------------|---------|
| Cortex briefs | Redis + Postgres | Need for briefing synthesis |
| Graph memory | SurrealDB | Memory-graph experimentation justified |
| Event bus | Kafka | Async scale-out required |

---

## 7. Why Redis Should Be Primary Vector Memory

### No, Redis Should NOT Be Primary

**Reasons against Redis as primary vector store:**

1. **Memory-bound** - All vectors in RAM; cost scales with vector count
2. **Secondary purpose** - Primary is caching, session state
3. **Persistence is afterthought** - RDB/AOF lag
4. **Ecosystem** - Fewer ML/AI integrations than specialized stores
5. **SingleStore already selected** - Unifies vector + operational

### But Redis IS Right For

- **Working memory** - Hot, mutable, TTL-based
- **Session cache** - Fast access to recent state
- **Rate limiting** - Native sorted set support
- **Pub/sub** - Simple event distribution
- **Hot checkpoints** - Fast recovery within session

### Redis Configuration

```python
# Working memory in Redis
redis_client.hset(
    f"working:{thread_id}",
    mapping={
        "current_node": "execute",
        "execution_state": json.dumps(state),
        "tool_outputs": json.dumps(tool_results)
    }
)
redis_client.expire(f"working:{thread_id}", 1800)  # 30 min TTL
```

---

## 8. Why SingleStore Should Be Default Vector Store

### Yes, SingleStore Should Be Primary

**Reasons for SingleStore:**

1. **HTAP** - Hybrid transactional/analytical in one system
2. **Native vector** - Vector type with HNSW index
3. **MySQL protocol** - Standard drivers
4. **Scales horizontally** - Auto-scaling cluster
5. **No FK compromise** - Can join with metadata tables
6. **Already in ecosystem** - Existing managed service

### SingleStore Schema Example

```sql
-- Semantic memory table
CREATE TABLE semantic_memory (
    memory_id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    memory_type VARCHAR(20) NOT NULL,  -- preference, fact, snippet
    
    -- Content
    content_text TEXT NOT NULL,
    content_embedding VECTOR(1536),
    
    -- Metadata
    source_type VARCHAR(20),
    source_id VARCHAR(36),
    expires_at DATETIME,
    
    -- Audit
    created_at DATETIME DEFAULT NOW(),
    created_by_type VARCHAR(20),
    created_by_id VARCHAR(36)
);

-- Vector index
ALTER TABLE semantic_memory 
ADD INDEX idx_semantic_vec 
USING MLTREE VECTOR_cosine_ops (content_embedding) 
WITH (num_dimensions=1536, algorithm=hnsw);
```

---

## 9. Where SurrealDB Fits, If At All

### SurrealDB Recommendation: Not Required for Phase 1

**Only consider SurrealDB if:**

1. **Memory-graph experimentation** - Graph-native queries over memory relationships
2. **Embedded mode** - Local dev without infrastructure
3. **Real-time sync** - Unique websocket requirements

**Phase 1 exclusion reasons:**

1. **Ecosystem maturity** - Smaller than Postgres/Redis
2. **Production AI workloads** - Less proven than alternatives
3. **Staff expertise** - New learning curve
4. **Cost** - Managed pricing less competitive

### If Eventually Needed

```python
# SurrealDB would connect as separate graph store
# Only if memory-graph queries clearly justified
surrealdb_client = surrealdb.connect("mem://localhost:8000")
```

---

## 10. Compaction Checkpoint Storage Recommendation

### Primary: Postgres

```sql
-- New table for cortex checkpoints
CREATE TABLE cortex_checkpoint (
    checkpoint_id VARCHAR(36) PRIMARY KEY,
    thread_id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(36) NOT NULL,
    execution_request_id VARCHAR(36),
    
    -- Checkpoint data
    step_number INTEGER NOT NULL,
    state_data JSONB NOT NULL,
    state_hash VARCHAR(64),
    
    -- Metadata
    checkpoint_type VARCHAR(20),  -- thread, branch, worker, summary
    compressed BOOLEAN DEFAULT FALSE,
    size_bytes INTEGER,
    
    created_at DATETIME DEFAULT NOW()
);

-- Retention policy
CREATE INDEX idx_cortex_checkpoint_expiry 
ON cortex_checkpoint(created_at) 
WHERE expires_at IS NOT NULL;
```

### Secondary: Redis Hot Cache

```python
# Fast recovery from Redis within session
redis_client.setex(
    f"checkpoint:{thread_id}:latest",
    86400,  # 24 hours
    json.dumps(checkpoint_data)
)
```

### Compaction Policy Integration

```python
COMPACTION_POLICY = """
checkpoints:
  frequency: every_50_steps
  max_retention: 7_days
  compression: gzip
"""
```

---

## 11. Cortex Briefing Storage Recommendation

### Primary: Redis (Hot Briefs)

```python
# Brief for active threads in Redis
redis_client.setex(
    f"briefing:{thread_id}",
    604800,  # 7 days
    json.dumps({
        "summary": "...",
        "pending_actions": [...],
        "recommendations": [...],
        "generated_at": "..."
    })
)
```

### Archive: Postgres (Durable Briefs)

```sql
CREATE TABLE cortex_briefing (
    briefing_id VARCHAR(36) PRIMARY KEY,
    thread_id VARCHAR(36) NOT NULL,
    tenant_id VARCHAR(36) NOT NULL,
    execution_request_id VARCHAR(36),
    
    briefing_data JSONB NOT NULL,
    
    created_at DATETIME DEFAULT NOW(),
    expires_at DATETIME
);
```

### Briefing Generation Flow

```
execution_request → compile events → generate summary 
    → cache in Redis (hot) → archive in Postgres 
    → retrieve from Redis first (cache hit)
```

---

## 12. What Not to Introduce Yet

### Kafka

**Not required for Phase 1 because:**

1. **Synchronous request flow** - Current execution_request flow is sync
2. **Existing webhook model** - Async handled via callbacks
3. **LangGraph handles orchestration** - No need for separate orchestrator
4. **Complexity** - Adds operational burden

**Future consideration:** If async event processing at scale needed.

### Airflow

**Not required for Phase 1 because:**

1. **LangGraph handles DAG/workflow** - No need for separate workflow engine
2. **Existing task tables** - Task dependencies in Postgres
3. **No batch processing** - No ETL requirements yet

**Future consideration:** If complex batch scheduling required.

### Camunda

**Not required for Phase 1 because:**

1. **Existing workflow model** - No BPM engine requirements
2. **Approval flow** - Handled by approval_request entity
3. **State machines** - In existing control-plane design

**Future consideration:** If complex BPM requirements emerge.

---

## 13. Rollout Path

### Phase 1: Working Memory + Semantic Vector (Month 1-2)

| Task | Storage | Implementation |
|------|---------|----------------|
| Add Redis connection | Redis | Session cache |
| Working memory in Redis | Redis | Hash per thread_id |
| Semantic vector table | SingleStore | New table + HNSW index |
| Runtime registry | Redis | Runtime selection |

### Phase 2: Cortex and Checkpoints (Month 2-3)

| Task | Storage | Implementation |
|------|---------|----------------|
| Checkpoint table | Postgres | New cortex_checkpoint |
| Brief caching | Redis + Postgres | cortex_briefing |
| Compaction logic | Script | Scheduled cleanup |

### Phase 3: Full Integration (Month 3-4)

| Task | Storage | Implementation |
|------|---------|----------------|
| LangGraph state | Redis | Working memory integration |
| Episodic cache | Redis LRU | Event cache layer |
| Full briefing flow | Redis + Postgres | Complete workflow |

### Phase 4: Optimization (Month 4+)

| Task | Trigger |
|------|---------|
| Redis memory monitoring | Need for memory optimization |
| SurrealDB evaluation | Graph queries clearly needed |

---

## 14. Open Questions

| Question | Impact | Resolution Path |
|----------|--------|--------------|
| SingleStore vector vs Pinecone? | Cost, ecosystem | Evaluate both in Phase 1 |
| Checkpoint encryption at rest? | Security requirement | Deferred to security review |
| Redis Cluster needed? | Scale requirements | Monitor and add if needed |
| SurrealDB for memory-graph? | Experimentation | Phase 2 evaluation |

---

## Appendix A: Storage Comparison Matrix

| Storage | Latency | Persistence | Query | Vector | Cost | Scale |
|---------|--------|-------------|-------|-------|-------|-------|
| Redis | <1ms | Secondary | Limited | Yes (VSS) | $/GB | Vertical |
| SingleStore | <10ms | Primary | Full SQL | Native | $$/GB | Horizontal |
| Postgres | <10ms | Primary | Full SQL | Extension | $ | Vertical |

---

## Appendix B: Data Flow Examples

### Execution Flow with Memory

```
1. New execution_request → Postgres (authoritative)
2. Thread created → Redis working:{thread_id}
3. LangGraph executes → State in Redis working
4. Tools called → Events to Redis cache + Postgres history
5. Checkpoint needed → Postgre cortex_checkpoint
6. Brief generation → Redis briefing:{thread_id}
7. Semantic recall → SingleStore semantic_memory
8. Execution complete → UsageRecord to Postgres
```

### Retrieval Flow

```
1. User query → Redis working:{thread_id}
2. Cache miss → SingleStore (similarity search)
3. Semantic results → Return + cache in Redis
4. Postgres operational check → Task/milestone lookup
5. Response → User
```

---

_End of Memory & Storage Decision Matrix_