# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A complete personal finance management system in Python with dual storage backends:
- **JSON-based** ([main.py](main.py)) - Simple file-based storage
- **MySQL-based** ([main_avancado.py](main_avancado.py)) - Production-ready database storage

The system manages bank accounts, digital wallet (cash), expenses, income, budget goals, and provides visualizations and reports.

## Common Commands

### Running the System

```bash
# MySQL version (recommended for production)
python main_avancado.py

# JSON version (simpler, no database required)
python main.py

# Windows executable
.\dist\SistemaControleGastosMySQL.exe
# or
.\Executar_Sistema_MySQL.bat
```

### Database Setup

```bash
# Initialize MySQL database (required for first run)
python init_database.py

# Migrate JSON data to MySQL
python migrar_json_para_mysql.py

# Configure database credentials
# Edit src/db/db_config.py or create .env file
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Build executable for MySQL version
pyinstaller build_exe_mysql.spec --clean

# Build executable for JSON version
pyinstaller SistemaControleGastos.spec --clean

# MySQL backup
mysqldump -u root -p cli_gastos > backup.sql

# Restore MySQL backup
mysql -u root -p cli_gastos < backup.sql
```

## Architecture

### Dual Storage System

The codebase supports two storage backends with identical business logic:

1. **JSON Storage** ([src/controllers/controle_avancado.py](src/controllers/controle_avancado.py))
   - Uses `dados_financeiros_avancado.json` for persistence
   - Suitable for single-user, lightweight deployments

2. **MySQL Storage** ([src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py))
   - Full RDBMS with views, stored procedures, and triggers
   - Connection pooling via [src/db/db_connection.py](src/db/db_connection.py)
   - Schema defined in [src/db/migrations.sql](src/db/migrations.sql)

### Package Structure

```
src/
├── controllers/           # Business logic
│   ├── controle_gastos.py          # Base classes (Despesa, Receita)
│   ├── controle_avancado.py        # JSON implementation
│   └── controle_avancado_mysql.py  # MySQL implementation
├── db/                    # Database layer
│   ├── db_config.py               # MySQL credentials
│   ├── db_connection.py           # Connection pool & query executor
│   └── migrations.sql             # Schema definition
└── utils/                 # Utilities
    └── exportador.py              # CSV, Excel, PDF exports
```

### Key Classes

- **`ControleFinanceiro`** (base class): Core financial operations
- **`ControleFinanceiroAvancado`**: Extended with bank accounts, goals, alerts
  - JSON variant uses file I/O
  - MySQL variant uses `DatabaseManager` for all persistence
- **`ContaBancaria`**: Represents bank accounts with transaction history
- **`MetaGasto`**: Budget goals with alerts at 80% threshold
- **`Despesa`/`Receita`**: Expense/Income entities

### Database Schema (MySQL)

The MySQL version uses 6 tables and 6 views:

**Tables:**
- `contas_bancarias` - Bank accounts and digital wallet
- `historico_saldo` - Transaction history with foreign key to accounts
- `despesas` - Expenses with optional link to paying account
- `receitas` - Income with optional link to receiving account
- `metas_gastos` - Budget goals by category/month/year
- `configuracoes` - System settings (key-value store)

**Views:**
- `v_resumo_contas` - Account summary with current balances
- `v_resumo_despesas_mensal` - Monthly expense aggregates
- `v_resumo_receitas_mensal` - Monthly income aggregates
- `v_gastos_por_categoria` - Spending by category
- `v_despesas_vencendo` - Expenses due within 7 days
- `v_metas_status` - Budget goal status with usage percentages

**Automation:**
- Trigger `trg_despesa_paga_atualizar_meta` updates goals when expenses are paid
- Stored procedure `sp_atualizar_gastos_metas` recalculates goal spending

### Import Conventions

**From main scripts** ([main_avancado.py](main_avancado.py), [main.py](main.py)):
```python
from src.controllers.controle_avancado_mysql import ControleFinanceiroAvancado, ContaBancaria, MetaGasto
from src.controllers.controle_gastos import Despesa, Receita
from src.utils.exportador import Exportador
```

**From utility scripts** (scripts/, root-level .py files):
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db.db_connection import DatabaseManager
from src.db.db_config import DB_CONFIG
```

**Within src/ modules**:
```python
from src.controllers.controle_gastos import ControleFinanceiro
from src.db.db_connection import DatabaseManager
```

## Database Configuration

**Option 1: Environment variables** (recommended):
Create `.env` file:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=cli_gastos
```

**Option 2: Direct edit**:
Modify [src/db/db_config.py](src/db/db_config.py):
```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',  # ← Edit here
    'database': 'cli_gastos',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

**IMPORTANT:** The `.env` file contains sensitive credentials and should never be committed to version control.

## Development Workflow

### Adding a New Feature

1. **Decide storage layer**: Implement in both `controle_avancado.py` (JSON) and `controle_avancado_mysql.py` (MySQL) to maintain parity
2. **MySQL changes**: If database schema changes needed:
   - Update [src/db/migrations.sql](src/db/migrations.sql)
   - Add methods in [src/db/db_connection.py](src/db/db_connection.py) (`DatabaseManager` class)
   - Update [src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py)
3. **UI integration**: Add menu options and handlers in [main_avancado.py](main_avancado.py) or [main.py](main.py)
4. **Test both backends**: Verify feature works with both JSON and MySQL

### Modifying Database Schema

1. Edit [src/db/migrations.sql](src/db/migrations.sql) - add new tables/columns with `IF NOT EXISTS` or `ADD COLUMN IF NOT EXISTS` syntax
2. Run `python init_database.py` to apply changes
3. Update [src/db/db_connection.py](src/db/db_connection.py) `DatabaseManager` class with new query methods
4. Update [src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py) to use new schema

### Creating Utility Scripts

Place in `scripts/` directory and add path handling:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Building Executables

```bash
# MySQL version
pyinstaller build_exe_mysql.spec --clean
# Output: dist/SistemaControleGastosMySQL.exe

# JSON version
pyinstaller SistemaControleGastos.spec --clean
# Output: dist/SistemaControleGastos.exe
```

Both specs include all `src/` modules and required dependencies (matplotlib, pandas, mysql-connector-python, etc.).

## Data Flow

### Expense Payment Flow
1. User selects expense to pay
2. [main_avancado.py](main_avancado.py) calls `controle.pagar_despesa(despesa_id, conta_id)`
3. `ControleFinanceiroAvancado` (MySQL variant):
   - Marks expense as paid in `despesas` table
   - Debits account balance in `contas_bancarias`
   - Logs transaction in `historico_saldo`
   - Trigger `trg_despesa_paga_atualizar_meta` updates `metas_gastos.gasto_atual`
4. If budget goal exceeded 80%, alert displayed

### Income Processing Flow
1. User adds income
2. System credits selected account
3. Transaction logged in `historico_saldo`
4. Account balance updated in `contas_bancarias`

### Report Generation Flow
1. User requests report (monthly/annual/category)
2. `ControleFinanceiroAvancado` queries database or loads JSON
3. `Exportador` class ([src/utils/exportador.py](src/utils/exportador.py)) formats data
4. Output generated as Excel (with pandas/openpyxl) or PDF (with reportlab)
5. Graphs created with matplotlib

## Testing

While there are no automated tests, manual testing checklist:

1. **Database operations**: Verify CRUD for all entities (accounts, expenses, income, goals)
2. **Transaction integrity**: Check that account balances update correctly on payments/transfers
3. **Foreign key constraints**: Delete account with expenses - should set `conta_id` to NULL
4. **Budget alerts**: Create goal, add expenses exceeding 80%, verify alert triggers
5. **Data migration**: Test `migrar_json_para_mysql.py` with sample JSON file
6. **Both backends**: Run identical operations in JSON and MySQL versions - verify consistency

## Common Pitfalls

1. **MySQL not running**: `main_avancado.py` will crash if MySQL is not running. Always check connection in `__init__` of `ControleFinanceiroAvancado`
2. **Path issues in scripts**: Scripts in `scripts/` must add parent directory to `sys.path` to import `src.*`
3. **Date format**: System expects `DD/MM/YYYY` format. Validation in `validar_data()` helper
4. **Decimal precision**: All monetary values use `DECIMAL(15,2)` in MySQL. Convert with `float()` when needed
5. **Connection pooling**: `DatabaseConnection` uses a singleton pool. Don't create multiple instances
6. **JSON file corruption**: The `dados_financeiros_avancado.json` can become corrupted if program crashes during write. Always keep backups

## Migration from JSON to MySQL

Use the migration script to preserve existing data:

```bash
python migrar_json_para_mysql.py
```

This script:
- Reads `dados_financeiros_avancado.json`
- Creates all accounts in MySQL
- Imports all expenses, income, and budget goals
- Renames JSON file to `backup_json_YYYYMMDD_HHMMSS.json`
- Preserves default account setting

## Security Notes

- Never commit `.env` or [src/db/db_config.py](src/db/db_config.py) with real credentials
- In production, create dedicated MySQL user (not `root`):
  ```sql
  CREATE USER 'cli_gastos'@'localhost' IDENTIFIED BY 'strong_password';
  GRANT ALL PRIVILEGES ON cli_gastos.* TO 'cli_gastos'@'localhost';
  FLUSH PRIVILEGES;
  ```
- Backup database regularly with `mysqldump`
