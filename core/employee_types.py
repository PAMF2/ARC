"""
Employee Types and Models
Sistema completo de gestão de funcionários bancários
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from enum import Enum
import uuid


class EmployeeLevel(Enum):
    """Níveis hierárquicos dos funcionários"""
    TRAINEE = "trainee"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vice_president"
    C_LEVEL = "c_level"


class Department(Enum):
    """Departamentos do banco"""
    # Front Office
    RETAIL_BANKING = "retail_banking"
    PRIVATE_BANKING = "private_banking"
    CORPORATE_BANKING = "corporate_banking"
    INVESTMENT_BANKING = "investment_banking"

    # Middle Office
    RISK_MANAGEMENT = "risk_management"
    COMPLIANCE = "compliance"
    TREASURY = "treasury"
    TRADING = "trading"

    # Back Office
    OPERATIONS = "operations"
    CLEARING_SETTLEMENT = "clearing_settlement"
    IT = "information_technology"
    FINANCE = "finance"

    # Support
    HR = "human_resources"
    LEGAL = "legal"
    MARKETING = "marketing"
    FACILITIES = "facilities"


class JobTitle(Enum):
    """Cargos disponíveis no banco"""
    # Front Office - Atendimento
    TELLER = "teller"
    CUSTOMER_SERVICE_REP = "customer_service_representative"
    PERSONAL_BANKER = "personal_banker"
    RELATIONSHIP_MANAGER = "relationship_manager"
    PRIVATE_BANKER = "private_banker"

    # Front Office - Consultoria
    INVESTMENT_ADVISOR = "investment_advisor"
    WEALTH_MANAGER = "wealth_manager"
    FINANCIAL_PLANNER = "financial_planner"

    # Crédito
    LOAN_OFFICER = "loan_officer"
    CREDIT_ANALYST = "credit_analyst"
    UNDERWRITER = "underwriter"

    # Risk & Compliance
    RISK_ANALYST = "risk_analyst"
    COMPLIANCE_OFFICER = "compliance_officer"
    AML_SPECIALIST = "aml_specialist"
    FRAUD_ANALYST = "fraud_analyst"

    # Treasury & Trading
    TRADER = "trader"
    TREASURY_ANALYST = "treasury_analyst"
    PORTFOLIO_MANAGER = "portfolio_manager"
    QUANT_ANALYST = "quantitative_analyst"

    # Operations
    OPERATIONS_ANALYST = "operations_analyst"
    SETTLEMENT_OFFICER = "settlement_officer"
    RECONCILIATION_SPECIALIST = "reconciliation_specialist"

    # IT & Tech
    SOFTWARE_ENGINEER = "software_engineer"
    DATA_ANALYST = "data_analyst"
    CYBERSECURITY_SPECIALIST = "cybersecurity_specialist"
    DEVOPS_ENGINEER = "devops_engineer"

    # Management
    BRANCH_MANAGER = "branch_manager"
    DEPARTMENT_MANAGER = "department_manager"
    REGIONAL_MANAGER = "regional_manager"

    # Executive
    DIRECTOR = "director"
    VP = "vice_president"
    SVP = "senior_vice_president"
    CFO = "chief_financial_officer"
    CRO = "chief_risk_officer"
    CTO = "chief_technology_officer"
    COO = "chief_operating_officer"
    CEO = "chief_executive_officer"


class EmploymentStatus(Enum):
    """Status de emprego"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    RETIRED = "retired"


class ContractType(Enum):
    """Tipos de contrato"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


@dataclass
class EmployeeCredentials:
    """Credenciais de acesso do funcionário"""
    employee_id: str
    email: str
    username: str
    access_level: int = 1  # 1-10
    permissions: List[str] = field(default_factory=list)
    active: bool = True
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "email": self.email,
            "username": self.username,
            "access_level": self.access_level,
            "permissions": self.permissions,
            "active": self.active,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


@dataclass
class EmployeeCompensation:
    """Compensação e benefícios"""
    base_salary: float
    currency: str = "USD"
    bonus_eligible: bool = True
    stock_options: int = 0
    benefits: List[str] = field(default_factory=list)
    last_raise_date: Optional[date] = None
    next_review_date: Optional[date] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_salary": self.base_salary,
            "currency": self.currency,
            "bonus_eligible": self.bonus_eligible,
            "stock_options": self.stock_options,
            "benefits": self.benefits,
            "last_raise_date": self.last_raise_date.isoformat() if self.last_raise_date else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None
        }


@dataclass
class EmployeePerformance:
    """Avaliação de performance"""
    employee_id: str
    rating: float = 0.0  # 0-5
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    goals: List[Dict[str, Any]] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def add_review(self, rating: float, reviewer: str, comments: str):
        """Adiciona uma avaliação"""
        self.reviews.append({
            "date": datetime.now().isoformat(),
            "rating": rating,
            "reviewer": reviewer,
            "comments": comments
        })
        # Atualiza rating médio
        if self.reviews:
            self.rating = sum(r["rating"] for r in self.reviews) / len(self.reviews)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "rating": self.rating,
            "reviews": self.reviews,
            "goals": self.goals,
            "achievements": self.achievements,
            "warnings": self.warnings
        }


@dataclass
class Employee:
    """
    Modelo completo de funcionário bancário
    """
    # Identificação
    employee_id: str
    first_name: str
    last_name: str
    email: str

    # Posição
    job_title: JobTitle
    department: Department
    level: EmployeeLevel

    # Emprego
    hire_date: date
    contract_type: ContractType = ContractType.FULL_TIME
    status: EmploymentStatus = EmploymentStatus.ACTIVE

    # Dados pessoais
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None

    # Hierarquia
    manager_id: Optional[str] = None
    direct_reports: List[str] = field(default_factory=list)

    # Local de trabalho
    branch_id: Optional[str] = None
    location: str = "Headquarters"
    office_number: Optional[str] = None

    # Compensação
    compensation: Optional[EmployeeCompensation] = None

    # Credenciais
    credentials: Optional[EmployeeCredentials] = None

    # Performance
    performance: Optional[EmployeePerformance] = None

    # Metadados
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Nome completo"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_title(self) -> str:
        """Título formatado para exibição"""
        level_prefix = ""
        if self.level in [EmployeeLevel.JUNIOR, EmployeeLevel.SENIOR]:
            level_prefix = f"{self.level.value.title()} "

        return f"{level_prefix}{self.job_title.value.replace('_', ' ').title()}"

    @property
    def is_manager(self) -> bool:
        """Verifica se é gerente"""
        return len(self.direct_reports) > 0 or self.level.value in ["manager", "director", "vice_president", "c_level"]

    @property
    def years_of_service(self) -> float:
        """Anos de serviço"""
        delta = datetime.now().date() - self.hire_date
        return round(delta.days / 365.25, 1)

    def add_direct_report(self, employee_id: str):
        """Adiciona subordinado direto"""
        if employee_id not in self.direct_reports:
            self.direct_reports.append(employee_id)
            self.updated_at = datetime.now()

    def remove_direct_report(self, employee_id: str):
        """Remove subordinado direto"""
        if employee_id in self.direct_reports:
            self.direct_reports.remove(employee_id)
            self.updated_at = datetime.now()

    def update_status(self, new_status: EmploymentStatus, reason: Optional[str] = None):
        """Atualiza status de emprego"""
        self.status = new_status
        self.updated_at = datetime.now()
        if reason:
            self.notes.append(f"[{datetime.now().isoformat()}] Status changed to {new_status.value}: {reason}")

    def add_note(self, note: str):
        """Adiciona nota ao histórico"""
        self.notes.append(f"[{datetime.now().isoformat()}] {note}")
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "employee_id": self.employee_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "job_title": self.job_title.value,
            "display_title": self.display_title,
            "department": self.department.value,
            "level": self.level.value,
            "hire_date": self.hire_date.isoformat(),
            "contract_type": self.contract_type.value,
            "status": self.status.value,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "phone": self.phone,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "manager_id": self.manager_id,
            "direct_reports": self.direct_reports,
            "is_manager": self.is_manager,
            "branch_id": self.branch_id,
            "location": self.location,
            "office_number": self.office_number,
            "years_of_service": self.years_of_service,
            "compensation": self.compensation.to_dict() if self.compensation else None,
            "credentials": self.credentials.to_dict() if self.credentials else None,
            "performance": self.performance.to_dict() if self.performance else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "notes": self.notes,
            "tags": self.tags
        }

    @staticmethod
    def generate_employee_id() -> str:
        """Gera ID único de funcionário"""
        return f"EMP-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def generate_email(first_name: str, last_name: str, domain: str = "globalbank.com") -> str:
        """Gera email corporativo"""
        return f"{first_name.lower()}.{last_name.lower()}@{domain}"

    @staticmethod
    def generate_username(first_name: str, last_name: str) -> str:
        """Gera username"""
        return f"{first_name.lower()}.{last_name.lower()}"


# Estrutura organizacional padrão
ORGANIZATIONAL_HIERARCHY = {
    "C_LEVEL": {
        "level": 10,
        "typical_titles": [JobTitle.CEO, JobTitle.CFO, JobTitle.CRO, JobTitle.CTO, JobTitle.COO],
        "reports_to": None
    },
    "VP": {
        "level": 9,
        "typical_titles": [JobTitle.VP, JobTitle.SVP],
        "reports_to": "C_LEVEL"
    },
    "DIRECTOR": {
        "level": 8,
        "typical_titles": [JobTitle.DIRECTOR],
        "reports_to": "VP"
    },
    "MANAGER": {
        "level": 6,
        "typical_titles": [JobTitle.BRANCH_MANAGER, JobTitle.DEPARTMENT_MANAGER, JobTitle.REGIONAL_MANAGER],
        "reports_to": "DIRECTOR"
    },
    "SENIOR": {
        "level": 5,
        "typical_titles": [JobTitle.WEALTH_MANAGER, JobTitle.PORTFOLIO_MANAGER],
        "reports_to": "MANAGER"
    },
    "PLENO": {
        "level": 3,
        "typical_titles": [JobTitle.RELATIONSHIP_MANAGER, JobTitle.CREDIT_ANALYST],
        "reports_to": "SENIOR"
    },
    "JUNIOR": {
        "level": 2,
        "typical_titles": [JobTitle.TELLER, JobTitle.OPERATIONS_ANALYST],
        "reports_to": "PLENO"
    }
}


# Salários base por nível (USD anual)
SALARY_RANGES = {
    EmployeeLevel.TRAINEE: (35_000, 45_000),
    EmployeeLevel.JUNIOR: (45_000, 65_000),
    EmployeeLevel.PLENO: (65_000, 95_000),
    EmployeeLevel.SENIOR: (95_000, 140_000),
    EmployeeLevel.SPECIALIST: (100_000, 150_000),
    EmployeeLevel.COORDINATOR: (90_000, 130_000),
    EmployeeLevel.MANAGER: (120_000, 180_000),
    EmployeeLevel.DIRECTOR: (180_000, 280_000),
    EmployeeLevel.VP: (280_000, 450_000),
    EmployeeLevel.C_LEVEL: (450_000, 1_500_000),
}
