"""
Decision API Router
"""
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.decision import (
    Decision as DecisionModel,
    DecisionAlternative as DecisionAlternativeModel,
    DecisionEvidence as DecisionEvidenceModel,
    DecisionCriterion as DecisionCriterionModel,
    DecisionScore as DecisionScoreModel,
    DecisionRecommendation as DecisionRecommendationModel,
    DecisionApprovalStep as DecisionApprovalStepModel,
    DecisionOutcomeReview as DecisionOutcomeReviewModel,
    DecisionEvent as DecisionEventModel,
)
from app.schemas.decision import (
    DecisionCreate, DecisionUpdate, Decision, DecisionList,
    DecisionAlternativeCreate, DecisionAlternativeUpdate, DecisionAlternative, DecisionAlternativeList,
    DecisionEvidenceCreate, DecisionEvidenceUpdate, DecisionEvidence, DecisionEvidenceList,
    DecisionCriterionCreate, DecisionCriterionUpdate, DecisionCriterion, DecisionCriterionList,
    DecisionScoreCreate, DecisionScoreUpdate, DecisionScore, DecisionScoreList,
    DecisionRecommendationCreate, DecisionRecommendationUpdate, DecisionRecommendation, DecisionRecommendationList,
    DecisionApprovalStepCreate, DecisionApprovalStepUpdate, DecisionApprovalStep, DecisionApprovalStepList,
    DecisionOutcomeReviewCreate, DecisionOutcomeReviewUpdate, DecisionOutcomeReview, DecisionOutcomeReviewList,
    DecisionEvent, DecisionEventList,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


# --- Decision CRUD ---


@router.get("", response_model=DecisionList)
def list_decisions(
    tenant_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(DecisionModel)
    if tenant_id:
        query = query.filter(DecisionModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return DecisionList(total=total, items=items)


@router.get("/{decision_id}", response_model=Decision)
def get_decision(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    return d


@router.post("", response_model=Decision, status_code=201)
def create_decision(decision_in: DecisionCreate, db: Session = Depends(get_db)):
    d = DecisionModel(id=str(uuid4()), **decision_in.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    # Create event
    event = DecisionEventModel(
        id=str(uuid4()),
        decision_id=d.id,
        event_type="created",
        event_data='{"action": "created"}'
    )
    db.add(event)
    db.commit()
    return d


@router.patch("/{decision_id}", response_model=Decision)
def update_decision(decision_id: str, decision_in: DecisionUpdate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    for f, v in decision_in.model_dump(exclude_unset=True).items():
        setattr(d, f, v)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{decision_id}", status_code=204)
def delete_decision(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    db.delete(d)
    db.commit()
    return None


# --- Alternatives ---


@router.get("/{decision_id}/alternatives", response_model=DecisionAlternativeList)
def list_alternatives(decision_id: str, db: Session = Depends(get_db)):
    # Verify decision exists
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionAlternativeModel).filter(DecisionAlternativeModel.decision_id == decision_id).all()
    return DecisionAlternativeList(total=len(items), items=items)


@router.post("/{decision_id}/alternatives", response_model=DecisionAlternative, status_code=201)
def create_alternative(decision_id: str, alt_in: DecisionAlternativeCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    alt = DecisionAlternativeModel(id=str(uuid4()), **alt_in.model_dump())
    db.add(alt)
    db.commit()
    db.refresh(alt)
    return alt


@router.patch("/alternatives/{alternative_id}", response_model=DecisionAlternative)
def update_alternative(alternative_id: str, alt_in: DecisionAlternativeUpdate, db: Session = Depends(get_db)):
    alt = db.query(DecisionAlternativeModel).filter(DecisionAlternativeModel.id == alternative_id).first()
    if not alt:
        raise HTTPException(404, "Alternative not found")
    for f, v in alt_in.model_dump(exclude_unset=True).items():
        setattr(alt, f, v)
    db.commit()
    db.refresh(alt)
    return alt


# --- Evidence ---


@router.get("/{decision_id}/evidence", response_model=DecisionEvidenceList)
def list_evidence(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionEvidenceModel).filter(DecisionEvidenceModel.decision_id == decision_id).all()
    return DecisionEvidenceList(total=len(items), items=items)


@router.post("/{decision_id}/evidence", response_model=DecisionEvidence, status_code=201)
def create_evidence(decision_id: str, ev_in: DecisionEvidenceCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    ev = DecisionEvidenceModel(id=str(uuid4()), **ev_in.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


# --- Criteria ---


@router.get("/{decision_id}/criteria", response_model=DecisionCriterionList)
def list_criteria(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionCriterionModel).filter(DecisionCriterionModel.decision_id == decision_id).all()
    return DecisionCriterionList(total=len(items), items=items)


@router.post("/{decision_id}/criteria", response_model=DecisionCriterion, status_code=201)
def create_criterion(decision_id: str, crit_in: DecisionCriterionCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    crit = DecisionCriterionModel(id=str(uuid4()), **crit_in.model_dump())
    db.add(crit)
    db.commit()
    db.refresh(crit)
    return crit


# --- Scores ---


@router.get("/{decision_id}/scores", response_model=DecisionScoreList)
def list_scores(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionScoreModel).filter(DecisionScoreModel.decision_id == decision_id).all()
    return DecisionScoreList(total=len(items), items=items)


@router.post("/{decision_id}/scores", response_model=DecisionScore, status_code=201)
def create_score(decision_id: str, score_in: DecisionScoreCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    score = DecisionScoreModel(id=str(uuid4()), **score_in.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


# --- Recommendations ---


@router.get("/{decision_id}/recommendation", response_model=DecisionRecommendation)
def get_recommendation(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    rec = db.query(DecisionRecommendationModel).filter(DecisionRecommendationModel.decision_id == decision_id).first()
    if not rec:
        raise HTTPException(404, "Recommendation not found")
    return rec


@router.post("/{decision_id}/recommendation", response_model=DecisionRecommendation, status_code=201)
def create_recommendation(decision_id: str, rec_in: DecisionRecommendationCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    rec = DecisionRecommendationModel(id=str(uuid4()), **rec_in.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    # Update decision status
    d.status = "recommended"
    db.commit()
    return rec


# --- Approvals ---


@router.get("/{decision_id}/approvals", response_model=DecisionApprovalStepList)
def list_approval_steps(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionApprovalStepModel).filter(DecisionApprovalStepModel.decision_id == decision_id).all()
    return DecisionApprovalStepList(total=len(items), items=items)


@router.post("/{decision_id}/approvals", response_model=DecisionApprovalStep, status_code=201)
def create_approval_step(decision_id: str, step_in: DecisionApprovalStepCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    step = DecisionApprovalStepModel(id=str(uuid4()), **step_in.model_dump())
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


# --- Outcomes ---


@router.get("/{decision_id}/outcomes", response_model=DecisionOutcomeReviewList)
def list_outcome_reviews(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionOutcomeReviewModel).filter(DecisionOutcomeReviewModel.decision_id == decision_id).all()
    return DecisionOutcomeReviewList(total=len(items), items=items)


@router.post("/{decision_id}/outcomes", response_model=DecisionOutcomeReview, status_code=201)
def create_outcome_review(decision_id: str, review_in: DecisionOutcomeReviewCreate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    review = DecisionOutcomeReviewModel(id=str(uuid4()), **review_in.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# --- Events ---


@router.get("/{decision_id}/events", response_model=DecisionEventList)
def list_decision_events(decision_id: str, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    items = db.query(DecisionEventModel).filter(DecisionEventModel.decision_id == decision_id).all()
    return DecisionEventList(total=len(items), items=items)