# 👥 Bank Employee Management System

Sistema completo de gestão de funcionários bancários com hierarquia organizacional, departamentos, cargos e benefícios.

## 🎯 Features

### ✅ Modelos de Dados Completos
- **Employee**: Modelo completo com informações pessoais, profissionais e credenciais
- **EmployeeCredentials**: Credenciais de acesso e permissões
- **EmployeeCompensation**: Salário, benefícios e bônus
- **EmployeePerformance**: Avaliações e metas

### 📊 Hierarquia Organizacional
- 10 níveis hierárquicos (Trainee até C-Level)
- 16 departamentos bancários
- 40+ cargos disponíveis
- Estrutura de reports (subordinados diretos)

### 🤖 HR Agent
Agente inteligente para gerenciar funcionários:
- Contratação (hire)
- Demissão (terminate)
- Promoção (promote)
- Transferência de departamento (transfer)
- Avaliação de performance (review)

### 🏭 Employee Factory
Criação em massa de funcionários com dados realistas:
- Nomes e sobrenomes variados
- Endereços em cidades dos EUA
- Telefones formatados
- Datas de nascimento e contratação
- Salários baseados em faixas realistas

## 🚀 Quick Start

### 1. Criar Organização Completa (150+ funcionários)

```bash
cd banking
python create_employees.py --full-organization
```

Isso cria:
- ✓ 5 executivos C-Level
- ✓ 4 Vice-Presidents
- ✓ 5 filiais completas em diferentes cidades
- ✓ 150+ funcionários em todos os departamentos

### 2. Criar Uma Filial

```bash
python create_employees.py --branch "West Coast Branch" --location "Los Angeles, CA"
```

Isso cria uma filial com:
- ✓ 50+ funcionários
- ✓ 7 departamentos operacionais
- ✓ Hierarquia completa (gerentes e times)

### 3. Criar Apenas Executivos

```bash
python create_employees.py --executives-only
```

Cria apenas o time executivo (C-Level + VPs).

### 4. Modo Interativo

```bash
python create_employees_interactive.py
```

Interface interativa com menu para:
1. Criar executive team
2. Criar filial completa
3. Criar organização completa
4. Criar time customizado
5. Criar funcionário individual
6. Ver resumo da organização
7. Ver diretório de funcionários
8. Buscar funcionário
9. Exportar para JSON

## 📋 Exemplos de Uso

### Criar e Gerenciar Funcionários Programaticamente

```python
from divisions.hr_agent import HRAgent
from employees.employee_factory import EmployeeFactory
from core.employee_types import Department, JobTitle, EmployeeLevel

# Initialize HR Agent
hr_agent = HRAgent()

# 1. Criar Executive Team
exec_result = EmployeeFactory.create_executive_team(hr_agent)
print(f"Created {exec_result['total_count']} executives")

# 2. Criar uma filial completa
branch_result = EmployeeFactory.create_complete_branch(
    hr_agent=hr_agent,
    branch_name="Silicon Valley Branch",
    location="San Jose, CA"
)
print(f"Created branch with {branch_result['total_employees']} employees")

# 3. Criar funcionário individual
employee_data = {
    "first_name": "John",
    "last_name": "Doe",
    "job_title": JobTitle.SOFTWARE_ENGINEER.value,
    "department": Department.IT.value,
    "level": EmployeeLevel.SENIOR.value,
    "location": "Headquarters"
}

result = hr_agent.hire_employee(employee_data)
print(f"Hired: {result['employee']['full_name']}")

# 4. Ver resumo da organização
summary = hr_agent.get_organization_summary()
print(f"Total employees: {summary['total_employees']}")
print(f"Active: {summary['active_employees']}")

# 5. Buscar funcionários por departamento
it_employees = hr_agent.get_department_employees(Department.IT)
print(f"IT Department has {len(it_employees)} employees")

# 6. Promover funcionário
hr_agent.promote_employee(
    employee_id=result['employee_id'],
    new_title=JobTitle.DIRECTOR.value,
    new_level=EmployeeLevel.DIRECTOR.value
)

# 7. Fazer avaliação de performance
hr_agent.conduct_review(
    employee_id=result['employee_id'],
    rating=4.5,
    reviewer="Jane Smith",
    comments="Excellent performance this quarter"
)

# 8. Ver subordinados de um gerente
manager_id = exec_result['ceo_id']
direct_reports = hr_agent.get_employees_by_manager(manager_id)
print(f"CEO has {len(direct_reports)} direct reports")
```

### Criar Time Customizado

```python
from divisions.hr_agent import HRAgent
from employees.employee_factory import EmployeeFactory
from core.employee_types import Department, JobTitle, EmployeeLevel

hr_agent = HRAgent()

# Criar time de Cybersecurity
team = EmployeeFactory.create_department_team(
    hr_agent=hr_agent,
    department=Department.IT,
    manager_title=JobTitle.DEPARTMENT_MANAGER,
    team_roles=[
        (JobTitle.CYBERSECURITY_SPECIALIST, EmployeeLevel.SENIOR, 2),
        (JobTitle.CYBERSECURITY_SPECIALIST, EmployeeLevel.PLENO, 3),
        (JobTitle.SOFTWARE_ENGINEER, EmployeeLevel.SENIOR, 1),
    ],
    location="Headquarters"
)

print(f"Created cybersecurity team with {team['total_count']} members")
```

## 📊 Estrutura de Dados

### Departamentos Disponíveis

#### Front Office
- `RETAIL_BANKING` - Varejo
- `PRIVATE_BANKING` - Private Banking
- `CORPORATE_BANKING` - Corporativo
- `INVESTMENT_BANKING` - Investment Banking

#### Middle Office
- `RISK_MANAGEMENT` - Gestão de Risco
- `COMPLIANCE` - Compliance
- `TREASURY` - Tesouraria
- `TRADING` - Trading

#### Back Office
- `OPERATIONS` - Operações
- `CLEARING_SETTLEMENT` - Liquidação
- `IT` - Tecnologia
- `FINANCE` - Finanças

#### Support
- `HR` - Recursos Humanos
- `LEGAL` - Jurídico
- `MARKETING` - Marketing
- `FACILITIES` - Facilities

### Níveis Hierárquicos

1. **C_LEVEL** (Level 10) - $450k-$1.5M
   - CEO, CFO, CRO, CTO, COO

2. **VP** (Level 9) - $280k-$450k
   - Vice President, Senior Vice President

3. **DIRECTOR** (Level 8) - $180k-$280k
   - Directors

4. **MANAGER** (Level 6-7) - $120k-$180k
   - Branch Manager, Department Manager, Regional Manager

5. **SENIOR** (Level 5) - $95k-$140k
   - Senior positions

6. **PLENO** (Level 3) - $65k-$95k
   - Mid-level positions

7. **JUNIOR** (Level 2) - $45k-$65k
   - Entry-level positions

8. **TRAINEE** (Level 1) - $35k-$45k
   - Interns and trainees

### Cargos (40+ disponíveis)

**Atendimento:**
- Teller
- Customer Service Representative
- Personal Banker
- Relationship Manager
- Private Banker

**Consultoria:**
- Investment Advisor
- Wealth Manager
- Financial Planner

**Crédito:**
- Loan Officer
- Credit Analyst
- Underwriter

**Risk & Compliance:**
- Risk Analyst
- Compliance Officer
- AML Specialist
- Fraud Analyst

**Treasury & Trading:**
- Trader
- Treasury Analyst
- Portfolio Manager
- Quantitative Analyst

**Operations:**
- Operations Analyst
- Settlement Officer
- Reconciliation Specialist

**IT:**
- Software Engineer
- Data Analyst
- Cybersecurity Specialist
- DevOps Engineer

**Management:**
- Branch Manager
- Department Manager
- Regional Manager

**Executive:**
- Director, VP, SVP
- CFO, CRO, CTO, COO, CEO

## 🔧 Funcionalidades do HR Agent

### 1. Analyze Transaction
Valida se o funcionário está autorizado a fazer transações:
- ✓ Verifica status do funcionário
- ✓ Valida credenciais ativas
- ✓ Checa permissões

### 2. Hire Employee
Contrata novo funcionário:
- ✓ Gera ID único
- ✓ Cria email corporativo
- ✓ Define salário baseado no nível
- ✓ Cria credenciais de acesso
- ✓ Atribui permissões por departamento/cargo
- ✓ Configura avaliação inicial (90 dias)

### 3. Terminate Employee
Desliga funcionário:
- ✓ Atualiza status
- ✓ Desativa credenciais
- ✓ Reatribui subordinados
- ✓ Registra motivo

### 4. Promote Employee
Promove funcionário:
- ✓ Atualiza cargo e nível
- ✓ Ajusta salário (mínimo 10% de aumento)
- ✓ Atualiza permissões
- ✓ Registra histórico

### 5. Transfer Employee
Transfere entre departamentos:
- ✓ Move entre departamentos
- ✓ Mantém nível e salário
- ✓ Registra transferência

### 6. Conduct Review
Realiza avaliação de performance:
- ✓ Registra rating (0-5)
- ✓ Atualiza média de avaliações
- ✓ Agenda próxima avaliação (6 meses)

## 📤 Export e Análise

### Exportar para JSON

```bash
python create_employees.py --full-organization --save organization.json
```

Formato do export:
```json
{
  "export_date": "2026-01-20T...",
  "total_employees": 150,
  "summary": {
    "total_employees": 150,
    "active_employees": 150,
    "departments": {...},
    "levels": {...},
    "average_tenure": 3.2
  },
  "employees": [...]
}
```

### Ver Resumo e Estatísticas

```bash
python create_employees.py --full-organization --summary --directory
```

Output:
```
📊 ORGANIZATION SUMMARY
==================================================
Total Employees: 150
Active Employees: 150
Average Tenure: 3.2 years

📂 BY DEPARTMENT:
  • Retail Banking: 45
  • Risk Management: 28
  • Operations: 24
  ...

📈 BY LEVEL:
  • Pleno: 42
  • Senior: 38
  • Junior: 35
  ...
```

## 🎨 Customização

### Adicionar Novos Cargos

Edite `core/employee_types.py`:

```python
class JobTitle(Enum):
    # ... existing titles
    BLOCKCHAIN_SPECIALIST = "blockchain_specialist"
    AI_ENGINEER = "ai_engineer"
```

### Adicionar Novos Departamentos

```python
class Department(Enum):
    # ... existing departments
    INNOVATION = "innovation"
    BLOCKCHAIN = "blockchain"
```

### Customizar Faixas Salariais

```python
SALARY_RANGES = {
    EmployeeLevel.SENIOR: (100_000, 150_000),  # Adjusted
    # ... other levels
}
```

## 📊 Métricas e Relatórios

O sistema mantém automaticamente:
- ✓ Total de funcionários por departamento
- ✓ Distribuição por nível hierárquico
- ✓ Tempo médio de casa
- ✓ Estrutura organizacional (org chart)
- ✓ Histórico de avaliações
- ✓ Histórico de movimentações

## 🔐 Permissões e Acesso

O sistema define automaticamente permissões baseadas em:
1. **Departamento** - Acesso a dados departamentais
2. **Cargo** - Operações permitidas
3. **Nível** - Amplitude de acesso

Exemplos de permissões:
- `read_own_data` - Todos
- `view_risk_reports` - Risk Management
- `approve_transactions` - Manager+
- `strategic_decisions` - Director+
- `full_access` - C-Level

## 🚀 Próximos Passos

Após criar funcionários, você pode:

1. **Integrar com Banking Agents**: Os funcionários podem ser vinculados aos agentes bancários (Front Office, Risk, Treasury, etc.)

2. **Criar Workflow de Aprovações**: Usar a hierarquia para workflows multi-nível

3. **Dashboard de RH**: Criar interface para visualizar organização

4. **Relatórios**: Gerar relatórios de headcount, turnover, etc.

5. **Performance Management**: Sistema completo de avaliações e metas

## 📝 Examples

Ver também:
- `examples/employee_management_demo.py` - Demonstração completa
- `test_employee_system.py` - Testes unitários

## 🐛 Troubleshooting

**Problema**: Erro ao importar módulos
```bash
# Solução: Execute do diretório banking/
cd banking
python create_employees.py
```

**Problema**: Permissões incorretas
```python
# Solução: Use _determine_permissions para recalcular
hr_agent._determine_permissions(dept, title, level)
```

## 📚 Documentação Adicional

- `core/employee_types.py` - Modelos de dados completos
- `divisions/hr_agent.py` - Documentação do HR Agent
- `employees/employee_factory.py` - Factory patterns

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2026-01-20
