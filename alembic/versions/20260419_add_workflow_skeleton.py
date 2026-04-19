"""Add workflow skeleton tables

Revision ID: add_workflow_skeleton
Revises: add_decision_domain
Create Date: 2026-04-19 02:35:00.000000

This migration adds the workflow skeleton tables for the Decide Studio.
Tables were added after the decision domain migration.

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_workflow_skeleton'
down_revision = 'add_decision_domain'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Workflow definition
    op.create_table(
        'workflow_definition',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True, server_default='langflow'),
        sa.Column('source_json', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('published_version_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_definition_tenant_id', 'workflow_definition', ['tenant_id'])
    op.create_index('ix_workflow_definition_is_published', 'workflow_definition', ['is_published'])
    
    # 2. Workflow version
    op.create_table(
        'workflow_version',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflow_definition.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('runtime_spec', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_version_workflow_id', 'workflow_version', ['workflow_id'])
    
    # 3. Workflow node
    op.create_table(
        'workflow_node',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('workflow_version.id'), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=True),
        sa.Column('position_y', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_node_version_id', 'workflow_node', ['version_id'])
    op.create_index('ix_workflow_node_node_type', 'workflow_node', ['node_type'])
    
    # 4. Workflow edge
    op.create_table(
        'workflow_edge',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('workflow_version.id'), nullable=False),
        sa.Column('edge_id', sa.String(100), nullable=True),
        sa.Column('source_node_id', sa.String(100), nullable=False),
        sa.Column('target_node_id', sa.String(100), nullable=False),
        sa.Column('edge_type', sa.String(50), nullable=True, server_default='smooth'),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('condition', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_edge_version_id', 'workflow_edge', ['version_id'])
    
    # 5. Workflow validation result
    op.create_table(
        'workflow_validation_result',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflow_definition.id'), nullable=False),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('workflow_version.id'), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('issues_json', sa.Text(), nullable=True),
        sa.Column('can_publish', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_validation_result_workflow_id', 'workflow_validation_result', ['workflow_id'])
    
    # 6. Workflow publish artifact
    op.create_table(
        'workflow_publish_artifact',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflow_definition.id'), nullable=False),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('workflow_version.id'), nullable=False),
        sa.Column('artifact_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_workflow_publish_artifact_workflow_id', 'workflow_publish_artifact', ['workflow_id'])
    
    # 7. Workflow run
    op.create_table(
        'workflow_run',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), sa.ForeignKey('workflow_definition.id'), nullable=False),
        sa.Column('version_id', sa.String(36), sa.ForeignKey('workflow_version.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('final_output', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
    )
    op.create_index('ix_workflow_run_workflow_id', 'workflow_run', ['workflow_id'])
    op.create_index('ix_workflow_run_status', 'workflow_run', ['status'])
    
    # 8. Workflow run step
    op.create_table(
        'workflow_run_step',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('run_id', sa.String(36), sa.ForeignKey('workflow_run.id'), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('branch_decision', sa.String(50), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_workflow_run_step_run_id', 'workflow_run_step', ['run_id'])


def downgrade() -> None:
    op.drop_table('workflow_run_step')
    op.drop_table('workflow_run')
    op.drop_table('workflow_publish_artifact')
    op.drop_table('workflow_validation_result')
    op.drop_table('workflow_edge')
    op.drop_table('workflow_node')
    op.drop_table('workflow_version')
    op.drop_table('workflow_definition')