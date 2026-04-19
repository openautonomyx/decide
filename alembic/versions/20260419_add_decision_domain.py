"""Add decision domain tables

Revision ID: add_decision_domain
Revises: 
Create Date: 2026-04-19 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_decision_domain'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Decision table
    op.create_table(
        'decision',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenant.id'), nullable=False),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('project.id'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('sponsor_type', sa.String(20), nullable=True),
        sa.Column('sponsor_id', sa.String(36), nullable=True),
        sa.Column('owner_type', sa.String(20), nullable=True),
        sa.Column('owner_id', sa.String(36), nullable=True),
        sa.Column('risk_level', sa.String(50), nullable=True),
        sa.Column('decision_scope', sa.String(100), nullable=True),
        sa.Column('recommended_alternative_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_tenant_id', 'decision', ['tenant_id'])
    op.create_index('ix_decision_project_id', 'decision', ['project_id'])
    op.create_index('ix_decision_status', 'decision', ['status'])
    
    # Add FK for recommended_alternative_id after table exists
    op.create_foreign_key('fk_decision_recommended_alt', 'decision', 'decision_alternative', 
                         ['recommended_alternative_id'], ['id'])
    
    # DecisionAlternative table
    op.create_table(
        'decision_alternative',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('estimated_cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('estimated_time_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_alternative_decision_id', 'decision_alternative', ['decision_id'])
    
    # Re-add FK for recommended_alternative_id (table now exists)
    op.drop_constraint('fk_decision_recommended_alt', 'decision', type_='foreignkey')
    op.create_foreign_key('fk_decision_recommended_alt', 'decision', 'decision_alternative', 
                         ['recommended_alternative_id'], ['id'])
    
    # DecisionEvidence table
    op.create_table(
        'decision_evidence',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('evidence_type', sa.String(50), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('source_id', sa.String(36), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('url_or_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_evidence_decision_id', 'decision_evidence', ['decision_id'])
    
    # DecisionCriterion table
    op.create_table(
        'decision_criterion',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Numeric(5, 2), nullable=True, server_default='1.0'),
        sa.Column('scoring_method', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_criterion_decision_id', 'decision_criterion', ['decision_id'])
    
    # DecisionScore table
    op.create_table(
        'decision_score',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('alternative_id', sa.String(36), sa.ForeignKey('decision_alternative.id'), nullable=False),
        sa.Column('criterion_id', sa.String(36), sa.ForeignKey('decision_criterion.id'), nullable=False),
        sa.Column('score', sa.Numeric(5, 2), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_score_decision_id', 'decision_score', ['decision_id'])
    op.create_index('ix_decision_score_alternative_id', 'decision_score', ['alternative_id'])
    op.create_index('ix_decision_score_criterion_id', 'decision_score', ['criterion_id'])
    
    # DecisionRecommendation table
    op.create_table(
        'decision_recommendation',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('recommended_alternative_id', sa.String(36), sa.ForeignKey('decision_alternative.id'), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('tradeoffs', sa.Text(), nullable=True),
        sa.Column('generated_by_type', sa.String(20), nullable=True),
        sa.Column('generated_by_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_recommendation_decision_id', 'decision_recommendation', ['decision_id'])
    op.create_foreign_key('fk_recommendation_alt', 'decision_recommendation', 'decision_alternative',
                         ['recommended_alternative_id'], ['id'])
    
    # DecisionApprovalStep table
    op.create_table(
        'decision_approval_step',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('approver_type', sa.String(20), nullable=True),
        sa.Column('approver_id', sa.String(36), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('sequence_order', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_approval_step_decision_id', 'decision_approval_step', ['decision_id'])
    
    # DecisionOutcomeReview table
    op.create_table(
        'decision_outcome_review',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('outcome_status', sa.String(50), nullable=True),
        sa.Column('expected_vs_actual', sa.Text(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_outcome_review_decision_id', 'decision_outcome_review', ['decision_id'])
    
    # DecisionEvent table
    op.create_table(
        'decision_event',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decision.id'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_decision_event_decision_id', 'decision_event', ['decision_id'])
    op.create_index('ix_decision_event_created_at', 'decision_event', ['created_at'])


def downgrade() -> None:
    op.drop_table('decision_event')
    op.drop_table('decision_outcome_review')
    op.drop_table('decision_approval_step')
    op.drop_table('decision_recommendation')
    op.drop_table('decision_score')
    op.drop_table('decision_criterion')
    op.drop_table('decision_evidence')
    op.drop_table('decision_alternative')
    op.drop_table('decision')