"""Add provider_name to execution_identity_binding and policy_evaluation_result

Revision ID: add_provider_name
Revises: add_execution_identity_binding
Create Date: 2026-04-19 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_provider_name'
down_revision = 'add_execution_identity_binding'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add provider_name column to execution_identity_binding
    op.add_column('execution_identity_binding', 
        sa.Column('provider_name', sa.String(50), nullable=False, server_default='autonomyx_agent_identity'))
    
    # Rename execution_identity_id to external_identity_id
    op.alter_column('execution_identity_binding', 'execution_identity_id',
        new_column_name='external_identity_id')
    
    # Drop source_system (now provider_name handles this)
    op.drop_column('execution_identity_binding', 'source_system')
    
    # Add provider_name to policy_evaluation_result
    op.add_column('policy_evaluation_result',
        sa.Column('provider_name', sa.String(50), nullable=True))
    
    # Rename execution_identity_id to external_identity_id
    op.alter_column('policy_evaluation_result', 'execution_identity_id',
        new_column_name='external_identity_id')


def downgrade() -> None:
    # Rename back
    op.alter_column('policy_evaluation_result', 'external_identity_id',
        new_column_name='execution_identity_id')
    op.drop_column('policy_evaluation_result', 'provider_name')
    
    op.add_column('execution_identity_binding',
        sa.Column('source_system', sa.String(50), server_default='autonomyx-agent-identity'))
    op.alter_column('execution_identity_binding', 'external_identity_id',
        new_column_name='execution_identity_id')
    op.drop_column('execution_identity_binding', 'provider_name')