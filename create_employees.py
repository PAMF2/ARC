"""
Create Bank Employees
Script para criar uma organização bancária completa com funcionários

Usage:
    python create_employees.py --branch "Main Branch" --location "New York, NY"
    python create_employees.py --executives-only
    python create_employees.py --full-organization
"""
import argparse
import json
from datetime import datetime
from divisions.hr_agent import HRAgent
from employees.employee_factory import EmployeeFactory
from core.employee_types import EmploymentStatus


def create_executives(hr_agent: HRAgent):
    """Cria apenas o time executivo"""
    result = EmployeeFactory.create_executive_team(hr_agent)
    return result


def create_branch(hr_agent: HRAgent, branch_name: str, location: str):
    """Cria uma filial completa"""
    result = EmployeeFactory.create_complete_branch(
        hr_agent=hr_agent,
        branch_name=branch_name,
        location=location
    )
    return result


def create_full_organization(hr_agent: HRAgent):
    """Cria organização completa: executivos + múltiplas filiais"""
    print("\n" + "=" * 80)
    print("🏦 CREATING FULL BANKING ORGANIZATION")
    print("=" * 80)

    all_employees = []

    # 1. Create Executive Team
    exec_result = create_executives(hr_agent)
    all_employees.extend(exec_result["executive_ids"])

    # 2. Create Main Branch
    main_branch = create_branch(hr_agent, "Main Branch", "New York, NY")
    all_employees.extend(main_branch["employee_ids"])

    # 3. Create Regional Branches
    branches = [
        ("West Coast Branch", "Los Angeles, CA"),
        ("Midwest Branch", "Chicago, IL"),
        ("South Branch", "Houston, TX"),
        ("East Coast Branch", "Boston, MA")
    ]

    branch_results = []
    for branch_name, location in branches:
        branch_result = create_branch(hr_agent, branch_name, location)
        all_employees.extend(branch_result["employee_ids"])
        branch_results.append(branch_result)

    print("\n" + "=" * 80)
    print("🎉 ORGANIZATION CREATION COMPLETE!")
    print("=" * 80)
    print(f"📊 Total Employees Created: {len(all_employees)}")
    print(f"👔 Executives: {exec_result['total_count']}")
    print(f"🏦 Branches: {len(branches) + 1}")
    print("=" * 80)

    return {
        "executives": exec_result,
        "main_branch": main_branch,
        "regional_branches": branch_results,
        "total_employees": len(all_employees),
        "all_employee_ids": all_employees
    }


def print_organization_summary(hr_agent: HRAgent):
    """Imprime resumo da organização"""
    summary = hr_agent.get_organization_summary()

    print("\n" + "=" * 80)
    print("📊 ORGANIZATION SUMMARY")
    print("=" * 80)
    print(f"Total Employees: {summary['total_employees']}")
    print(f"Active Employees: {summary['active_employees']}")
    print(f"Average Tenure: {summary['average_tenure']:.1f} years")

    print("\n📂 DEPARTMENTS:")
    for dept, count in sorted(summary['departments'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {dept.replace('_', ' ').title()}: {count} employees")

    print("\n📈 LEVELS:")
    for level, count in sorted(summary['levels'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {level.replace('_', ' ').title()}: {count} employees")

    print("=" * 80)


def print_employee_directory(hr_agent: HRAgent, limit: int = 20):
    """Imprime diretório de funcionários"""
    employees = hr_agent.get_all_employees(status=EmploymentStatus.ACTIVE)

    print("\n" + "=" * 80)
    print(f"👥 EMPLOYEE DIRECTORY (showing {min(limit, len(employees))} of {len(employees)})")
    print("=" * 80)

    # Ordenar por nível e depois por nome
    level_order = {
        'c_level': 0, 'vice_president': 1, 'director': 2, 'manager': 3,
        'specialist': 4, 'coordinator': 5, 'senior': 6, 'pleno': 7,
        'junior': 8, 'trainee': 9
    }

    sorted_employees = sorted(
        employees,
        key=lambda e: (level_order.get(e.level.value, 99), e.last_name)
    )

    for i, employee in enumerate(sorted_employees[:limit]):
        print(f"\n{i+1}. {employee.full_name}")
        print(f"   ID: {employee.employee_id}")
        print(f"   Title: {employee.display_title}")
        print(f"   Department: {employee.department.value.replace('_', ' ').title()}")
        print(f"   Email: {employee.email}")
        print(f"   Location: {employee.location}")

        if employee.compensation:
            print(f"   Salary: ${employee.compensation.base_salary:,.0f}")

        if employee.manager_id:
            manager = hr_agent.get_employee(employee.manager_id)
            if manager:
                print(f"   Manager: {manager.full_name}")

        if employee.direct_reports:
            print(f"   Direct Reports: {len(employee.direct_reports)}")

    if len(employees) > limit:
        print(f"\n... and {len(employees) - limit} more employees")

    print("=" * 80)


def save_organization_to_file(hr_agent: HRAgent, filename: str = "organization.json"):
    """Salva organização em arquivo JSON"""
    employees = hr_agent.get_all_employees()

    data = {
        "export_date": datetime.now().isoformat(),
        "total_employees": len(employees),
        "summary": hr_agent.get_organization_summary(),
        "employees": [emp.to_dict() for emp in employees]
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Organization saved to: {filename}")
    print(f"   Total employees: {len(employees)}")
    print(f"   File size: {len(json.dumps(data))} bytes")


def main():
    parser = argparse.ArgumentParser(description='Create bank employees')
    parser.add_argument('--executives-only', action='store_true', help='Create only executive team')
    parser.add_argument('--branch', type=str, help='Create single branch with name')
    parser.add_argument('--location', type=str, default='New York, NY', help='Branch location')
    parser.add_argument('--full-organization', action='store_true', help='Create full organization')
    parser.add_argument('--save', type=str, help='Save to JSON file')
    parser.add_argument('--directory', action='store_true', help='Print employee directory')
    parser.add_argument('--summary', action='store_true', help='Print organization summary')

    args = parser.parse_args()

    # Initialize HR Agent
    print("\n🚀 Initializing HR Agent...")
    hr_agent = HRAgent()

    # Execute requested action
    if args.executives_only:
        create_executives(hr_agent)

    elif args.branch:
        create_branch(hr_agent, args.branch, args.location)

    elif args.full_organization:
        create_full_organization(hr_agent)

    else:
        # Default: create a single branch
        print("\n💡 No specific action provided. Creating a sample branch...")
        print("   Use --help to see all options\n")
        create_branch(hr_agent, "Sample Branch", "New York, NY")

    # Print summary if requested or by default
    if args.summary or not any([args.executives_only, args.branch, args.full_organization]):
        print_organization_summary(hr_agent)

    # Print directory if requested
    if args.directory:
        print_employee_directory(hr_agent)

    # Save to file if requested
    if args.save:
        save_organization_to_file(hr_agent, args.save)

    print("\n✅ Employee creation complete!\n")


if __name__ == "__main__":
    main()
