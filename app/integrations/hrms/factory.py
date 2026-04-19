"""
HRMS Factory - Creates HRMS adapter based on configuration
Supports: Workday, BambooHR, SAP SuccessFactors, Oracle HCM, ADP, UKG, etc.
"""
import os
from typing import Optional, List
from app.integrations.hrms.base import BaseHRMSAdapter, HREmployee, HRDepartment, HRPolicy


def get_hrms_adapter(provider: Optional[str] = None) -> BaseHRMSAdapter:
    """
    Factory to create HRMS adapter based on environment configuration.
    
    Set HRMS_PROVIDER env var to specify provider:
    - workday
    - bamboohr
    - sap_successfactors
    - oracle_hcm
    - adp
    - ukg
    - bamboo_hr (alias)
    - custom (requires HRMS_API_URL)
    """
    provider = provider or os.environ.get("HRMS_PROVIDER", "custom").lower()
    
    if provider == "workday":
        from app.integrations.hrms.workday import WorkdayHRMSAdapter
        return WorkdayHRMSAdapter()
    elif provider in ("bamboohr", "bamboo_hr"):
        from app.integrations.hrms.bamboohr import BambooHRAdapter
        return BambooHRAdapter()
    elif provider == "sap_successfactors":
        from app.integrations.hrms.sap import SAPSuccessFactorsAdapter
        return SAPSuccessFactorsAdapter()
    elif provider == "oracle_hcm":
        from app.integrations.hrms.oracle import OracleHCMAdapter
        return OracleHCMAdapter()
    elif provider == "adp":
        from app.integrations.hrms.adp import ADPAdapter
        return ADPAdapter()
    elif provider == "ukg":
        from app.integrations.hrms.ukg import UKGAdapter
        return UKGAdapter()
    else:
        # Custom HRMS - requires API URL configuration
        from app.integrations.hrms.custom import CustomHRMSAdapter
        return CustomHRMSAdapter()


__all__ = [
    "get_hrms_adapter",
    "BaseHRMSAdapter",
    "HREmployee",
    "HRDepartment", 
    "HRPolicy",
]