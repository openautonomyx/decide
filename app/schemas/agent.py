"""
Agent Pydantic Schemas
Note: Agent is separate from Employee
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
# from uuid import UUID (DB uses VARCHAR(36))


class AgentBase(BaseModel):
    name: str
    agent_type: str | None = None
    is_primary: bool = False


class AgentCreate(AgentBase):
    tenant_id: str


class AgentUpdate(BaseModel):
    name: str | None = None
    agent_type: str | None = None
    is_primary: bool | None = None


class Agent(AgentBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AgentWithRelations(Agent):
    owner_employee_id: str | None = None
    goals: list["AgentGoal"] = []
    skills: list["AgentSkill"] = []


class AgentGoalBase(BaseModel):
    goal_type: str | None = None  # short_term/long_term/ambition
    description: str | None = None
    target_date: datetime | None = None


class AgentGoalCreate(AgentGoalBase):
    agent_id: str


class AgentGoal(AgentGoalBase):
    id: str
    agent_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AgentSkillBase(BaseModel):
    skill_code: str | None = None
    skill_name: str | None = None
    proficiency_level: str | None = None


class AgentSkillCreate(AgentSkillBase):
    agent_id: str


class AgentSkill(AgentSkillBase):
    id: str
    agent_id: str
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeAgentAssignmentBase(BaseModel):
    assignment_role: str | None = None  # owner/supervisor/sponsor


class EmployeeAgentAssignmentCreate(EmployeeAgentAssignmentBase):
    employee_id: str
    agent_id: str


class EmployeeAgentAssignment(EmployeeAgentAssignmentBase):
    id: str
    employee_id: str
    agent_id: str
    assigned_at: datetime
    ended_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class AgentList(BaseModel):
    total: int
    items: list[Agent]


