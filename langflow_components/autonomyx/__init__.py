"""Autonomyx Langflow components."""

from langflow_components.autonomyx.process_doc_flow_builder import ProcessDocFlowBuilder
from langflow_components.autonomyx.schemaorg_action_catalog import SchemaOrgActionCatalog
from langflow_components.autonomyx.org_sso_settings import OrgSSOSettings

COMPONENTS = {
    "ProcessDocFlowBuilder": ProcessDocFlowBuilder,
    "SchemaOrgActionCatalog": SchemaOrgActionCatalog,
    "OrgSSOSettings": OrgSSOSettings,
}

__all__ = [
    "ProcessDocFlowBuilder",
    "SchemaOrgActionCatalog",
    "OrgSSOSettings",
    "COMPONENTS",
]
