"""Add templates and component registry tables

Revision ID: add_templates_and_components
Revises: add_memory_skill
Create Date: 2026-04-19 03:55:00.000000

This migration adds:
- Template packs and workflow templates
- Component registry (definitions, versions, capabilities)

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_templates_and_components'
down_revision = 'add_memory_skill'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== Template Pack =====
    op.create_table(
        'template_pack',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_template_pack_name', 'template_pack', ['name'])
    op.create_index('ix_template_pack_is_default', 'template_pack', ['is_default'])
    
    # ===== Workflow Template =====
    op.create_table(
        'workflow_template',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('pack_id', sa.String(36), sa.ForeignKey('template_pack.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('published_version_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_template_pack_id', 'workflow_template', ['pack_id'])
    op.create_index('ix_workflow_template_category', 'workflow_template', ['category'])
    
    # ===== Workflow Template Version =====
    op.create_table(
        'workflow_template_version',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('template_id', sa.String(36), sa.ForeignKey('workflow_template.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('runtime_spec', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_template_version_template_id', 'workflow_template_version', ['template_id'])
    
    # ===== Component Definition =====
    op.create_table(
        'component_definition',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_component_definition_name', 'component_definition', ['name'])
    op.create_index('ix_component_definition_category', 'component_definition', ['category'])
    
    # ===== Component Version =====
    op.create_table(
        'component_version',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('component_id', sa.String(36), sa.ForeignKey('component_definition.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('schema_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_component_version_component_id', 'component_version', ['component_id'])
    
    # ===== Component Capability =====
    op.create_table(
        'component_capability',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('component_id', sa.String(36), sa.ForeignKey('component_definition.id'), nullable=False),
        sa.Column('capability_type', sa.String(100), nullable=False),
        sa.Column('capability_config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_component_capability_component_id', 'component_capability', ['component_id'])
    op.create_index('ix_component_capability_type', 'component_capability', ['capability_type'])


def downgrade() -> None:
    op.drop_table('component_capability')
    op.drop_table('component_version')
    op.drop_table('component_definition')
    op.drop_table('workflow_template_version')
    op.drop_table('workflow_template')
    op.drop_table('template_pack')