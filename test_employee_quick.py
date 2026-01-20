"""
Quick Test of Employee System
Teste rápido para validar o sistema de funcionários
"""
import sys
import os

# Ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

from divisions.hr_agent import HRAgent
from employees.employee_factory import EmployeeFactory
from core.employee_types import Department, JobTitle, EmployeeLevel

def test_basic_employee_creation():
    """Teste básico: criar alguns funcionários"""
    print("\n" + "=" * 60)
    print("TESTING EMPLOYEE SYSTEM")
    print("=" * 60)

    # Initialize HR Agent
    print("\n[1] Initializing HR Agent...")
    hr_agent = HRAgent()
    print("   [OK] HR Agent initialized")

    # Create individual employee
    print("\n[2] Creating individual employee...")
    employee_data = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "job_title": JobTitle.SOFTWARE_ENGINEER.value,
        "department": Department.IT.value,
        "level": EmployeeLevel.SENIOR.value,
        "base_salary": 120000,
        "location": "San Francisco"
    }

    result = hr_agent.hire_employee(employee_data)
    if result["success"]:
        print(f"   [OK] Hired: {result['employee']['full_name']}")
        print(f"   [OK] ID: {result['employee_id']}")
        print(f"   [OK] Email: {result['employee']['email']}")
        print(f"   [OK] Salary: ${result['employee']['compensation']['base_salary']:,.0f}")
        employee_id = result['employee_id']
    else:
        print(f"   [FAIL] Failed: {result.get('error')}")
        return False

    # Create a small team
    print("\n[3] Creating a small IT team...")
    team = EmployeeFactory.create_department_team(
        hr_agent=hr_agent,
        department=Department.IT,
        manager_title=JobTitle.DEPARTMENT_MANAGER,
        team_roles=[
            (JobTitle.SOFTWARE_ENGINEER, EmployeeLevel.SENIOR, 2),
            (JobTitle.SOFTWARE_ENGINEER, EmployeeLevel.PLENO, 2),
            (JobTitle.DEVOPS_ENGINEER, EmployeeLevel.SENIOR, 1),
        ],
        location="New York"
    )
    print(f"   [OK] Created team with {team['total_count']} employees")
    print(f"   [OK] Manager ID: {team['manager_id']}")

    # View organization summary
    print("\n[4] Organization Summary:")
    summary = hr_agent.get_organization_summary()
    print(f"   - Total Employees: {summary['total_employees']}")
    print(f"   - Active Employees: {summary['active_employees']}")
    print(f"   - Departments: {len(summary['departments'])}")

    # Test promotion
    print("\n[5] Testing promotion...")
    promo_result = hr_agent.promote_employee(
        employee_id=employee_id,
        new_title=JobTitle.DIRECTOR.value,
        new_level=EmployeeLevel.DIRECTOR.value
    )
    if promo_result["success"]:
        print(f"   [OK] Promoted to: {promo_result['new_title']}")
        print(f"   [OK] New salary: ${promo_result['new_salary']:,.0f}")

    # Test performance review
    print("\n[6] Testing performance review...")
    review_result = hr_agent.conduct_review(
        employee_id=employee_id,
        rating=4.5,
        reviewer="John Smith",
        comments="Excellent technical leadership"
    )
    if review_result["success"]:
        print(f"   [OK] Review completed: {review_result['rating']}/5.0")
        print(f"   [OK] Average rating: {review_result['average_rating']:.1f}")

    # Get employee details
    print("\n[7] Employee Details:")
    employee = hr_agent.get_employee(employee_id)
    if employee:
        print(f"   - Name: {employee.full_name}")
        print(f"   - Title: {employee.display_title}")
        print(f"   - Department: {employee.department.value}")
        print(f"   - Years of Service: {employee.years_of_service}")
        print(f"   - Direct Reports: {len(employee.direct_reports)}")
        if employee.performance:
            print(f"   - Performance Rating: {employee.performance.rating:.1f}/5.0")

    # List all employees
    print("\n[8] Employee Directory:")
    all_employees = hr_agent.get_all_employees()
    for i, emp in enumerate(all_employees[:5], 1):  # Show first 5
        print(f"   {i}. {emp.full_name:<25} {emp.display_title:<30} {emp.email}")

    if len(all_employees) > 5:
        print(f"   ... and {len(all_employees) - 5} more")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nFinal Count: {len(all_employees)} employees created")

    return True


if __name__ == "__main__":
    try:
        success = test_basic_employee_creation()
        if success:
            print("\nSystem is working perfectly!")
            print("\nNext steps:")
            print("   - Run: python create_employees_interactive.py")
            print("   - Or: python create_employees.py --full-organization")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
