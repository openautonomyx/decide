"""Create base tables

Revision ID: base_tables
Revises: 
Create Date: 2026-04-19 03:10:00.000000

Base migration creating foundational tables:
- tenant
- project
- employee
- file_asset

"""
from alembic import op
import sqlalchemy as sa

revision = 'base_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tenant
    op.create_table(
        'tenant',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Project
    op.create_table(
        'project',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_project_tenant_id', 'project', ['tenant_id'])

    # Employee
    op.create_table(
        'employee',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_employee_tenant_id', 'employee', ['tenant_id'])

    # File Asset
    op.create_table(
        'file_asset',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500)),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_file_asset_tenant_id', 'file_asset', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('file_asset')
    op.drop_table('employee')
    op.drop_table('project')
    op.drop_table('tenant')