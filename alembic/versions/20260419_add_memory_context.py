"""Add memory_context to workflow run

Revision ID: add_memory_context
Revises: add_memory_skill
Create Date: 2026-04-19 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_memory_context'
down_revision = 'add_memory_skill'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add memory_context column to workflow_run for storing resolved memory context
    op.add_column('workflow_run', 
        sa.Column('memory_context_json', sa.Text, nullable=True)
    )


def downgrade() -> None:
    op.drop_column('workflow_run', 'memory_context_json')