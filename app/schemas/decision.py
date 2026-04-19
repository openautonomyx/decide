"""
Decision Domain Pydantic Schemas
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


# Decision Status Enum
class DecisionStatus:
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    RECOMMENDED = "recommended"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROMOTED = "promoted"
    COMPLETED = "completed"


# Decision Base Schemas
class DecisionBase(BaseModel):
    title: str
    description: str | None = None
    category: str | None = None
    status: str = DecisionStatus.DRAFT
    sponsor_type: str | None = None
    sponsor_id: str | None = None
    owner_type: str | None = None
    owner_id: str | None = None
    risk_level: str | None = None
    decision_scope: str | None = None


class DecisionCreate(DecisionBase):
    tenant_id: str
    project_id: str | None = None


class DecisionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    status: str | None = None
    sponsor_type: str | None = None
    sponsor_id: str | None = None
    owner_type: str | None = None
    owner_id: str | None = None
    risk_level: str | None = None
    decision_scope: str | None = None
    project_id: str | None = None
    recommended_alternative_id: str | None = None


class Decision(DecisionBase):
    id: str
    tenant_id: str
    project_id: str | None = None
    recommended_alternative_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionList(BaseModel):
    total: int
    items: list[Decision]


# Decision Alternative Schemas
class DecisionAlternativeBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "active"
    estimated_cost: float | None = None
    estimated_time_days: int | None = None


class DecisionAlternativeCreate(DecisionAlternativeBase):
    decision_id: str


class DecisionAlternativeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    estimated_cost: float | None = None
    estimated_time_days: int | None = None


class DecisionAlternative(DecisionAlternativeBase):
    id: str
    decision_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionAlternativeList(BaseModel):
    total: int
    items: list[DecisionAlternative]


# Decision Evidence Schemas
class DecisionEvidenceBase(BaseModel):
    title: str
    evidence_type: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    summary: str | None = None
    url_or_path: str | None = None


class DecisionEvidenceCreate(DecisionEvidenceBase):
    decision_id: str


class DecisionEvidenceUpdate(BaseModel):
    title: str | None = None
    evidence_type: str | None = None
    source_type: str | None = None
    source_id: str | None = None
    summary: str | None = None
    url_or_path: str | None = None


class DecisionEvidence(DecisionEvidenceBase):
    id: str
    decision_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionEvidenceList(BaseModel):
    total: int
    items: list[DecisionEvidence]


# Decision Criterion Schemas
class DecisionCriterionBase(BaseModel):
    name: str
    description: str | None = None
    weight: float = 1.0
    scoring_method: str | None = None


class DecisionCriterionCreate(DecisionCriterionBase):
    decision_id: str


class DecisionCriterionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    weight: float | None = None
    scoring_method: str | None = None


class DecisionCriterion(DecisionCriterionBase):
    id: str
    decision_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionCriterionList(BaseModel):
    total: int
    items: list[DecisionCriterion]


# Decision Score Schemas
class DecisionScoreBase(BaseModel):
    score: float | None = None
    rationale: str | None = None


class DecisionScoreCreate(DecisionScoreBase):
    decision_id: str
    alternative_id: str
    criterion_id: str


class DecisionScoreUpdate(BaseModel):
    score: float | None = None
    rationale: str | None = None


class DecisionScore(DecisionScoreBase):
    id: str
    decision_id: str
    alternative_id: str
    criterion_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionScoreList(BaseModel):
    total: int
    items: list[DecisionScore]


# Decision Recommendation Schemas
class DecisionRecommendationBase(BaseModel):
    summary: str | None = None
    rationale: str | None = None
    tradeoffs: str | None = None
    generated_by_type: str | None = None
    generated_by_id: str | None = None


class DecisionRecommendationCreate(DecisionRecommendationBase):
    decision_id: str
    recommended_alternative_id: str | None = None


class DecisionRecommendationUpdate(BaseModel):
    summary: str | None = None
    rationale: str | None = None
    tradeoffs: str | None = None
    recommended_alternative_id: str | None = None


class DecisionRecommendation(DecisionRecommendationBase):
    id: str
    decision_id: str
    recommended_alternative_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionRecommendationList(BaseModel):
    total: int
    items: list[DecisionRecommendation]


# Decision Approval Step Schemas
class DecisionApprovalStepBase(BaseModel):
    approver_type: str | None = None
    approver_id: str | None = None
    status: str = "pending"
    sequence_order: int = 1
    notes: str | None = None


class DecisionApprovalStepCreate(DecisionApprovalStepBase):
    decision_id: str


class DecisionApprovalStepUpdate(BaseModel):
    approver_type: str | None = None
    approver_id: str | None = None
    status: str | None = None
    notes: str | None = None


class DecisionApprovalStep(DecisionApprovalStepBase):
    id: str
    decision_id: str
    decided_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionApprovalStepList(BaseModel):
    total: int
    items: list[DecisionApprovalStep]


# Decision Outcome Review Schemas
class DecisionOutcomeReviewBase(BaseModel):
    review_date: datetime | None = None
    outcome_status: str | None = None
    expected_vs_actual: str | None = None
    lessons_learned: str | None = None
    reviewed_by: str | None = None


class DecisionOutcomeReviewCreate(DecisionOutcomeReviewBase):
    decision_id: str


class DecisionOutcomeReviewUpdate(BaseModel):
    review_date: datetime | None = None
    outcome_status: str | None = None
    expected_vs_actual: str | None = None
    lessons_learned: str | None = None
    reviewed_by: str | None = None


class DecisionOutcomeReview(DecisionOutcomeReviewBase):
    id: str
    decision_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionOutcomeReviewList(BaseModel):
    total: int
    items: list[DecisionOutcomeReview]


# Decision Event Schemas
class DecisionEvent(BaseModel):
    id: str
    decision_id: str
    event_type: str
    event_data: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DecisionEventList(BaseModel):
    total: int
    items: list[DecisionEvent]


# Detailed Decision Response Model
class DecisionDetail(BaseModel):
    """Complete decision with all nested data"""
    id: str
    tenant_id: str
    project_id: str | None = None
    title: str
    description: str | None = None
    category: str | None = None
    status: str
    sponsor_type: str | None = None
    sponsor_id: str | None = None
    owner_type: str | None = None
    owner_id: str | None = None
    risk_level: str | None = None
    decision_scope: str | None = None
    recommended_alternative_id: str | None = None
    created_at: datetime
    updated_at: datetime
    
    # Nested data
    alternatives: list[DecisionAlternative] = []
    evidence: list[DecisionEvidence] = []
    criteria: list[DecisionCriterion] = []
    recommendation: DecisionRecommendation | None = None
    approval_steps: list[DecisionApprovalStep] = []
    outcome_reviews: list[DecisionOutcomeReview] = []
    events: list[DecisionEvent] = []

    model_config = ConfigDict(from_attributes=True)