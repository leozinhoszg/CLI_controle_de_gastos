"""
Configuração de conexão com o banco de dados MySQL
"""
import os

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Jae66yrr@'),
    'database': os.getenv('DB_NAME', 'cli_gastos'),
    'charset': 'utf8mb4',
    'autocommit': True
}

# Criar arquivo .env de exemplo se não existir
ENV_EXAMPLE = """# Configurações do Banco de Dados MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Jae66yrr@
DB_NAME=cli_gastos
"""

if not os.path.exists('.env'):
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(ENV_EXAMPLE)
    print("ℹ️  Arquivo .env.example criado. Configure suas credenciais do MySQL!")

