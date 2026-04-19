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
from app.models.control_plane import (
    ExecutionRequest as ExecutionRequestModel,
    DecisionRecord as DecisionRecordModel,
)
from app.schemas.decision import (
    DecisionCreate, DecisionUpdate, Decision, DecisionList,
    DecisionAlternativeCreate, DecisionAlternativeUpdate, DecisionAlternative, DecisionAlternativeList,
    DecisionEvidenceCreate, DecisionEvidence, DecisionEvidenceList,
    DecisionCriterionCreate, DecisionCriterion, DecisionCriterionList,
    DecisionScoreCreate, DecisionScore, DecisionScoreList,
    DecisionRecommendationCreate, DecisionRecommendation, DecisionRecommendationList,
    DecisionApprovalStepCreate, DecisionApprovalStep, DecisionApprovalStepList,
    DecisionOutcomeReviewCreate, DecisionOutcomeReview, DecisionOutcomeReviewList,
    DecisionEvent, DecisionEventList,
)

router = APIRouter(prefix="/decisions", tags=["decisions"])


def _create_event(db: Session, decision_id: str, event_type: str, event_data: str = None):
    """Helper to create decision events."""
    event = DecisionEventModel(
        id=str(uuid4()),
        decision_id=decision_id,
        event_type=event_type,
        event_data=event_data,
    )
    db.add(event)
    return event


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
    _create_event(db, d.id, "created", '{"action": "created"}')
    db.commit()
    return d


@router.patch("/{decision_id}", response_model=Decision)
def update_decision(decision_id: str, decision_in: DecisionUpdate, db: Session = Depends(get_db)):
    d = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not d:
        raise HTTPException(404, "Decision not found")
    old_status = d.status
    for f, v in decision_in.model_dump(exclude_unset=True).items():
        setattr(d, f, v)
    db.commit()
    db.refresh(d)
    # Event on status change
    if d.status != old_status:
        _create_event(db, d.id, "status_changed", f'{{"old": "{old_status}", "new": "{d.status}"}}')
        db.commit()
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
    # Use path decision_id, ignore body decision_id
    alt_data = alt_in.model_dump(exclude={"decision_id"})
    alt = DecisionAlternativeModel(id=str(uuid4()), decision_id=decision_id, **alt_data)
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
    # Use path decision_id
    ev_data = ev_in.model_dump(exclude={"decision_id"})
    ev = DecisionEvidenceModel(id=str(uuid4()), decision_id=decision_id, **ev_data)
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
    # Use path decision_id
    crit_data = crit_in.model_dump(exclude={"decision_id"})
    crit = DecisionCriterionModel(id=str(uuid4()), decision_id=decision_id, **crit_data)
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
    
    # Validate alternative belongs to this decision
    alt = db.query(DecisionAlternativeModel).filter(
        DecisionAlternativeModel.id == score_in.alternative_id,
        DecisionAlternativeModel.decision_id == decision_id
    ).first()
    if not alt:
        raise HTTPException(400, "Alternative not found for this decision")
    
    # Validate criterion belongs to this decision
    crit = db.query(DecisionCriterionModel).filter(
        DecisionCriterionModel.id == score_in.criterion_id,
        DecisionCriterionModel.decision_id == decision_id
    ).first()
    if not crit:
        raise HTTPException(400, "Criterion not found for this decision")
    
    # Use path decision_id
    score_data = score_in.model_dump(exclude={"decision_id"})
    score = DecisionScoreModel(id=str(uuid4()), decision_id=decision_id, **score_data)
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
    
    # Validate recommended_alternative if provided
    if rec_in.recommended_alternative_id:
        alt = db.query(DecisionAlternativeModel).filter(
            DecisionAlternativeModel.id == rec_in.recommended_alternative_id,
            DecisionAlternativeModel.decision_id == decision_id
        ).first()
        if not alt:
            raise HTTPException(400, "Recommended alternative not found for this decision")
    
    # Use path decision_id
    rec_data = rec_in.model_dump(exclude={"decision_id"})
    rec = DecisionRecommendationModel(id=str(uuid4()), decision_id=decision_id, **rec_data)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    
    # Create event
    _create_event(db, decision_id, "recommendation_created", f'{{"recommendation_id": "{rec.id}"}}')
    db.commit()
    
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
    # Use path decision_id
    step_data = step_in.model_dump(exclude={"decision_id"})
    step = DecisionApprovalStepModel(id=str(uuid4()), decision_id=decision_id, **step_data)
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
    # Use path decision_id
    review_data = review_in.model_dump(exclude={"decision_id"})
    review = DecisionOutcomeReviewModel(id=str(uuid4()), decision_id=decision_id, **review_data)
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


# --- Promote to Execution ---


@router.post("/{decision_id}/promote-to-execution", status_code=201)
def promote_decision_to_execution(decision_id: str, db: Session = Depends(get_db)):
    """
    Promote an approved decision to an execution request.
    
    Interim approval rule (must satisfy ONE):
      a) decision.status == "approved"
      OR
      b) there is at least one approval step AND all approval steps are approved
    
    Idempotency: Rejects if decision is already promoted.
    """
    # 1. Validate decision exists
    decision = db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
    if not decision:
        raise HTTPException(404, "Decision not found")
    
    # 2. Idempotency: prevent duplicate promotion
    if decision.status == "promoted":
        raise HTTPException(400, "Decision has already been promoted")
    
    # Check if promotion event exists
    existing_promotion = db.query(DecisionEventModel).filter(
        DecisionEventModel.decision_id == decision_id,
        DecisionEventModel.event_type == "promoted_to_execution"
    ).first()
    if existing_promotion:
        raise HTTPException(400, "Decision has already been promoted")
    
    # 3. Validate decision has a recommendation
    recommendation = db.query(DecisionRecommendationModel).filter(
        DecisionRecommendationModel.decision_id == decision_id
    ).first()
    if not recommendation:
        raise HTTPException(400, "Decision has no recommendation")
    
    # 4. Validate recommended_alternative belongs to this decision
    if recommendation.recommended_alternative_id:
        alt = db.query(DecisionAlternativeModel).filter(
            DecisionAlternativeModel.id == recommendation.recommended_alternative_id,
            DecisionAlternativeModel.decision_id == decision_id
        ).first()
        if not alt:
            raise HTTPException(400, "Recommended alternative not found for this decision")
    
    # 5. Validate approval requirements (interim rule)
    # Rule: (a) status == "approved" OR (b) all approval steps are approved
    rule_a_satisfied = decision.status == "approved"
    
    approval_steps = db.query(DecisionApprovalStepModel).filter(
        DecisionApprovalStepModel.decision_id == decision_id
    ).all()
    
    rule_b_satisfied = False
    if approval_steps:
        all_approved = all(s.status == "approved" for s in approval_steps)
        if all_approved:
            rule_b_satisfied = True
    
    if not (rule_a_satisfied or rule_b_satisfied):
        if rule_a_satisfied is False and rule_b_satisfied is False:
            raise HTTPException(400, "Decision must be in 'approved' status or have all approval steps approved")
        # More detailed message
        if not approval_steps:
            raise HTTPException(400, "Decision must have at least one approval step to be promoted")
        pending = [s for s in approval_steps if s.status != "approved"]
        raise HTTPException(400, f"Decision has {len(pending)} pending approval steps")
    
    # 6. Get the recommended alternative
    recommended_alt = None
    if recommendation.recommended_alternative_id:
        recommended_alt = db.query(DecisionAlternativeModel).filter(
            DecisionAlternativeModel.id == recommendation.recommended_alternative_id
        ).first()
    
    # 7. Build execution request goal from decision data
    goal = f"Execute decision: {decision.title}"
    if recommendation.rationale:
        goal += f"\n\nRationale: {recommendation.rationale}"
    if recommended_alt and recommended_alt.description:
        goal += f"\n\nAlternative: {recommended_alt.title} - {recommended_alt.description}"
    
    # 8. Create ExecutionRequest
    exec_req = ExecutionRequestModel(
        id=str(uuid4()),
        tenant_id=decision.tenant_id,
        goal=goal,
        capability="decision_execution",
        quality="standard",
        status="pending",
    )
    db.add(exec_req)
    db.commit()
    db.refresh(exec_req)
    
    # 9. Create DecisionRecord bridge for backward compatibility
    decision_record = DecisionRecordModel(
        id=str(uuid4()),
        execution_request_id=exec_req.id,
        decision_type="promoted_decision",
        decision_reason=recommendation.rationale or recommendation.summary or "Decision promoted to execution",
    )
    db.add(decision_record)
    db.commit()
    
    # 10. Create DecisionEvent for status change to promoted
    _create_event(
        db, 
        decision_id, 
        "status_changed", 
        f'{{"old": "approved", "new": "promoted"}}'
    )
    
    # 11. Create DecisionEvent for promotion
    _create_event(
        db, 
        decision_id, 
        "promoted_to_execution", 
        f'{{"execution_request_id": "{exec_req.id}", "decision_record_id": "{decision_record.id}"}}'
    )
    db.commit()
    
    # 12. Update decision status
    decision.status = "promoted"
    db.commit()
    
    return {
        "decision_id": decision_id,
        "execution_request_id": exec_req.id,
        "decision_record_id": decision_record.id,
        "status": "promoted",
    }