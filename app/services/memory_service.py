"""Memory service for durable recall and explicit write-back."""
from __future__ import annotations

import json
from uuid import uuid4
from typing import Any
from sqlalchemy.orm import Session

from app.models.memory import MemorySpace, MemoryEntry

SCOPE_PRIORITY = ["organization", "product", "workflow", "run", "session"]


class MemoryService:
    @staticmethod
    def get_or_create_space(
        db: Session,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        name: str | None = None,
    ) -> MemorySpace:
        space = db.query(MemorySpace).filter(
            MemorySpace.tenant_id == tenant_id,
            MemorySpace.scope_type == scope_type,
            MemorySpace.scope_id == scope_id,
            MemorySpace.is_active == True,
        ).first()
        if space:
            return space

        space = MemorySpace(
            id=str(uuid4()),
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
            name=name or f"{scope_type}:{scope_id}",
            is_active=True,
        )
        db.add(space)
        db.flush()
        return space

    @staticmethod
    def persist_entry(
        db: Session,
        *,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        memory_type: str,
        title: str,
        content: str,
        tags: list[str] | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        source_metadata: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        space_name: str | None = None,
    ) -> MemoryEntry:
        space = MemoryService.get_or_create_space(
            db,
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
            name=space_name,
        )

        entry = MemoryEntry(
            id=str(uuid4()),
            memory_space_id=space.id,
            memory_type=memory_type,
            title=title,
            content=content,
            tags_json=json.dumps(tags or []),
            source_type=source_type,
            source_id=source_id,
            source_metadata_json=json.dumps(source_metadata) if source_metadata else None,
            metadata_json=json.dumps(metadata) if metadata else None,
            is_active=True,
        )
        db.add(entry)
        db.flush()
        return entry

    @staticmethod
    def resolve(
        db: Session,
        *,
        tenant_id: str,
        scopes: dict[str, str],
        memory_type: str | None = None,
        tags: list[str] | None = None,
        is_active: bool = True,
        limit_per_scope: int = 100,
    ) -> tuple[list[MemoryEntry], list[str], list[dict[str, Any]]]:
        all_entries: list[MemoryEntry] = []
        resolved_scopes: list[str] = []
        context: list[dict[str, Any]] = []

        for scope in SCOPE_PRIORITY:
            scope_id = scopes.get(scope)
            if not scope_id:
                continue
            space = db.query(MemorySpace).filter(
                MemorySpace.tenant_id == tenant_id,
                MemorySpace.scope_type == scope,
                MemorySpace.scope_id == scope_id,
                MemorySpace.is_active == True,
            ).first()
            if not space:
                continue

            q = db.query(MemoryEntry).filter(MemoryEntry.memory_space_id == space.id)
            if is_active:
                q = q.filter(MemoryEntry.is_active == True)
            if memory_type:
                q = q.filter(MemoryEntry.memory_type == memory_type)

            entries = q.order_by(MemoryEntry.created_at.desc()).limit(limit_per_scope).all()
            if tags:
                tags_lower = {t.lower() for t in tags}
                entries = [
                    e for e in entries
                    if any(t.lower() in tags_lower for t in json.loads(e.tags_json or "[]"))
                ]

            if entries:
                resolved_scopes.append(scope)
                all_entries.extend(entries)
                context.append(
                    {
                        "scope_type": scope,
                        "scope_id": scope_id,
                        "entries": entries,
                    }
                )

        return all_entries, resolved_scopes, context
