"""
Real Bank Organizational Structure
Based on research of actual commercial bank structures in 2026

Sources:
- https://theorgchart.com/bank-organizational-chart/
- https://opsdog.com/categories/organization-charts/banking
- https://vault.com/industries/commercial-banking/structure

Structure:
Board of Directors
├── CEO (Chief Executive Officer)
    ├── CFO (Chief Financial Officer)
    │   ├── Treasury & Financial Markets
    │   ├── Finance & Accounting
    │   ├── Investor Relations
    │   └── Strategic Planning
    ├── COO (Chief Operating Officer)
    │   ├── Operations
    │   ├── Clearing & Settlement
    │   ├── Business Process Management
    │   └── Facilities
    ├── CRO (Chief Risk Officer)
    │   ├── Risk Management
    │   ├── Compliance & Legal
    │   ├── Internal Audit
    │   └── Fraud Prevention
    ├── CTO/CIO (Chief Technology Officer)
    │   ├── Information Technology
    │   ├── Digital Banking
    │   ├── Cybersecurity
    │   └── Data & Analytics
    ├── Chief Banking Officer
    │   ├── Retail Banking (LOB)
    │   ├── Commercial Banking (LOB)
    │   ├── Private Banking (LOB)
    │   └── Small Business Banking
    ├── Chief Investment Officer
    │   ├── Investment Banking (LOB)
    │   ├── Wealth Management
    │   ├── Asset Management
    │   └── Trading
    ├── Chief Credit Officer
    │   ├── Mortgage Lending
    │   ├── Consumer Lending
    │   ├── Commercial Lending
    │   └── Credit Cards
    └── CHRO (Chief Human Resources Officer)
        ├── Talent Acquisition
        ├── Learning & Development
        ├── Compensation & Benefits
        └── Employee Relations
"""
import sys
import os
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.employee_types import Department, JobTitle, EmployeeLevel
from employees.employee_factory import EmployeeFactory
from divisions.hr_agent import HRAgent


class RealBankOrganizationalStructure:
    """Creates a realistic bank organizational structure"""

    # C-Suite reporting to CEO
    C_SUITE = {
        JobTitle.CEO: None,  # Reports to Board
        JobTitle.CFO: JobTitle.CEO,
        JobTitle.COO: JobTitle.CEO,
        JobTitle.CRO: JobTitle.CEO,
        JobTitle.CTO: JobTitle.CEO,
    }

    # Lines of Business (LOBs) - Revenue generating
    LINES_OF_BUSINESS = {
        Department.RETAIL_BANKING: {
            "name": "Retail Banking",
            "reports_to": "Chief Banking Officer",
            "teams": {
                JobTitle.BRANCH_MANAGER: 3,  # 3 branch managers
                JobTitle.TELLER: 12,  # 4 per branch
                JobTitle.CUSTOMER_SERVICE_REP: 9,  # 3 per branch
                JobTitle.PERSONAL_BANKER: 6,  # 2 per branch
                JobTitle.LOAN_OFFICER: 6,  # 2 per branch
            }
        },
        Department.PRIVATE_BANKING: {
            "name": "Private Banking & Wealth Management",
            "reports_to": "Chief Banking Officer",
            "teams": {
                JobTitle.DEPARTMENT_MANAGER: 1,
                JobTitle.PRIVATE_BANKER: 4,
                JobTitle.WEALTH_MANAGER: 3,
                JobTitle.INVESTMENT_ADVISOR: 3,
                JobTitle.RELATIONSHIP_MANAGER: 2,
            }
        },
        Department.CORPORATE_BANKING: {
            "name": "Commercial Banking",
            "reports_to": "Chief Banking Officer",
            "teams": {
                JobTitle.DEPARTMENT_MANAGER: 1,
                JobTitle.RELATIONSHIP_MANAGER: 4,
                JobTitle.CREDIT_ANALYST: 3,
                JobTitle.LOAN_OFFICER: 3,
                JobTitle.UNDERWRITER: 2,
            }
        },
        Department.INVESTMENT_BANKING: {
            "name": "Investment Banking",
            "reports_to": "Chief Investment Officer",
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.PORTFOLIO_MANAGER: 2,
                JobTitle.FINANCIAL_PLANNER: 2,
                JobTitle.INVESTMENT_ADVISOR: 2,
            }
        },
        Department.TRADING: {
            "name": "Trading & Capital Markets",
            "reports_to": "Chief Investment Officer",
            "teams": {
                JobTitle.DEPARTMENT_MANAGER: 1,
                JobTitle.TRADER: 3,
                JobTitle.QUANT_ANALYST: 2,
            }
        }
    }

    # Support/Middle Office - Risk, compliance, control
    MIDDLE_OFFICE = {
        Department.RISK_MANAGEMENT: {
            "name": "Risk Management",
            "reports_to": JobTitle.CRO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.RISK_ANALYST: 4,
                JobTitle.CREDIT_ANALYST: 2,
            }
        },
        Department.COMPLIANCE: {
            "name": "Compliance & Legal",
            "reports_to": JobTitle.CRO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.COMPLIANCE_OFFICER: 3,
                JobTitle.AML_SPECIALIST: 2,
                JobTitle.FRAUD_ANALYST: 2,
            }
        },
        Department.TREASURY: {
            "name": "Treasury & Financial Markets",
            "reports_to": JobTitle.CFO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.TREASURY_ANALYST: 3,
            }
        },
        Department.FINANCE: {
            "name": "Finance & Accounting",
            "reports_to": JobTitle.CFO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.OPERATIONS_ANALYST: 4,  # Finance analysts
            }
        }
    }

    # Back Office - Processing, settlement, technology
    BACK_OFFICE = {
        Department.OPERATIONS: {
            "name": "Operations",
            "reports_to": JobTitle.COO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.DEPARTMENT_MANAGER: 2,
                JobTitle.OPERATIONS_ANALYST: 6,
            }
        },
        Department.CLEARING_SETTLEMENT: {
            "name": "Clearing & Settlement",
            "reports_to": JobTitle.COO,
            "teams": {
                JobTitle.DEPARTMENT_MANAGER: 1,
                JobTitle.SETTLEMENT_OFFICER: 3,
                JobTitle.RECONCILIATION_SPECIALIST: 3,
            }
        },
        Department.IT: {
            "name": "Information Technology",
            "reports_to": JobTitle.CTO,
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.DEPARTMENT_MANAGER: 2,
                JobTitle.SOFTWARE_ENGINEER: 8,
                JobTitle.DATA_ANALYST: 3,
                JobTitle.CYBERSECURITY_SPECIALIST: 3,
                JobTitle.DEVOPS_ENGINEER: 2,
            }
        },
        Department.HR: {
            "name": "Human Resources",
            "reports_to": "CHRO",
            "teams": {
                JobTitle.DIRECTOR: 1,
                JobTitle.DEPARTMENT_MANAGER: 1,
                JobTitle.CUSTOMER_SERVICE_REP: 3,  # HR specialists
            }
        }
    }

    @classmethod
    def create_complete_bank_organization(
        cls,
        hr_agent: HRAgent,
        bank_name: str = "GlobalBank"
    ) -> Dict[str, Any]:
        """
        Create a complete, realistic bank organization

        Returns:
            Dictionary with all employee IDs organized by role
        """
        print("\n" + "=" * 80)
        print(f"CREATING {bank_name.upper()} - REALISTIC BANK STRUCTURE")
        print("=" * 80)
        print("\nBased on research of actual commercial bank structures")
        print("Sources: theorgchart.com, opsdog.com, vault.com")
        print("=" * 80)

        organization = {
            "bank_name": bank_name,
            "c_suite": {},
            "senior_leadership": {},
            "lines_of_business": {},
            "middle_office": {},
            "back_office": {},
            "all_employees": []
        }

        # Phase 1: Create C-Suite
        print("\n[PHASE 1] Creating C-Suite Executive Team")
        print("-" * 80)

        c_suite_roles = [
            (JobTitle.CEO, Department.OPERATIONS, EmployeeLevel.C_LEVEL, None),
            (JobTitle.CFO, Department.FINANCE, EmployeeLevel.C_LEVEL, "CEO"),
            (JobTitle.COO, Department.OPERATIONS, EmployeeLevel.C_LEVEL, "CEO"),
            (JobTitle.CRO, Department.RISK_MANAGEMENT, EmployeeLevel.C_LEVEL, "CEO"),
            (JobTitle.CTO, Department.IT, EmployeeLevel.C_LEVEL, "CEO"),
        ]

        ceo_id = None
        for job_title, department, level, reports_to in c_suite_roles:
            manager_id = None
            if reports_to == "CEO" and ceo_id:
                manager_id = ceo_id

            employee_data = EmployeeFactory.create_employee_data(
                job_title=job_title,
                department=department,
                level=level,
                manager_id=manager_id,
                location="Headquarters"
            )

            result = hr_agent.hire_employee(employee_data)
            if result["success"]:
                emp_id = result["employee_id"]
                organization["c_suite"][job_title.value] = emp_id
                organization["all_employees"].append(emp_id)

                if job_title == JobTitle.CEO:
                    ceo_id = emp_id

                print(f"  [OK] {result['employee']['full_name']} - {job_title.value.upper()}")

        # Phase 2: Create Senior Leadership (VPs & Directors under C-Suite)
        print("\n[PHASE 2] Creating Senior Leadership Team")
        print("-" * 80)

        senior_roles = [
            # Under CFO
            (JobTitle.VP, Department.FINANCE, "CFO", "VP Finance"),
            (JobTitle.DIRECTOR, Department.TREASURY, "CFO", "Director Treasury"),
            # Under COO
            (JobTitle.VP, Department.OPERATIONS, "COO", "VP Operations"),
            # Under CRO
            (JobTitle.DIRECTOR, Department.COMPLIANCE, "CRO", "Director Compliance"),
            # Under CTO
            (JobTitle.VP, Department.IT, "CTO", "VP Technology"),
            # Business heads
            (JobTitle.SVP, Department.RETAIL_BANKING, "CEO", "Chief Banking Officer"),
            (JobTitle.SVP, Department.INVESTMENT_BANKING, "CEO", "Chief Investment Officer"),
            (JobTitle.VP, Department.CORPORATE_BANKING, "CEO", "Chief Credit Officer"),
        ]

        for job_title, department, reports_to, role_name in senior_roles:
            manager_id = organization["c_suite"].get(reports_to.lower())

            employee_data = EmployeeFactory.create_employee_data(
                job_title=job_title,
                department=department,
                level=EmployeeLevel.VP if "VP" in job_title.value else EmployeeLevel.DIRECTOR,
                manager_id=manager_id,
                location="Headquarters"
            )

            result = hr_agent.hire_employee(employee_data)
            if result["success"]:
                emp_id = result["employee_id"]
                organization["senior_leadership"][role_name] = emp_id
                organization["all_employees"].append(emp_id)
                print(f"  [OK] {result['employee']['full_name']} - {role_name}")

        # Phase 3: Create Lines of Business (Revenue-generating)
        print("\n[PHASE 3] Creating Lines of Business")
        print("-" * 80)

        for dept, config in cls.LINES_OF_BUSINESS.items():
            print(f"\n  Creating {config['name']}...")

            dept_employees = []

            # Find appropriate senior leader
            reports_to_id = organization["senior_leadership"].get(config["reports_to"])
            if not reports_to_id:
                reports_to_id = ceo_id

            # Create teams
            for job_title, count in config["teams"].items():
                for i in range(count):
                    level = cls._determine_level(job_title)

                    employee_data = EmployeeFactory.create_employee_data(
                        job_title=job_title,
                        department=dept,
                        level=level,
                        manager_id=reports_to_id if level in [EmployeeLevel.DIRECTOR, EmployeeLevel.MANAGER] else None,
                        location="Headquarters" if level in [EmployeeLevel.DIRECTOR, EmployeeLevel.MANAGER] else "Branch"
                    )

                    result = hr_agent.hire_employee(employee_data)
                    if result["success"]:
                        emp_id = result["employee_id"]
                        dept_employees.append(emp_id)
                        organization["all_employees"].append(emp_id)

            organization["lines_of_business"][config["name"]] = dept_employees
            print(f"    [OK] Created {len(dept_employees)} employees")

        # Phase 4: Create Middle Office
        print("\n[PHASE 4] Creating Middle Office (Risk, Compliance, Treasury)")
        print("-" * 80)

        for dept, config in cls.MIDDLE_OFFICE.items():
            print(f"\n  Creating {config['name']}...")

            dept_employees = []

            # Find C-Suite manager
            reports_to_title = config["reports_to"]
            reports_to_id = organization["c_suite"].get(reports_to_title.value.lower())

            for job_title, count in config["teams"].items():
                for i in range(count):
                    level = cls._determine_level(job_title)

                    employee_data = EmployeeFactory.create_employee_data(
                        job_title=job_title,
                        department=dept,
                        level=level,
                        manager_id=reports_to_id if level == EmployeeLevel.DIRECTOR else None,
                        location="Headquarters"
                    )

                    result = hr_agent.hire_employee(employee_data)
                    if result["success"]:
                        emp_id = result["employee_id"]
                        dept_employees.append(emp_id)
                        organization["all_employees"].append(emp_id)

            organization["middle_office"][config["name"]] = dept_employees
            print(f"    [OK] Created {len(dept_employees)} employees")

        # Phase 5: Create Back Office
        print("\n[PHASE 5] Creating Back Office (Operations, IT, Support)")
        print("-" * 80)

        for dept, config in cls.BACK_OFFICE.items():
            print(f"\n  Creating {config['name']}...")

            dept_employees = []

            # Find appropriate manager
            if isinstance(config["reports_to"], JobTitle):
                reports_to_id = organization["c_suite"].get(config["reports_to"].value.lower())
            else:
                reports_to_id = ceo_id  # CHRO reports to CEO

            for job_title, count in config["teams"].items():
                for i in range(count):
                    level = cls._determine_level(job_title)

                    employee_data = EmployeeFactory.create_employee_data(
                        job_title=job_title,
                        department=dept,
                        level=level,
                        manager_id=reports_to_id if level in [EmployeeLevel.DIRECTOR, EmployeeLevel.MANAGER] else None,
                        location="Headquarters"
                    )

                    result = hr_agent.hire_employee(employee_data)
                    if result["success"]:
                        emp_id = result["employee_id"]
                        dept_employees.append(emp_id)
                        organization["all_employees"].append(emp_id)

            organization["back_office"][config["name"]] = dept_employees
            print(f"    [OK] Created {len(dept_employees)} employees")

        # Summary
        print("\n" + "=" * 80)
        print("ORGANIZATION CREATION COMPLETE")
        print("=" * 80)
        print(f"Bank Name: {bank_name}")
        print(f"Total Employees: {len(organization['all_employees'])}")
        print(f"  - C-Suite: {len(organization['c_suite'])}")
        print(f"  - Senior Leadership: {len(organization['senior_leadership'])}")
        print(f"  - Lines of Business: {sum(len(v) for v in organization['lines_of_business'].values())}")
        print(f"  - Middle Office: {sum(len(v) for v in organization['middle_office'].values())}")
        print(f"  - Back Office: {sum(len(v) for v in organization['back_office'].values())}")
        print("=" * 80)

        return organization

    @staticmethod
    def _determine_level(job_title: JobTitle) -> EmployeeLevel:
        """Determine employee level from job title"""
        level_map = {
            JobTitle.CEO: EmployeeLevel.C_LEVEL,
            JobTitle.CFO: EmployeeLevel.C_LEVEL,
            JobTitle.CRO: EmployeeLevel.C_LEVEL,
            JobTitle.CTO: EmployeeLevel.C_LEVEL,
            JobTitle.COO: EmployeeLevel.C_LEVEL,
            JobTitle.VP: EmployeeLevel.VP,
            JobTitle.SVP: EmployeeLevel.VP,
            JobTitle.DIRECTOR: EmployeeLevel.DIRECTOR,
            JobTitle.BRANCH_MANAGER: EmployeeLevel.MANAGER,
            JobTitle.DEPARTMENT_MANAGER: EmployeeLevel.MANAGER,
            JobTitle.REGIONAL_MANAGER: EmployeeLevel.MANAGER,
            JobTitle.WEALTH_MANAGER: EmployeeLevel.SENIOR,
            JobTitle.PORTFOLIO_MANAGER: EmployeeLevel.SENIOR,
            JobTitle.PRIVATE_BANKER: EmployeeLevel.SENIOR,
            JobTitle.RELATIONSHIP_MANAGER: EmployeeLevel.SENIOR,
            JobTitle.TRADER: EmployeeLevel.SENIOR,
            JobTitle.CYBERSECURITY_SPECIALIST: EmployeeLevel.SPECIALIST,
            JobTitle.AML_SPECIALIST: EmployeeLevel.SPECIALIST,
            JobTitle.QUANT_ANALYST: EmployeeLevel.SPECIALIST,
            JobTitle.SOFTWARE_ENGINEER: EmployeeLevel.PLENO,
            JobTitle.CREDIT_ANALYST: EmployeeLevel.PLENO,
            JobTitle.RISK_ANALYST: EmployeeLevel.PLENO,
            JobTitle.TREASURY_ANALYST: EmployeeLevel.PLENO,
            JobTitle.OPERATIONS_ANALYST: EmployeeLevel.PLENO,
            JobTitle.DATA_ANALYST: EmployeeLevel.PLENO,
            JobTitle.COMPLIANCE_OFFICER: EmployeeLevel.PLENO,
            JobTitle.FRAUD_ANALYST: EmployeeLevel.PLENO,
            JobTitle.SETTLEMENT_OFFICER: EmployeeLevel.PLENO,
            JobTitle.RECONCILIATION_SPECIALIST: EmployeeLevel.PLENO,
            JobTitle.DEVOPS_ENGINEER: EmployeeLevel.PLENO,
            JobTitle.UNDERWRITER: EmployeeLevel.PLENO,
            JobTitle.FINANCIAL_PLANNER: EmployeeLevel.PLENO,
            JobTitle.INVESTMENT_ADVISOR: EmployeeLevel.PLENO,
            JobTitle.LOAN_OFFICER: EmployeeLevel.JUNIOR,
            JobTitle.PERSONAL_BANKER: EmployeeLevel.JUNIOR,
            JobTitle.CUSTOMER_SERVICE_REP: EmployeeLevel.JUNIOR,
            JobTitle.TELLER: EmployeeLevel.JUNIOR,
        }

        return level_map.get(job_title, EmployeeLevel.PLENO)
