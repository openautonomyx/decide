"""
Agent API Router
Note: Agent is separate from Employee
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.session import get_db
from app.models.agent import Agent as AgentModel, EmployeeAgentAssignment
from app.schemas.agent import AgentCreate, AgentUpdate, Agent, AgentList
from app.schemas.collaboration import GroupMembership

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=AgentList)
def list_agents(tenant_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(AgentModel)
    if tenant_id:
        query = query.filter(AgentModel.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return AgentList(total=total, items=items)


@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("", response_model=Agent, status_code=201)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    agent = AgentModel(id=str(uuid4()), **agent_in.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.patch("/{agent_id}", response_model=Agent)
def update_agent(agent_id: str, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, value in agent_in.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return None


# Employee-Agent Assignment Routes
@router.post("/{agent_id}/assign", status_code=201)
def assign_agent_to_employee(agent_id: str, employee_id: str, role: str = "owner", db: Session = Depends(get_db)):
    # Verify agent exists
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    assignment = EmployeeAgentAssignment(
        id=str(uuid4()),
        employee_id=employee_id,
        agent_id=agent_id,
        assignment_role=role
    )
    db.add(assignment)
    db.commit()
    return {"status": "assigned", "agent_id": agent_id, "employee_id": employee_id, "role": role}