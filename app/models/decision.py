# Decision Domain SQLAlchemy Models
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Numeric, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Decision(Base):
    __tablename__ = "decision"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenant.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("project.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    status = Column(String(50), default="draft")
    sponsor_type = Column(String(20))
    sponsor_id = Column(String(36))
    owner_type = Column(String(20))
    owner_id = Column(String(36))
    risk_level = Column(String(50))
    decision_scope = Column(String(100))
    recommended_alternative_id = Column(String(36), ForeignKey("decision_alternative.id", name="fk_decision_recommended_alt"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", backref="decisions")
    project = relationship("Project", backref="decisions")
    alternatives = relationship("DecisionAlternative", back_populates="decision", cascade="all, delete-orphan")
    evidence = relationship("DecisionEvidence", back_populates="decision", cascade="all, delete-orphan")
    criteria = relationship("DecisionCriterion", back_populates="decision", cascade="all, delete-orphan")
    scores = relationship("DecisionScore", back_populates="decision", cascade="all, delete-orphan")
    recommendations = relationship("DecisionRecommendation", back_populates="decision", cascade="all, delete-orphan")
    approval_steps = relationship("DecisionApprovalStep", back_populates="decision", cascade="all, delete-orphan")
    outcome_reviews = relationship("DecisionOutcomeReview", back_populates="decision", cascade="all, delete-orphan")
    events = relationship("DecisionEvent", back_populates="decision", cascade="all, delete-orphan")


class DecisionAlternative(Base):
    __tablename__ = "decision_alternative"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    estimated_cost = Column(Numeric(12, 2))
    estimated_time_days = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="alternatives")
    scores = relationship("DecisionScore", back_populates="alternative", cascade="all, delete-orphan")


class DecisionEvidence(Base):
    __tablename__ = "decision_evidence"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    evidence_type = Column(String(50))
    source_type = Column(String(50))
    source_id = Column(String(36))
    title = Column(String(255), nullable=False)
    summary = Column(Text)
    url_or_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="evidence")


class DecisionCriterion(Base):
    __tablename__ = "decision_criterion"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    weight = Column(Numeric(5, 2), default=1.0)
    scoring_method = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="criteria")
    scores = relationship("DecisionScore", back_populates="criterion", cascade="all, delete-orphan")


class DecisionScore(Base):
    __tablename__ = "decision_score"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    alternative_id = Column(String(36), ForeignKey("decision_alternative.id"), nullable=False)
    criterion_id = Column(String(36), ForeignKey("decision_criterion.id"), nullable=False)
    score = Column(Numeric(5, 2))
    rationale = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="scores")
    alternative = relationship("DecisionAlternative", back_populates="scores")
    criterion = relationship("DecisionCriterion", back_populates="scores")


class DecisionRecommendation(Base):
    __tablename__ = "decision_recommendation"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    recommended_alternative_id = Column(String(36), ForeignKey("decision_alternative.id", name="fk_recommendation_alt"))
    summary = Column(Text)
    rationale = Column(Text)
    tradeoffs = Column(Text)
    generated_by_type = Column(String(20))
    generated_by_id = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="recommendations")
    recommended_alternative = relationship("DecisionAlternative")


class DecisionApprovalStep(Base):
    __tablename__ = "decision_approval_step"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    approver_type = Column(String(20))
    approver_id = Column(String(36))
    status = Column(String(50), default="pending")
    sequence_order = Column(Integer, default=1)
    notes = Column(Text)
    decided_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="approval_steps")


class DecisionOutcomeReview(Base):
    __tablename__ = "decision_outcome_review"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    review_date = Column(DateTime)
    outcome_status = Column(String(50))
    expected_vs_actual = Column(Text)
    lessons_learned = Column(Text)
    reviewed_by = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="outcome_reviews")


class DecisionEvent(Base):
    __tablename__ = "decision_event"

    id = Column(String(36), primary_key=True)
    decision_id = Column(String(36), ForeignKey("decision.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text)  # JSONB in schema
    created_at = Column(DateTime, server_default=func.now())

    decision = relationship("Decision", back_populates="events")