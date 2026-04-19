# Seed Data - Initial template packs and component registry data
import json
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.template import TemplatePack, WorkflowTemplate, WorkflowTemplateVersion
from app.models.component import ComponentDefinition, ComponentVersion, ComponentCapability


def seed_template_packs_and_templates(db: Session):
    """Seed default template pack and demo publish workflow template."""
    
    # Check if already seeded
    existing_pack = db.query(TemplatePack).filter(TemplatePack.name == "publish").first()
    if existing_pack:
        return  # Already seeded
    
    # Create default "publish" template pack
    pack = TemplatePack(
        id=str(uuid4()),
        name="publish",
        description="Publishing workflows for decision automation",
        is_default=True,
    )
    db.add(pack)
    db.commit()
    db.refresh(pack)
    
    # Create demo-ready publish workflow template
    template = WorkflowTemplate(
        id=str(uuid4()),
        pack_id=pack.id,
        name="basic-publish",
        description="Basic publish workflow with LLM, tool, and approval",
        category="publish",
        tags=json.dumps(["demo", "publish", "approval"]),
        is_published=True,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    # Create runtime spec for the template
    runtime_spec = {
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "label": "Start",
                "config": {},
            },
            {
                "id": "llm_1",
                "type": "llm",
                "label": "Generate Content",
                "config": {
                    "model": "gpt-4o",
                    "prompt": "Generate a publish decision document.",
                },
            },
            {
                "id": "condition_1",
                "type": "condition",
                "label": "Auto Approve?",
                "config": {
                    "condition": "${auto_approve}",
                },
            },
            {
                "id": "tool_1",
                "type": "tool",
                "label": "Publish to Channel",
                "config": {
                    "tool_name": "channel_publish",
                    "channel_id": "${channel_id}",
                },
            },
            {
                "id": "human_approval_1",
                "type": "human_approval",
                "label": "Get Approval",
                "config": {
                    "approver_email": "${approver_email}",
                },
            },
            {
                "id": "end_1",
                "type": "end",
                "label": "Complete",
                "config": {},
            },
        ],
        "edges": [
            {"source": "start_1", "target": "llm_1"},
            {"source": "llm_1", "target": "condition_1"},
            {"source": "condition_1", "target": "tool_1", "label": "true"},
            {"source": "condition_1", "target": "human_approval_1", "label": "false"},
            {"source": "tool_1", "target": "end_1"},
            {"source": "human_approval_1", "target": "end_1"},
        ],
    }
    
    version = WorkflowTemplateVersion(
        id=str(uuid4()),
        template_id=template.id,
        version_number=1,
        is_current=True,
        runtime_spec=json.dumps(runtime_spec),
    )
    db.add(version)
    db.commit()
    
    # Update template with published version
    template.published_version_id = version.id
    db.commit()
    
    print(f"Seeded template pack '{pack.name}' with template '{template.name}'")


def seed_mvp_components(db: Session):
    """Seed MVP component definitions."""
    
    # MVP components to seed
    mvp_components = [
        {
            "name": "start",
            "display_name": "Start",
            "description": "Workflow start node - entry point for workflow execution",
            "category": "control",
            "icon": "play",
            "capabilities": [
                {"capability_type": "start_workflow", "capability_config": {}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Initial input"},
                },
            },
        },
        {
            "name": "llm",
            "display_name": "LLM",
            "description": "Large language model node - generates content using AI",
            "category": "ai",
            "icon": "brain",
            "capabilities": [
                {"capability_type": "execute_llm", "capability_config": {"temperature": 0.7}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "prompt": {"type": "string"},
                    "temperature": {"type": "number"},
                    "max_tokens": {"type": "integer"},
                },
                "required": ["model", "prompt"],
            },
        },
        {
            "name": "tool",
            "display_name": "Tool",
            "description": "Tool execution node - calls external tools or APIs",
            "category": "integration",
            "icon": "wrench",
            "capabilities": [
                {"capability_type": "call_tool", "capability_config": {}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "tool_config": {"type": "object"},
                },
                "required": ["tool_name"],
            },
        },
        {
            "name": "condition",
            "display_name": "Condition",
            "description": "Conditional branching node - routes based on boolean logic",
            "category": "control",
            "icon": "git-branch",
            "capabilities": [
                {"capability_type": "evaluate_condition", "capability_config": {}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string"},
                    "expression": {"type": "string"},
                },
                "required": ["condition"],
            },
        },
        {
            "name": "human_approval",
            "display_name": "Human Approval",
            "description": "Human approval node - pauses for human decision",
            "category": "integration",
            "icon": "user-check",
            "capabilities": [
                {"capability_type": "await_approval", "capability_config": {}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "approver_email": {"type": "string"},
                    "approval_timeout": {"type": "integer"},
                    "instructions": {"type": "string"},
                },
            },
        },
        {
            "name": "end",
            "display_name": "End",
            "description": "Workflow end node - terminates workflow execution",
            "category": "control",
            "icon": "stop",
            "capabilities": [
                {"capability_type": "end_workflow", "capability_config": {}},
            ],
            "schema": {
                "type": "object",
                "properties": {
                    "output": {"type": "string"},
                },
            },
        },
    ]
    
    for comp_data in mvp_components:
        # Check if already exists
        existing = db.query(ComponentDefinition).filter(
            ComponentDefinition.name == comp_data["name"]
        ).first()
        if existing:
            continue
        
        # Create component definition
        component = ComponentDefinition(
            id=str(uuid4()),
            name=comp_data["name"],
            display_name=comp_data["display_name"],
            description=comp_data["description"],
            category=comp_data["category"],
            icon=comp_data["icon"],
        )
        db.add(component)
        db.commit()
        db.refresh(component)
        
        # Create version 1
        version = ComponentVersion(
            id=str(uuid4()),
            component_id=component.id,
            version_number=1,
            is_current=True,
            schema_json=json.dumps(comp_data["schema"]),
        )
        db.add(version)
        
        # Create capabilities
        for cap_data in comp_data["capabilities"]:
            capability = ComponentCapability(
                id=str(uuid4()),
                component_id=component.id,
                capability_type=cap_data["capability_type"],
                capability_config=json.dumps(cap_data["capability_config"]),
            )
            db.add(capability)
        
        db.commit()
        print(f"Seeded component '{component.name}'")


def seed_all(db: Session):
    """Run all seed functions."""
    seed_template_packs_and_templates(db)
    seed_mvp_components(db)