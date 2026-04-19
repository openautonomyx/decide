"""Make memory durable and inspectable across runs

Revision ID: make_memory_persistent
Revises: add_memory_skill
Create Date: 2026-04-19 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'make_memory_persistent'
down_revision = 'add_memory_skill'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('memory_space', sa.Column('metadata_json', sa.Text(), nullable=True))
    op.add_column('memory_space', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')))

    op.add_column('memory_entry', sa.Column('source_metadata_json', sa.Text(), nullable=True))
    op.add_column('memory_entry', sa.Column('metadata_json', sa.Text(), nullable=True))

    op.add_column('workflow_run', sa.Column('memory_context_json', sa.Text(), nullable=True))
    op.add_column('workflow_run', sa.Column('memory_read_ids_json', sa.Text(), nullable=True))
    op.add_column('workflow_run', sa.Column('memory_written_ids_json', sa.Text(), nullable=True))
    op.add_column('workflow_run', sa.Column('memory_write_mode', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('workflow_run', 'memory_write_mode')
    op.drop_column('workflow_run', 'memory_written_ids_json')
    op.drop_column('workflow_run', 'memory_read_ids_json')
    op.drop_column('workflow_run', 'memory_context_json')

    op.drop_column('memory_entry', 'metadata_json')
    op.drop_column('memory_entry', 'source_metadata_json')

    op.drop_column('memory_space', 'is_active')
    op.drop_column('memory_space', 'metadata_json')
