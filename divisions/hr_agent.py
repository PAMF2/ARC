"""
Human Resources Agent
Responsible for:
- Employee onboarding and offboarding
- Employee records management
- Performance tracking
- Organizational structure
- Compliance with labor regulations
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
import random
import sys
import os

try:
    from ..core.base_banking_agent import BaseBankingAgent, BankingAgentError
    from ..core.transaction_types import Transaction, AgentState, BankingAnalysis
    from ..core.config import CONFIG, DECISION_TYPES
    from ..core.employee_types import (
        Employee, EmployeeLevel, Department, JobTitle,
        EmploymentStatus, ContractType, EmployeeCredentials,
        EmployeeCompensation, EmployeePerformance, SALARY_RANGES
    )
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.base_banking_agent import BaseBankingAgent, BankingAgentError
    from core.transaction_types import Transaction, AgentState, BankingAnalysis
    from core.config import CONFIG, DECISION_TYPES
    from core.employee_types import (
        Employee, EmployeeLevel, Department, JobTitle,
        EmploymentStatus, ContractType, EmployeeCredentials,
        EmployeeCompensation, EmployeePerformance, SALARY_RANGES
    )


class HRAgent(BaseBankingAgent):
    """
    Human Resources Agent
    Manages all employee-related operations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(role="HUMAN_RESOURCES", config=config)
        self.employees: Dict[str, Employee] = {}
        self.departments: Dict[Department, List[str]] = {dept: [] for dept in Department}
        self.organization_chart: Dict[str, List[str]] = {}  # manager_id -> [employee_ids]

        self.logger.info("[HR] Human Resources Agent initialized")

    def analyze_transaction(
        self,
        transaction: Transaction,
        agent_state: AgentState,
        context: Optional[Dict[str, Any]] = None
    ) -> BankingAnalysis:
        """
        HR validates if the employee making the transaction is authorized
        and in good standing
        """
        self.logger.info(f"[HR] Validating employee authorization for tx {transaction.tx_id}")

        # Check if we can identify an employee from agent_id
        employee = self.employees.get(transaction.agent_id)

        if not employee:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=0.8,
                reasoning="Employee not found in HR database",
                alerts=["Unregistered employee attempting transaction"],
                recommended_actions=["Complete employee onboarding process"]
            )

        # Check employee status
        if employee.status != EmploymentStatus.ACTIVE:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=1.0,
                reasoning=f"Employee status is {employee.status.value}",
                alerts=[f"Inactive employee ({employee.status.value}) attempting transaction"],
                recommended_actions=["Contact HR immediately"]
            )

        # Check if employee has necessary permissions
        if employee.credentials and not employee.credentials.active:
            return self._create_analysis(
                decision=DECISION_TYPES["REJECT"],
                risk_score=0.9,
                reasoning="Employee credentials are inactive",
                alerts=["Inactive credentials used"],
                recommended_actions=["Reactivate credentials or investigate unauthorized access"]
            )

        # All OK
        return self._create_analysis(
            decision=DECISION_TYPES["APPROVE"],
            risk_score=0.0,
            reasoning=f"Employee {employee.full_name} authorized",
            metadata={
                "employee_id": employee.employee_id,
                "department": employee.department.value,
                "title": employee.display_title
            }
        )

    def execute_action(
        self,
        transaction: Transaction,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute HR actions

        Actions:
        - "hire": Hire new employee
        - "terminate": Terminate employee
        - "promote": Promote employee
        - "transfer": Transfer to another department
        - "review": Conduct performance review
        """
        context = context or {}

        if action == "hire":
            return self.hire_employee(context)
        elif action == "terminate":
            employee_id = context.get("employee_id")
            reason = context.get("reason", "Unspecified")
            return self.terminate_employee(employee_id, reason)
        elif action == "promote":
            employee_id = context.get("employee_id")
            new_title = context.get("new_title")
            new_level = context.get("new_level")
            return self.promote_employee(employee_id, new_title, new_level)
        elif action == "transfer":
            employee_id = context.get("employee_id")
            new_department = context.get("new_department")
            return self.transfer_employee(employee_id, new_department)
        elif action == "review":
            employee_id = context.get("employee_id")
            rating = context.get("rating")
            reviewer = context.get("reviewer")
            comments = context.get("comments", "")
            return self.conduct_review(employee_id, rating, reviewer, comments)
        else:
            raise BankingAgentError(f"Unknown HR action: {action}")

    def hire_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hire a new employee

        Args:
            employee_data: {
                "first_name": str,
                "last_name": str,
                "job_title": str (JobTitle enum value),
                "department": str (Department enum value),
                "level": str (EmployeeLevel enum value),
                "base_salary": float (optional),
                "manager_id": str (optional),
                "hire_date": str (optional, YYYY-MM-DD),
                "phone": str (optional),
                "address": str (optional),
                "date_of_birth": str (optional, YYYY-MM-DD),
                "location": str (optional),
                "contract_type": str (optional)
            }
        """
        try:
            # Generate IDs and email
            employee_id = Employee.generate_employee_id()
            first_name = employee_data["first_name"]
            last_name = employee_data["last_name"]
            email = Employee.generate_email(first_name, last_name)
            username = Employee.generate_username(first_name, last_name)

            # Parse enums
            job_title = JobTitle(employee_data["job_title"])
            department = Department(employee_data["department"])
            level = EmployeeLevel(employee_data["level"])
            contract_type = ContractType(employee_data.get("contract_type", "full_time"))

            # Parse dates
            hire_date_str = employee_data.get("hire_date")
            hire_date = date.fromisoformat(hire_date_str) if hire_date_str else date.today()

            dob_str = employee_data.get("date_of_birth")
            date_of_birth = date.fromisoformat(dob_str) if dob_str else None

            # Create compensation
            base_salary = employee_data.get("base_salary")
            if not base_salary:
                # Auto-assign salary based on level
                salary_range = SALARY_RANGES.get(level, (50000, 100000))
                base_salary = random.uniform(salary_range[0], salary_range[1])

            compensation = EmployeeCompensation(
                base_salary=base_salary,
                currency="USD",
                bonus_eligible=level.value not in ["trainee", "junior"],
                stock_options=100 if level.value in ["senior", "manager", "director", "vice_president", "c_level"] else 0,
                benefits=["health_insurance", "dental", "vision", "401k"],
                next_review_date=hire_date + timedelta(days=90)  # 90-day review
            )

            # Create credentials
            access_level = self._determine_access_level(level, job_title)
            permissions = self._determine_permissions(department, job_title, level)

            credentials = EmployeeCredentials(
                employee_id=employee_id,
                email=email,
                username=username,
                access_level=access_level,
                permissions=permissions,
                active=True
            )

            # Create performance tracker
            performance = EmployeePerformance(
                employee_id=employee_id,
                rating=0.0,
                reviews=[],
                goals=[{
                    "goal": "Complete onboarding training",
                    "deadline": (hire_date + timedelta(days=30)).isoformat(),
                    "status": "pending"
                }]
            )

            # Create employee
            employee = Employee(
                employee_id=employee_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                job_title=job_title,
                department=department,
                level=level,
                hire_date=hire_date,
                contract_type=contract_type,
                status=EmploymentStatus.ACTIVE,
                date_of_birth=date_of_birth,
                phone=employee_data.get("phone"),
                address=employee_data.get("address"),
                manager_id=employee_data.get("manager_id"),
                location=employee_data.get("location", "Headquarters"),
                compensation=compensation,
                credentials=credentials,
                performance=performance
            )

            # Register employee
            self.employees[employee_id] = employee
            self.departments[department].append(employee_id)

            # Update organizational chart
            if employee.manager_id:
                manager = self.employees.get(employee.manager_id)
                if manager:
                    manager.add_direct_report(employee_id)

            self.logger.info(f"[HR] ✓ Hired {employee.full_name} as {employee.display_title}")

            return {
                "success": True,
                "employee_id": employee_id,
                "employee": employee.to_dict(),
                "message": f"Successfully hired {employee.full_name}"
            }

        except Exception as e:
            self.logger.error(f"[HR] Failed to hire employee: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def terminate_employee(self, employee_id: str, reason: str = "Unspecified") -> Dict[str, Any]:
        """Terminate an employee"""
        employee = self.employees.get(employee_id)

        if not employee:
            return {"success": False, "error": "Employee not found"}

        # Update status
        employee.update_status(EmploymentStatus.TERMINATED, reason)

        # Deactivate credentials
        if employee.credentials:
            employee.credentials.active = False

        # Remove from manager's reports
        if employee.manager_id:
            manager = self.employees.get(employee.manager_id)
            if manager:
                manager.remove_direct_report(employee_id)

        # Reassign direct reports if this was a manager
        if employee.direct_reports:
            for report_id in employee.direct_reports:
                report = self.employees.get(report_id)
                if report:
                    report.manager_id = employee.manager_id  # Assign to this person's manager

        self.logger.info(f"[HR] ✗ Terminated {employee.full_name} - Reason: {reason}")

        return {
            "success": True,
            "employee_id": employee_id,
            "message": f"Terminated {employee.full_name}",
            "termination_date": datetime.now().isoformat(),
            "reason": reason
        }

    def promote_employee(
        self,
        employee_id: str,
        new_title: Optional[str] = None,
        new_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Promote an employee"""
        employee = self.employees.get(employee_id)

        if not employee:
            return {"success": False, "error": "Employee not found"}

        old_title = employee.display_title
        old_level = employee.level.value

        # Update title if provided
        if new_title:
            employee.job_title = JobTitle(new_title)

        # Update level if provided
        if new_level:
            employee.level = EmployeeLevel(new_level)

            # Adjust salary
            new_range = SALARY_RANGES.get(employee.level, (50000, 100000))
            # Give raise: new salary is 110% of current or minimum of new range, whichever is higher
            current_salary = employee.compensation.base_salary if employee.compensation else 50000
            new_salary = max(current_salary * 1.10, new_range[0])
            new_salary = min(new_salary, new_range[1])  # Cap at max of range

            if employee.compensation:
                employee.compensation.base_salary = new_salary
                employee.compensation.last_raise_date = date.today()

            # Update access level
            if employee.credentials:
                employee.credentials.access_level = self._determine_access_level(employee.level, employee.job_title)

        employee.add_note(f"Promoted from {old_title} ({old_level}) to {employee.display_title} ({employee.level.value})")

        self.logger.info(f"[HR] ↑ Promoted {employee.full_name} to {employee.display_title}")

        return {
            "success": True,
            "employee_id": employee_id,
            "old_title": old_title,
            "new_title": employee.display_title,
            "new_salary": employee.compensation.base_salary if employee.compensation else None,
            "message": f"Promoted {employee.full_name} to {employee.display_title}"
        }

    def transfer_employee(self, employee_id: str, new_department: str) -> Dict[str, Any]:
        """Transfer employee to another department"""
        employee = self.employees.get(employee_id)

        if not employee:
            return {"success": False, "error": "Employee not found"}

        old_department = employee.department

        # Remove from old department
        if employee_id in self.departments[old_department]:
            self.departments[old_department].remove(employee_id)

        # Add to new department
        new_dept = Department(new_department)
        employee.department = new_dept
        self.departments[new_dept].append(employee_id)

        employee.add_note(f"Transferred from {old_department.value} to {new_dept.value}")

        self.logger.info(f"[HR] → Transferred {employee.full_name} to {new_dept.value}")

        return {
            "success": True,
            "employee_id": employee_id,
            "old_department": old_department.value,
            "new_department": new_dept.value,
            "message": f"Transferred {employee.full_name} to {new_dept.value}"
        }

    def conduct_review(
        self,
        employee_id: str,
        rating: float,
        reviewer: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Conduct performance review"""
        employee = self.employees.get(employee_id)

        if not employee:
            return {"success": False, "error": "Employee not found"}

        if not employee.performance:
            employee.performance = EmployeePerformance(employee_id=employee_id)

        employee.performance.add_review(rating, reviewer, comments)
        employee.add_note(f"Performance review: {rating}/5.0 by {reviewer}")

        # Schedule next review
        if employee.compensation:
            employee.compensation.next_review_date = date.today() + timedelta(days=180)  # 6 months

        self.logger.info(f"[HR] ★ Review completed for {employee.full_name}: {rating}/5.0")

        return {
            "success": True,
            "employee_id": employee_id,
            "rating": rating,
            "average_rating": employee.performance.rating,
            "message": f"Review completed for {employee.full_name}"
        }

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        return self.employees.get(employee_id)

    def get_department_employees(self, department: Department) -> List[Employee]:
        """Get all employees in a department"""
        employee_ids = self.departments.get(department, [])
        return [self.employees[eid] for eid in employee_ids if eid in self.employees]

    def get_employees_by_manager(self, manager_id: str) -> List[Employee]:
        """Get all direct reports of a manager"""
        manager = self.employees.get(manager_id)
        if not manager:
            return []

        return [
            self.employees[eid]
            for eid in manager.direct_reports
            if eid in self.employees
        ]

    def get_all_employees(self, status: Optional[EmploymentStatus] = None) -> List[Employee]:
        """Get all employees, optionally filtered by status"""
        employees = list(self.employees.values())

        if status:
            employees = [e for e in employees if e.status == status]

        return employees

    def get_organization_summary(self) -> Dict[str, Any]:
        """Get organizational summary"""
        total_employees = len(self.employees)
        active_employees = sum(1 for e in self.employees.values() if e.status == EmploymentStatus.ACTIVE)

        department_counts = {
            dept.value: len(emp_ids)
            for dept, emp_ids in self.departments.items()
            if len(emp_ids) > 0
        }

        level_counts = {}
        for employee in self.employees.values():
            level = employee.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "departments": department_counts,
            "levels": level_counts,
            "average_tenure": sum(e.years_of_service for e in self.employees.values()) / max(total_employees, 1)
        }

    def _determine_access_level(self, level: EmployeeLevel, job_title: JobTitle) -> int:
        """Determine access level based on position"""
        access_map = {
            EmployeeLevel.C_LEVEL: 10,
            EmployeeLevel.VP: 9,
            EmployeeLevel.DIRECTOR: 8,
            EmployeeLevel.MANAGER: 7,
            EmployeeLevel.COORDINATOR: 6,
            EmployeeLevel.SENIOR: 5,
            EmployeeLevel.SPECIALIST: 5,
            EmployeeLevel.PLENO: 3,
            EmployeeLevel.JUNIOR: 2,
            EmployeeLevel.TRAINEE: 1
        }
        return access_map.get(level, 1)

    def _determine_permissions(
        self,
        department: Department,
        job_title: JobTitle,
        level: EmployeeLevel
    ) -> List[str]:
        """Determine permissions based on role"""
        permissions = ["read_own_data"]

        # Department-specific permissions
        dept_permissions = {
            Department.RISK_MANAGEMENT: ["view_risk_reports", "assess_risk"],
            Department.COMPLIANCE: ["view_compliance_reports", "audit_transactions"],
            Department.TREASURY: ["view_treasury_data", "manage_liquidity"],
            Department.OPERATIONS: ["process_transactions", "view_operations"],
            Department.HR: ["view_employee_data", "manage_employees"],
            Department.IT: ["system_admin", "technical_support"]
        }

        permissions.extend(dept_permissions.get(department, []))

        # Level-based permissions
        if level.value in ["manager", "director", "vice_president", "c_level"]:
            permissions.extend(["approve_transactions", "view_reports", "manage_team"])

        if level.value in ["director", "vice_president", "c_level"]:
            permissions.extend(["strategic_decisions", "view_all_departments"])

        if level.value == "c_level":
            permissions.append("full_access")

        return list(set(permissions))  # Remove duplicates
