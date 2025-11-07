# 💰 Sistema de Controle de Gastos CLI

Um sistema completo em Python para gerenciar suas finanças pessoais via linha de comando, com suporte para múltiplas contas bancárias, carteira digital, metas de gastos, gráficos e relatórios.

## 📋 Índice

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração do Banco de Dados](#-configuração-do-banco-de-dados)
- [Como Usar](#-como-usar)
- [Migração de Dados](#-migração-de-dados)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Contribuindo](#-contribuindo)

## ✨ Características

### 🏦 Gestão Financeira Completa
- **Múltiplas Contas Bancárias**: Crie e gerencie várias contas
- **Carteira Digital**: Controle dinheiro em espécie separadamente
- **Saldo Dinâmico**: Atualização automática de saldos
- **Histórico Completo**: Rastreie todas as movimentações

### 💸 Despesas e Receitas
- Adicionar, editar e remover despesas
- Gerenciar receitas de múltiplas fontes
- Categorização por tipo (moradia, alimentação, transporte, etc.)
- Marcação de status (pago/pendente)
- Alertas de vencimento

### 🎯 Metas e Planejamento
- Definir metas de gastos por categoria
- Alertas quando atingir 80% da meta
- Acompanhamento mensal de gastos
- Comparativos entre períodos

### 📊 Relatórios e Visualizações
- Gráficos de gastos por categoria
- Comparativos mensais e anuais
- Exportação para Excel e PDF
- Análises detalhadas por período

### 🔄 Dual Storage
- **Versão JSON**: Simples, sem banco de dados
- **Versão MySQL**: Profissional, com integridade referencial

## 🔧 Requisitos

### Requisitos Mínimos
- Python 3.6 ou superior
- pip (gerenciador de pacotes Python)

### Para Versão MySQL (Recomendado)
- MySQL Server 5.7 ou superior
- Acesso root ou usuário com privilégios para criar databases

## 📥 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/cli_sistema_gastos.git
cd cli_sistema_gastos
```

### 2. Crie um Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

As dependências incluem:
- `mysql-connector-python` - Conexão com MySQL
- `matplotlib` - Gráficos e visualizações
- `pandas` - Análise de dados
- `openpyxl` - Exportação Excel
- `reportlab` - Geração de PDFs
- `numpy` - Cálculos numéricos

## 🗄️ Configuração do Banco de Dados

### Opção 1: Usar Versão JSON (Sem Banco de Dados)

Se você quer começar rapidamente sem configurar MySQL:

```bash
python main.py
```

Os dados serão salvos em `dados_financeiros.json`.

### Opção 2: Usar Versão MySQL (Recomendado)

#### Passo 1: Instalar MySQL

**Windows:**
- Baixe o instalador em [mysql.com/downloads](https://dev.mysql.com/downloads/installer/)
- Execute o instalador e escolha "MySQL Server"
- Durante a instalação, defina uma senha para o usuário `root`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**MacOS:**
```bash
brew install mysql
brew services start mysql
```

#### Passo 2: Configurar Credenciais

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=cli_gastos
```

**⚠️ IMPORTANTE:**
- O arquivo `.env` está no `.gitignore` e não será commitado
- Nunca compartilhe suas credenciais de banco de dados
- Use uma senha forte para o MySQL

Alternativamente, você pode editar diretamente o arquivo [src/db/db_config.py](src/db/db_config.py):

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'sua_senha',  # ← Altere aqui
    'database': 'cli_gastos',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

#### Passo 3: Inicializar o Banco de Dados

Execute o script de inicialização para criar o schema e as tabelas:

```bash
python init_database.py
```

Este script irá:
- ✅ Criar o database `cli_gastos`
- ✅ Criar 6 tabelas (contas, despesas, receitas, metas, histórico, configurações)
- ✅ Criar 6 views para consultas otimizadas
- ✅ Criar triggers para automação
- ✅ Criar stored procedures
- ✅ Inserir dados iniciais (Carteira e Conta Principal)

#### Passo 4: Verificar Conexão

Teste se tudo está funcionando:

```bash
python main_avancado.py
```

Se aparecer o menu principal, a configuração foi bem-sucedida! 🎉

## 🚀 Como Usar

### Versão Básica (JSON)

```bash
python main.py
```

### Versão Avançada (MySQL)

```bash
python main_avancado.py
```

### Menu Principal

Ao executar o sistema, você verá:

```
======================================================================
        💰 SISTEMA AVANÇADO DE CONTROLE DE GASTOS 💰
======================================================================

📋 MENU PRINCIPAL:
1️⃣  - Gerenciar Contas Bancárias
2️⃣  - Gerenciar Despesas
3️⃣  - Gerenciar Receitas
4️⃣  - Metas de Gastos
5️⃣  - Busca e Filtros
6️⃣  - Relatórios e Gráficos
7️⃣  - Alertas e Notificações
8️⃣  - Exportar Dados
9️⃣  - Limpar Dados
0️⃣  - Sair
```

### Primeiros Passos

1. **Configure suas contas** (Menu 1)
   - O sistema já cria uma "Conta Principal" e "Carteira" automaticamente
   - Adicione suas contas bancárias reais (Banco do Brasil, Nubank, etc.)
   - Defina os saldos iniciais

2. **Registre suas receitas** (Menu 3)
   - Adicione seu salário, freelances, etc.
   - O sistema credita automaticamente na conta escolhida

3. **Cadastre suas despesas** (Menu 2)
   - Adicione todas as suas despesas mensais
   - Defina datas de vencimento
   - Categorize (Moradia, Alimentação, Transporte, etc.)

4. **Defina metas** (Menu 4)
   - Estabeleça limites de gastos por categoria
   - Receba alertas quando atingir 80% da meta

5. **Acompanhe suas finanças** (Menu 6)
   - Visualize relatórios mensais
   - Gere gráficos de gastos
   - Compare períodos diferentes

### Formato de Datas

Todas as datas devem ser inseridas no formato: **DD/MM/AAAA**

Exemplos válidos:
- `15/11/2024`
- `01/12/2024`
- `25/12/2024`

## 🔄 Migração de Dados

Se você já usava a versão JSON e quer migrar para MySQL:

### Passo 1: Backup (Opcional mas Recomendado)

```bash
# Faça uma cópia do seu arquivo JSON
cp dados_financeiros_avancado.json backup_seguranca.json
```

### Passo 2: Configure o MySQL

Siga os passos da seção [Configuração do Banco de Dados](#-configuração-do-banco-de-dados).

### Passo 3: Execute o Script de Migração

```bash
python migrar_json_para_mysql.py
```

O script irá:

1. ✅ Ler o arquivo `dados_financeiros_avancado.json`
2. ✅ Criar todas as contas bancárias no MySQL
3. ✅ Migrar todas as despesas mantendo histórico
4. ✅ Migrar todas as receitas
5. ✅ Migrar as metas de gastos
6. ✅ Preservar configurações (conta padrão)
7. ✅ Renomear o JSON original para `backup_json_AAAAMMDD_HHMMSS.json`

### Passo 4: Verificar Migração

```bash
# Execute o sistema MySQL
python main_avancado.py

# Verifique se todos os dados foram migrados:
# - Menu 1 → Opção 2: Listar Contas
# - Menu 2 → Opção 2: Listar Despesas
# - Menu 3 → Opção 3: Listar Receitas
```

### O que fazer se algo der errado?

Se a migração falhar:

1. Restaure o backup:
   ```bash
   cp backup_seguranca.json dados_financeiros_avancado.json
   ```

2. Verifique os logs de erro exibidos

3. Problemas comuns:
   - **"Access denied"**: Credenciais incorretas no `.env`
   - **"Unknown database"**: Execute `python init_database.py` primeiro
   - **"Connection refused"**: MySQL não está rodando

## 📁 Estrutura do Projeto

```
cli_sistema_gastos/
├── src/                           # Código fonte
│   ├── controllers/               # Lógica de negócio
│   │   ├── controle_gastos.py            # Classes base
│   │   ├── controle_avancado.py          # Versão JSON
│   │   └── controle_avancado_mysql.py    # Versão MySQL
│   ├── db/                        # Camada de banco de dados
│   │   ├── db_config.py                  # Configurações MySQL
│   │   ├── db_connection.py              # Pool de conexões
│   │   └── migrations.sql                # Schema SQL completo
│   └── utils/                     # Utilitários
│       └── exportador.py                 # Exportação Excel/PDF
├── main.py                        # CLI versão JSON
├── main_avancado.py               # CLI versão MySQL
├── init_database.py               # Script de inicialização do banco
├── migrar_json_para_mysql.py      # Script de migração
├── requirements.txt               # Dependências Python
├── CLAUDE.md                      # Guia para Claude Code
├── README.md                      # Este arquivo
├── .gitignore                     # Arquivos ignorados pelo Git
├── .env                           # Credenciais (não commitado)
└── build_exe_mysql.spec           # Config PyInstaller
```

### Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| [main_avancado.py](main_avancado.py) | Interface CLI principal (MySQL) |
| [init_database.py](init_database.py) | Inicializa banco de dados MySQL |
| [migrar_json_para_mysql.py](migrar_json_para_mysql.py) | Migra dados JSON → MySQL |
| [src/db/migrations.sql](src/db/migrations.sql) | Schema completo do banco |
| [src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py) | Lógica de negócio MySQL |
| [CLAUDE.md](CLAUDE.md) | Documentação técnica do projeto |

## 🐛 Solução de Problemas

### MySQL não conecta

**Erro:** `Can't connect to MySQL server`

**Solução:**
```bash
# Windows
net start MySQL

# Linux
sudo systemctl start mysql

# Verificar status
# Windows: services.msc
# Linux: sudo systemctl status mysql
```

### Credenciais incorretas

**Erro:** `Access denied for user 'root'@'localhost'`

**Solução:**
1. Verifique o arquivo `.env` ou `src/db/db_config.py`
2. Teste no terminal:
   ```bash
   mysql -u root -p
   # Digite a senha e veja se conecta
   ```

### Database não existe

**Erro:** `Unknown database 'cli_gastos'`

**Solução:**
```bash
python init_database.py
```

### Erro ao importar módulos

**Erro:** `ModuleNotFoundError: No module named 'mysql'`

**Solução:**
```bash
pip install -r requirements.txt
```

### Gráficos não são gerados

**Erro:** Gráficos não aparecem ou dão erro

**Solução:**
```bash
# Instalar dependências de gráficos
pip install matplotlib pandas numpy

# Linux: pode precisar de bibliotecas adicionais
sudo apt-get install python3-tk
```

## 🛠️ Compilando Executável (Opcional)

Se você quer distribuir o sistema sem exigir Python instalado:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar versão MySQL
pyinstaller build_exe_mysql.spec --clean

# Compilar versão JSON
pyinstaller SistemaControleGastos.spec --clean
```

O executável estará em `dist/`.

**Nota:** O executável ainda precisa que o MySQL esteja instalado e configurado no sistema de destino.

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Mantenha compatibilidade com ambas versões (JSON e MySQL)
- Adicione comentários em código complexo
- Teste suas mudanças antes de submeter
- Siga o estilo de código existente
- Atualize a documentação quando necessário

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 📧 Contato

Para dúvidas, sugestões ou reportar problemas:
- Abra uma [Issue](https://github.com/seu-usuario/cli_sistema_gastos/issues)
- Entre em contato via email: seu-email@exemplo.com

---

**Desenvolvido com ❤️ em Python**

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!
