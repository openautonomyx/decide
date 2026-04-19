"""Add resolved_skills_json to workflow_run

Revision ID: add_workflow_run_skills
Revises: add_memory_skill
Create Date: 2026-04-19 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_workflow_run_skills'
down_revision = 'add_memory_skill'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('workflow_run', sa.Column('resolved_skills_json', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('workflow_run', 'resolved_skills_json')