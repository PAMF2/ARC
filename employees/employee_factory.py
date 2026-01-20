"""
Employee Factory
Utilities para criar múltiplos funcionários com dados realistas
"""
import random
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

try:
    from ..core.employee_types import (
        Employee, EmployeeLevel, Department, JobTitle,
        ContractType, EmploymentStatus
    )
    from ..divisions.hr_agent import HRAgent
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.employee_types import (
        Employee, EmployeeLevel, Department, JobTitle,
        ContractType, EmploymentStatus
    )
    from divisions.hr_agent import HRAgent


# Listas de nomes realistas
FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy",
    "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob", "Nicholas", "Eric",
    "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
    "Samuel", "Raymond", "Gregory", "Alexander", "Patrick", "Frank", "Dennis",
    "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Douglas", "Henry"
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy",
    "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia",
    "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma",
    "Nicole", "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel",
    "Carolyn", "Janet", "Catherine", "Maria", "Heather", "Diane", "Ruth", "Julie"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson"
]

# Endereços de exemplo
CITIES = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
    "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA",
    "Austin, TX", "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "San Francisco, CA",
    "Charlotte, NC", "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Boston, MA",
    "Washington, DC", "Nashville, TN", "Detroit, MI", "Portland, OR", "Las Vegas, NV"
]

STREETS = [
    "Main St", "Oak Ave", "Park Blvd", "Maple Dr", "Cedar Ln", "Washington St",
    "Lake Rd", "Hill St", "Pine Ave", "Elm St", "Market St", "Church St",
    "Spring St", "Broadway", "Franklin St", "Madison Ave", "Jefferson St"
]


class EmployeeFactory:
    """Factory para criar funcionários com dados realistas"""

    @staticmethod
    def generate_random_name(gender: Optional[str] = None) -> tuple[str, str]:
        """Gera nome e sobrenome aleatórios"""
        if gender is None:
            gender = random.choice(["male", "female"])

        if gender == "male":
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)

        last_name = random.choice(LAST_NAMES)

        return first_name, last_name

    @staticmethod
    def generate_random_address() -> str:
        """Gera endereço aleatório"""
        number = random.randint(100, 9999)
        street = random.choice(STREETS)
        city = random.choice(CITIES)
        return f"{number} {street}, {city}"

    @staticmethod
    def generate_random_phone() -> str:
        """Gera telefone aleatório"""
        area_code = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"+1-{area_code}-{prefix}-{line}"

    @staticmethod
    def generate_random_dob(min_age: int = 22, max_age: int = 65) -> date:
        """Gera data de nascimento aleatória"""
        years_ago = random.randint(min_age, max_age)
        days_offset = random.randint(0, 365)
        return date.today() - timedelta(days=years_ago * 365 + days_offset)

    @staticmethod
    def generate_random_hire_date(years_back: int = 10) -> date:
        """Gera data de contratação aleatória"""
        days_back = random.randint(0, years_back * 365)
        return date.today() - timedelta(days=days_back)

    @staticmethod
    def create_employee_data(
        job_title: JobTitle,
        department: Department,
        level: EmployeeLevel,
        manager_id: Optional[str] = None,
        location: str = "Headquarters"
    ) -> Dict[str, Any]:
        """Cria dados de funcionário completos"""
        first_name, last_name = EmployeeFactory.generate_random_name()

        return {
            "first_name": first_name,
            "last_name": last_name,
            "job_title": job_title.value,
            "department": department.value,
            "level": level.value,
            "manager_id": manager_id,
            "hire_date": EmployeeFactory.generate_random_hire_date().isoformat(),
            "date_of_birth": EmployeeFactory.generate_random_dob().isoformat(),
            "phone": EmployeeFactory.generate_random_phone(),
            "address": EmployeeFactory.generate_random_address(),
            "location": location,
            "contract_type": ContractType.FULL_TIME.value
        }

    @staticmethod
    def create_department_team(
        hr_agent: HRAgent,
        department: Department,
        manager_title: JobTitle,
        team_roles: List[tuple[JobTitle, EmployeeLevel, int]],  # (title, level, count)
        location: str = "Headquarters"
    ) -> Dict[str, Any]:
        """
        Cria um time completo de um departamento

        Args:
            hr_agent: Agente de RH
            department: Departamento
            manager_title: Cargo do gerente
            team_roles: Lista de (cargo, nível, quantidade)
            location: Localização

        Returns:
            Dicionário com manager_id e lista de employee_ids
        """
        # Criar gerente
        manager_data = EmployeeFactory.create_employee_data(
            job_title=manager_title,
            department=department,
            level=EmployeeLevel.MANAGER,
            location=location
        )

        manager_result = hr_agent.hire_employee(manager_data)
        manager_id = manager_result["employee_id"]

        employee_ids = [manager_id]

        # Criar membros do time
        for job_title, level, count in team_roles:
            for _ in range(count):
                employee_data = EmployeeFactory.create_employee_data(
                    job_title=job_title,
                    department=department,
                    level=level,
                    manager_id=manager_id,
                    location=location
                )

                result = hr_agent.hire_employee(employee_data)
                if result["success"]:
                    employee_ids.append(result["employee_id"])

        return {
            "department": department.value,
            "manager_id": manager_id,
            "employee_ids": employee_ids,
            "total_count": len(employee_ids)
        }

    @staticmethod
    def create_complete_branch(
        hr_agent: HRAgent,
        branch_name: str = "Main Branch",
        location: str = "New York, NY"
    ) -> Dict[str, Any]:
        """
        Cria uma filial bancária completa com todos os departamentos

        Args:
            hr_agent: Agente de RH
            branch_name: Nome da filial
            location: Localização

        Returns:
            Dicionário com informações da filial
        """
        print(f"\n🏦 Creating {branch_name} in {location}...")
        print("=" * 60)

        all_employees = []

        # 1. Retail Banking Team
        print("\n📊 Creating Retail Banking Team...")
        retail_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.RETAIL_BANKING,
            manager_title=JobTitle.BRANCH_MANAGER,
            team_roles=[
                (JobTitle.TELLER, EmployeeLevel.JUNIOR, 4),
                (JobTitle.CUSTOMER_SERVICE_REP, EmployeeLevel.PLENO, 3),
                (JobTitle.PERSONAL_BANKER, EmployeeLevel.SENIOR, 2),
                (JobTitle.LOAN_OFFICER, EmployeeLevel.SENIOR, 2)
            ],
            location=location
        )
        all_employees.extend(retail_team["employee_ids"])
        print(f"  ✓ Created {retail_team['total_count']} retail banking employees")

        # 2. Private Banking Team
        print("\n💼 Creating Private Banking Team...")
        private_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.PRIVATE_BANKING,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.PRIVATE_BANKER, EmployeeLevel.SENIOR, 2),
                (JobTitle.WEALTH_MANAGER, EmployeeLevel.SPECIALIST, 2),
                (JobTitle.INVESTMENT_ADVISOR, EmployeeLevel.SENIOR, 2)
            ],
            location=location
        )
        all_employees.extend(private_team["employee_ids"])
        print(f"  ✓ Created {private_team['total_count']} private banking employees")

        # 3. Risk & Compliance Team
        print("\n🛡️ Creating Risk & Compliance Team...")
        risk_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.RISK_MANAGEMENT,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.RISK_ANALYST, EmployeeLevel.PLENO, 2),
                (JobTitle.COMPLIANCE_OFFICER, EmployeeLevel.SENIOR, 2),
                (JobTitle.AML_SPECIALIST, EmployeeLevel.SPECIALIST, 1),
                (JobTitle.FRAUD_ANALYST, EmployeeLevel.PLENO, 2)
            ],
            location=location
        )
        all_employees.extend(risk_team["employee_ids"])
        print(f"  ✓ Created {risk_team['total_count']} risk & compliance employees")

        # 4. Operations Team
        print("\n⚙️ Creating Operations Team...")
        ops_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.OPERATIONS,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.OPERATIONS_ANALYST, EmployeeLevel.PLENO, 3),
                (JobTitle.SETTLEMENT_OFFICER, EmployeeLevel.SENIOR, 2),
                (JobTitle.RECONCILIATION_SPECIALIST, EmployeeLevel.PLENO, 2)
            ],
            location=location
        )
        all_employees.extend(ops_team["employee_ids"])
        print(f"  ✓ Created {ops_team['total_count']} operations employees")

        # 5. IT Team
        print("\n💻 Creating IT Team...")
        it_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.IT,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.SOFTWARE_ENGINEER, EmployeeLevel.SENIOR, 2),
                (JobTitle.SOFTWARE_ENGINEER, EmployeeLevel.PLENO, 2),
                (JobTitle.DATA_ANALYST, EmployeeLevel.PLENO, 1),
                (JobTitle.CYBERSECURITY_SPECIALIST, EmployeeLevel.SPECIALIST, 1),
                (JobTitle.DEVOPS_ENGINEER, EmployeeLevel.SENIOR, 1)
            ],
            location=location
        )
        all_employees.extend(it_team["employee_ids"])
        print(f"  ✓ Created {it_team['total_count']} IT employees")

        # 6. HR Team
        print("\n👥 Creating HR Team...")
        hr_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.HR,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.CUSTOMER_SERVICE_REP, EmployeeLevel.PLENO, 2),  # HR Specialists
            ],
            location=location
        )
        all_employees.extend(hr_team["employee_ids"])
        print(f"  ✓ Created {hr_team['total_count']} HR employees")

        # 7. Create Credit Analysis Team
        print("\n📈 Creating Credit Analysis Team...")
        credit_team = EmployeeFactory.create_department_team(
            hr_agent=hr_agent,
            department=Department.CORPORATE_BANKING,
            manager_title=JobTitle.DEPARTMENT_MANAGER,
            team_roles=[
                (JobTitle.CREDIT_ANALYST, EmployeeLevel.SENIOR, 2),
                (JobTitle.CREDIT_ANALYST, EmployeeLevel.PLENO, 2),
                (JobTitle.UNDERWRITER, EmployeeLevel.SENIOR, 2)
            ],
            location=location
        )
        all_employees.extend(credit_team["employee_ids"])
        print(f"  ✓ Created {credit_team['total_count']} credit analysis employees")

        print("\n" + "=" * 60)
        print(f"✅ {branch_name} created successfully!")
        print(f"📊 Total employees: {len(all_employees)}")
        print("=" * 60)

        return {
            "branch_name": branch_name,
            "location": location,
            "employee_ids": all_employees,
            "total_employees": len(all_employees),
            "teams": {
                "retail_banking": retail_team,
                "private_banking": private_team,
                "risk_compliance": risk_team,
                "operations": ops_team,
                "it": it_team,
                "hr": hr_team,
                "credit": credit_team
            }
        }

    @staticmethod
    def create_executive_team(hr_agent: HRAgent) -> Dict[str, Any]:
        """Cria o time executivo (C-Level)"""
        print("\n👔 Creating Executive Team...")
        print("=" * 60)

        executives = []

        # CEO
        ceo_data = EmployeeFactory.create_employee_data(
            job_title=JobTitle.CEO,
            department=Department.OPERATIONS,
            level=EmployeeLevel.C_LEVEL,
            location="Headquarters"
        )
        ceo_result = hr_agent.hire_employee(ceo_data)
        ceo_id = ceo_result["employee_id"]
        executives.append(ceo_id)
        print(f"  ✓ CEO: {ceo_result['employee']['full_name']}")

        # Other C-Level executives reporting to CEO
        c_level_roles = [
            (JobTitle.CFO, Department.FINANCE),
            (JobTitle.CRO, Department.RISK_MANAGEMENT),
            (JobTitle.CTO, Department.IT),
            (JobTitle.COO, Department.OPERATIONS)
        ]

        for title, dept in c_level_roles:
            exec_data = EmployeeFactory.create_employee_data(
                job_title=title,
                department=dept,
                level=EmployeeLevel.C_LEVEL,
                manager_id=ceo_id,
                location="Headquarters"
            )
            result = hr_agent.hire_employee(exec_data)
            executives.append(result["employee_id"])
            print(f"  ✓ {title.value.upper()}: {result['employee']['full_name']}")

        # VPs reporting to CXOs
        vp_roles = [
            (JobTitle.VP, Department.RETAIL_BANKING, executives[1]),  # Reports to CFO
            (JobTitle.VP, Department.PRIVATE_BANKING, executives[1]),
            (JobTitle.VP, Department.COMPLIANCE, executives[2]),  # Reports to CRO
            (JobTitle.SVP, Department.IT, executives[3]),  # Reports to CTO
        ]

        for title, dept, manager_id in vp_roles:
            vp_data = EmployeeFactory.create_employee_data(
                job_title=title,
                department=dept,
                level=EmployeeLevel.VP,
                manager_id=manager_id,
                location="Headquarters"
            )
            result = hr_agent.hire_employee(vp_data)
            executives.append(result["employee_id"])
            print(f"  ✓ {title.value.upper()} ({dept.value}): {result['employee']['full_name']}")

        print("=" * 60)
        print(f"✅ Executive team created: {len(executives)} executives")
        print("=" * 60)

        return {
            "ceo_id": ceo_id,
            "executive_ids": executives,
            "total_count": len(executives)
        }
