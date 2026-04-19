"""Add memory and skill tables

Revision ID: add_memory_skill
Revises: add_provider_name
Create Date: 2026-04-19 04:35:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_memory_skill'
down_revision = 'add_provider_name'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Memory tables
    op.create_table('memory_space',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('scope_type', sa.String(50), nullable=False),
        sa.Column('scope_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table('memory_entry',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('memory_space_id', sa.String(36), nullable=False, index=True),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tags_json', sa.Text),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', sa.String(36)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    # Skill tables
    op.create_table('skill_definition',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('scope_type', sa.String(50)),
        sa.Column('scope_id', sa.String(36), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('skill_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table('skill_version',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('skill_id', sa.String(36), nullable=False, index=True),
        sa.Column('version_number', sa.Integer, nullable=False),
        sa.Column('content_json', sa.Text, nullable=False),
        sa.Column('input_schema_json', sa.Text),
        sa.Column('output_schema_json', sa.Text),
        sa.Column('tool_requirements_json', sa.Text),
        sa.Column('metadata_json', sa.Text),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table('skill_binding',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('skill_id', sa.String(36), nullable=False, index=True),
        sa.Column('workflow_id', sa.String(36), nullable=True),
        sa.Column('template_id', sa.String(36), nullable=True),
        sa.Column('component_id', sa.String(36), nullable=True),
        sa.Column('agent_role', sa.String(50), nullable=True),
        sa.Column('binding_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    
    op.create_table('skill_promotion_record',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('source_id', sa.String(36), nullable=False),
        sa.Column('skill_id', sa.String(36), nullable=False, index=True),
        sa.Column('promoted_by', sa.String(36)),
        sa.Column('reason', sa.Text),
        sa.Column('evidence_json', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('skill_promotion_record')
    op.drop_table('skill_binding')
    op.drop_table('skill_version')
    op.drop_table('skill_definition')
    op.drop_table('memory_entry')
    op.drop_table('memory_space')