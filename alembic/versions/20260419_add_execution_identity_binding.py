"""Add execution identity binding tables

Revision ID: add_execution_identity_binding
Revises: add_workflow_skeleton
Create Date: 2026-04-19 04:00:00.000000

This migration adds the execution identity binding and policy evaluation result tables.
These tables bind external execution identities from autonomyx-agent-identity to Decide workflows.

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_execution_identity_binding'
down_revision = 'add_workflow_skeleton'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Execution Identity Binding
    op.create_table(
        'execution_identity_binding',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36)),
        sa.Column('workflow_version_id', sa.String(36)),
        sa.Column('template_id', sa.String(36)),
        sa.Column('execution_identity_id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('agent_name', sa.String(255)),
        sa.Column('agent_type', sa.String(50)),
        sa.Column('sponsor_id', sa.String(36)),
        sa.Column('owner_ids_json', sa.Text()),
        sa.Column('manager_id', sa.String(36)),
        sa.Column('blueprint_id', sa.String(36)),
        sa.Column('allowed_models_json', sa.Text()),
        sa.Column('budget_limit', sa.Numeric(12, 2)),
        sa.Column('tpm_limit', sa.Integer),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('source_system', sa.String(50), server_default='autonomyx-agent-identity'),
        sa.Column('last_synced_at', sa.DateTime()),
        sa.Column('metadata_json', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_eib_tenant_id', 'execution_identity_binding', ['tenant_id'])
    op.create_index('ix_eib_workflow_id', 'execution_identity_binding', ['workflow_id'])

    # Policy Evaluation Result
    op.create_table(
        'policy_evaluation_result',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36)),
        sa.Column('workflow_version_id', sa.String(36)),
        sa.Column('run_id', sa.String(36)),
        sa.Column('execution_identity_id', sa.String(36)),
        sa.Column('evaluation_type', sa.String(50), nullable=False),
        sa.Column('is_allowed', sa.Boolean, nullable=False),
        sa.Column('reasons_json', sa.Text()),
        sa.Column('metadata_json', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_per_workflow_id', 'policy_evaluation_result', ['workflow_id'])
    op.create_index('ix_per_evaluation_type', 'policy_evaluation_result', ['evaluation_type'])


def downgrade() -> None:
    op.drop_table('policy_evaluation_result')
    op.drop_table('execution_identity_binding')