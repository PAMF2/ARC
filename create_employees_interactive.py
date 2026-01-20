"""
Interactive Employee Creator
Interface interativa para criar funcionários

Usage:
    python create_employees_interactive.py
"""
from divisions.hr_agent import HRAgent
from employees.employee_factory import EmployeeFactory
from core.employee_types import (
    Department, JobTitle, EmployeeLevel, EmploymentStatus
)


def print_menu():
    """Imprime menu principal"""
    print("\n" + "=" * 60)
    print("🏦 BANK EMPLOYEE CREATOR")
    print("=" * 60)
    print("\n📋 MENU:")
    print("  1. Create Executive Team (C-Level + VPs)")
    print("  2. Create Single Branch (50+ employees)")
    print("  3. Create Full Organization (150+ employees)")
    print("  4. Create Custom Department Team")
    print("  5. Create Individual Employee")
    print("  6. View Organization Summary")
    print("  7. View Employee Directory")
    print("  8. Search Employee")
    print("  9. Export to JSON")
    print("  0. Exit")
    print("=" * 60)


def create_custom_department_team(hr_agent: HRAgent):
    """Interface para criar time customizado"""
    print("\n📂 AVAILABLE DEPARTMENTS:")
    departments = list(Department)
    for i, dept in enumerate(departments, 1):
        print(f"  {i}. {dept.value.replace('_', ' ').title()}")

    dept_choice = int(input("\nSelect department number: ")) - 1
    department = departments[dept_choice]

    print("\n👔 SELECT MANAGER TITLE:")
    manager_titles = [
        JobTitle.BRANCH_MANAGER,
        JobTitle.DEPARTMENT_MANAGER,
        JobTitle.REGIONAL_MANAGER
    ]
    for i, title in enumerate(manager_titles, 1):
        print(f"  {i}. {title.value.replace('_', ' ').title()}")

    title_choice = int(input("\nSelect manager title: ")) - 1
    manager_title = manager_titles[title_choice]

    location = input("\nLocation (default: Headquarters): ").strip() or "Headquarters"

    print("\n👥 TEAM COMPOSITION:")
    print("  Enter number of employees for each level (0 to skip)")

    team_roles = []

    # Pedir informações para cada nível
    levels = [EmployeeLevel.SENIOR, EmployeeLevel.PLENO, EmployeeLevel.JUNIOR]

    for level in levels:
        count = int(input(f"  {level.value.title()} employees: ") or "0")
        if count > 0:
            # Selecionar job title apropriado
            if department == Department.IT:
                title = JobTitle.SOFTWARE_ENGINEER
            elif department == Department.RISK_MANAGEMENT:
                title = JobTitle.RISK_ANALYST
            elif department == Department.OPERATIONS:
                title = JobTitle.OPERATIONS_ANALYST
            else:
                title = JobTitle.CUSTOMER_SERVICE_REP

            team_roles.append((title, level, count))

    print("\n🔨 Creating team...")
    result = EmployeeFactory.create_department_team(
        hr_agent=hr_agent,
        department=department,
        manager_title=manager_title,
        team_roles=team_roles,
        location=location
    )

    print(f"\n✅ Team created successfully!")
    print(f"   Department: {department.value.replace('_', ' ').title()}")
    print(f"   Total employees: {result['total_count']}")
    print(f"   Manager ID: {result['manager_id']}")


def create_individual_employee(hr_agent: HRAgent):
    """Interface para criar funcionário individual"""
    print("\n👤 CREATE INDIVIDUAL EMPLOYEE")
    print("-" * 60)

    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    print("\n📂 SELECT DEPARTMENT:")
    departments = list(Department)
    for i, dept in enumerate(departments, 1):
        print(f"  {i}. {dept.value.replace('_', ' ').title()}")

    dept_choice = int(input("\nDepartment number: ")) - 1
    department = departments[dept_choice]

    print("\n👔 SELECT JOB TITLE:")
    titles = list(JobTitle)
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title.value.replace('_', ' ').title()}")

    title_choice = int(input("\nJob title number: ")) - 1
    job_title = titles[title_choice]

    print("\n📈 SELECT LEVEL:")
    levels = list(EmployeeLevel)
    for i, level in enumerate(levels, 1):
        print(f"  {i}. {level.value.replace('_', ' ').title()}")

    level_choice = int(input("\nLevel number: ")) - 1
    level = levels[level_choice]

    location = input("\nLocation (default: Headquarters): ").strip() or "Headquarters"

    employee_data = {
        "first_name": first_name,
        "last_name": last_name,
        "job_title": job_title.value,
        "department": department.value,
        "level": level.value,
        "location": location
    }

    result = hr_agent.hire_employee(employee_data)

    if result["success"]:
        print(f"\n✅ Employee created successfully!")
        print(f"   Name: {result['employee']['full_name']}")
        print(f"   ID: {result['employee_id']}")
        print(f"   Email: {result['employee']['email']}")
        print(f"   Title: {result['employee']['display_title']}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")


def view_organization_summary(hr_agent: HRAgent):
    """Visualiza resumo da organização"""
    summary = hr_agent.get_organization_summary()

    print("\n" + "=" * 60)
    print("📊 ORGANIZATION SUMMARY")
    print("=" * 60)
    print(f"Total Employees: {summary['total_employees']}")
    print(f"Active Employees: {summary['active_employees']}")
    print(f"Average Tenure: {summary['average_tenure']:.1f} years")

    print("\n📂 BY DEPARTMENT:")
    for dept, count in sorted(summary['departments'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {dept.replace('_', ' ').title()}: {count}")

    print("\n📈 BY LEVEL:")
    for level, count in sorted(summary['levels'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {level.replace('_', ' ').title()}: {count}")


def view_employee_directory(hr_agent: HRAgent):
    """Visualiza diretório de funcionários"""
    employees = hr_agent.get_all_employees(status=EmploymentStatus.ACTIVE)

    if not employees:
        print("\n⚠️  No employees found.")
        return

    print(f"\n👥 EMPLOYEE DIRECTORY ({len(employees)} employees)")
    print("=" * 80)

    # Ordenar por departamento e nome
    sorted_employees = sorted(employees, key=lambda e: (e.department.value, e.last_name))

    current_dept = None
    for employee in sorted_employees:
        if employee.department != current_dept:
            current_dept = employee.department
            print(f"\n📂 {current_dept.value.replace('_', ' ').title().upper()}")
            print("-" * 80)

        print(f"  • {employee.full_name:<30} {employee.display_title:<35} {employee.email}")


def search_employee(hr_agent: HRAgent):
    """Busca funcionário"""
    query = input("\n🔍 Enter employee name or ID: ").strip().lower()

    employees = hr_agent.get_all_employees()
    matches = [
        e for e in employees
        if query in e.full_name.lower() or query in e.employee_id.lower()
    ]

    if not matches:
        print(f"\n⚠️  No employees found matching '{query}'")
        return

    print(f"\n✅ Found {len(matches)} employee(s):")
    print("=" * 80)

    for employee in matches:
        print(f"\n👤 {employee.full_name}")
        print(f"   ID: {employee.employee_id}")
        print(f"   Title: {employee.display_title}")
        print(f"   Department: {employee.department.value.replace('_', ' ').title()}")
        print(f"   Email: {employee.email}")
        print(f"   Status: {employee.status.value.title()}")
        print(f"   Location: {employee.location}")
        print(f"   Tenure: {employee.years_of_service} years")

        if employee.compensation:
            print(f"   Salary: ${employee.compensation.base_salary:,.0f}")

        if employee.manager_id:
            manager = hr_agent.get_employee(employee.manager_id)
            if manager:
                print(f"   Manager: {manager.full_name}")

        if employee.direct_reports:
            print(f"   Direct Reports: {len(employee.direct_reports)}")


def export_to_json(hr_agent: HRAgent):
    """Exporta para JSON"""
    import json
    from datetime import datetime

    filename = input("\n💾 Filename (default: organization.json): ").strip() or "organization.json"

    employees = hr_agent.get_all_employees()

    data = {
        "export_date": datetime.now().isoformat(),
        "total_employees": len(employees),
        "summary": hr_agent.get_organization_summary(),
        "employees": [emp.to_dict() for emp in employees]
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Exported successfully!")
    print(f"   File: {filename}")
    print(f"   Employees: {len(employees)}")


def main():
    """Main interactive loop"""
    print("\n🚀 Initializing HR System...")
    hr_agent = HRAgent()

    while True:
        print_menu()

        try:
            choice = input("\n👉 Select option: ").strip()

            if choice == "1":
                print("\n👔 Creating Executive Team...")
                result = EmployeeFactory.create_executive_team(hr_agent)
                print(f"✅ Created {result['total_count']} executives")

            elif choice == "2":
                branch_name = input("\n🏦 Branch name (default: Main Branch): ").strip() or "Main Branch"
                location = input("Location (default: New York, NY): ").strip() or "New York, NY"
                result = EmployeeFactory.create_complete_branch(hr_agent, branch_name, location)

            elif choice == "3":
                confirm = input("\n⚠️  This will create 150+ employees. Continue? (yes/no): ").strip().lower()
                if confirm == "yes":
                    print("\n🏗️  Creating full organization...")
                    from create_employees import create_full_organization
                    create_full_organization(hr_agent)

            elif choice == "4":
                create_custom_department_team(hr_agent)

            elif choice == "5":
                create_individual_employee(hr_agent)

            elif choice == "6":
                view_organization_summary(hr_agent)

            elif choice == "7":
                view_employee_directory(hr_agent)

            elif choice == "8":
                search_employee(hr_agent)

            elif choice == "9":
                export_to_json(hr_agent)

            elif choice == "0":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n⚠️  Invalid option. Please try again.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n")


if __name__ == "__main__":
    main()
