# 🔄 Guia Completo de Migração para MySQL

Este guia detalha como migrar seus dados da versão JSON para a versão MySQL do Sistema de Controle de Gastos.

## 📋 Índice

- [Por que migrar para MySQL?](#-por-que-migrar-para-mysql)
- [Pré-requisitos](#-pré-requisitos)
- [Preparação](#-preparação)
- [Processo de Migração](#-processo-de-migração)
- [Verificação da Migração](#-verificação-da-migração)
- [Solução de Problemas](#-solução-de-problemas)
- [Rollback (Reverter)](#-rollback-reverter)

## 🎯 Por que migrar para MySQL?

### Vantagens do MySQL sobre JSON

| Característica | JSON | MySQL |
|----------------|------|-------|
| **Performance** | Lenta com muitos dados | Rápida com índices |
| **Integridade** | Sem validação | Constraints e foreign keys |
| **Consultas** | Carrega tudo na memória | Queries otimizadas |
| **Backup** | Arquivo único | Ferramentas profissionais |
| **Concorrência** | Um usuário por vez | Múltiplos usuários |
| **Escalabilidade** | Limitada | Milhões de registros |
| **Automação** | Manual | Triggers e procedures |

### Quando migrar?

✅ **Migre se:**
- Você tem muitos registros (> 1000 transações)
- Quer relatórios mais rápidos
- Precisa de backup profissional
- Quer integridade de dados garantida
- Planeja usar em produção

❌ **Não migre se:**
- Você está apenas testando
- Tem poucos dados
- Não quer instalar MySQL
- Prefere simplicidade

## 🔧 Pré-requisitos

### 1. Verifique suas Dependências

```bash
# Verifique se Python está instalado
python --version
# Deve mostrar: Python 3.6 ou superior

# Verifique se pip está funcionando
pip --version
```

### 2. Instale o MySQL

#### Windows

1. **Baixe o instalador:**
   - Acesse [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
   - Baixe "MySQL Installer for Windows"
   - Escolha a versão "mysql-installer-community"

2. **Execute o instalador:**
   - Escolha "Developer Default" ou "Server only"
   - Configure uma senha forte para o usuário `root`
   - **ANOTE ESTA SENHA!** Você precisará dela

3. **Verifique a instalação:**
   ```cmd
   mysql --version
   ```

4. **Inicie o serviço:**
   ```cmd
   net start MySQL
   ```

#### Linux (Ubuntu/Debian)

```bash
# Atualize os pacotes
sudo apt update

# Instale o MySQL
sudo apt install mysql-server

# Inicie o serviço
sudo systemctl start mysql
sudo systemctl enable mysql

# Configure a segurança
sudo mysql_secure_installation
```

#### MacOS

```bash
# Instale via Homebrew
brew install mysql

# Inicie o serviço
brew services start mysql

# Configure a senha do root
mysql_secure_installation
```

### 3. Teste a Conexão MySQL

```bash
# Entre no MySQL
mysql -u root -p
# Digite sua senha quando solicitado

# Dentro do MySQL, teste:
SHOW DATABASES;
EXIT;
```

Se você conseguiu entrar e ver os databases, está tudo OK! ✅

## 📦 Preparação

### 1. Backup Completo

**⚠️ IMPORTANTE:** Sempre faça backup antes de migrar!

```bash
# No diretório do projeto
# Windows
copy dados_financeiros_avancado.json backup_antes_migracao.json

# Linux/Mac
cp dados_financeiros_avancado.json backup_antes_migracao.json
```

### 2. Instale as Dependências Python

```bash
# Certifique-se de estar no diretório do projeto
cd cli_sistema_gastos

# Instale todas as dependências
pip install -r requirements.txt

# Verifique se mysql-connector-python foi instalado
pip show mysql-connector-python
```

### 3. Configure as Credenciais

**Método 1: Arquivo .env (Recomendado)**

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=SUA_SENHA_AQUI
DB_NAME=cli_gastos
```

**⚠️ Substitua `SUA_SENHA_AQUI` pela senha que você definiu na instalação do MySQL!**

**Método 2: Editar db_config.py**

Abra o arquivo `src/db/db_config.py` e edite:

```python
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'SUA_SENHA_AQUI',  # ← MUDE AQUI
    'database': 'cli_gastos',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 4. Verifique seu Arquivo JSON

```bash
# Verifique se o arquivo existe
# Windows
dir dados_financeiros_avancado.json

# Linux/Mac
ls -lh dados_financeiros_avancado.json
```

Se o arquivo não existir, você não tem dados para migrar. Pule para a seção de "Configurar MySQL do Zero".

## 🚀 Processo de Migração

### Passo 1: Inicializar o Banco de Dados

```bash
python init_database.py
```

**O que este script faz:**
- ✅ Cria o database `cli_gastos`
- ✅ Cria as tabelas (contas_bancarias, despesas, receitas, etc.)
- ✅ Cria views para consultas otimizadas
- ✅ Cria triggers para automação
- ✅ Cria stored procedures
- ✅ Insere dados iniciais (Carteira e Conta Principal)

**Saída esperada:**
```
=============================================================
  🗄️  INICIALIZADOR DO BANCO DE DADOS MYSQL
=============================================================

✅ Conectado ao MySQL com sucesso!
✅ Database 'cli_gastos' criado com sucesso!
✅ Tabela 'contas_bancarias' criada com sucesso!
✅ Tabela 'historico_saldo' criada com sucesso!
...
✅ Conta 'Carteira' criada com sucesso!
✅ Conta 'Conta Principal' criada com sucesso!

=============================================================
  ✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!
=============================================================
```

Se houver erros, veja a seção [Solução de Problemas](#-solução-de-problemas).

### Passo 2: Executar a Migração

```bash
python migrar_json_para_mysql.py
```

**O que este script faz:**

1. ✅ Lê o arquivo `dados_financeiros_avancado.json`
2. ✅ Valida os dados
3. ✅ Cria todas as contas bancárias no MySQL
4. ✅ Migra todas as despesas (preservando mês/ano)
5. ✅ Migra todas as receitas
6. ✅ Migra as metas de gastos
7. ✅ Configura a conta padrão
8. ✅ Renomeia o JSON original para backup

**Saída esperada:**
```
📖 Lendo dados do JSON...

🏦 Migrando contas bancárias...
   ✅ Conta 'Banco do Brasil' criada
   ✅ Conta 'Nubank' criada
   ⚠️  Conta 'Carteira' já existe

💸 Migrando despesas...
   ✅ 45 despesas migradas

💰 Migrando receitas...
   ✅ 12 receitas migradas

🎯 Migrando metas de gastos...
   ✅ 5 metas migradas

⚙️  Conta padrão configurada: Banco do Brasil

============================================================
  ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!
============================================================

📊 Resumo:
   • Contas bancárias: 4
   • Despesas: 45
   • Receitas: 12
   • Metas: 5

💾 JSON original salvo como backup: backup_json_20241107_142530.json
```

### Passo 3: Primeiro Teste

```bash
python main_avancado.py
```

Você deve ver o menu principal. Teste algumas operações:

1. **Listar Contas** (Menu 1 → Opção 2)
   - Verifique se todas as suas contas aparecem
   - Confira se os saldos estão corretos

2. **Listar Despesas** (Menu 2 → Opção 2)
   - Verifique se todas as despesas foram migradas
   - Confira valores e categorias

3. **Listar Receitas** (Menu 3 → Opção 3)
   - Verifique se as receitas estão corretas

## ✅ Verificação da Migração

### Verificação via Sistema

Execute cada verificação e compare com seus dados anteriores:

```bash
python main_avancado.py
```

**Checklist de Verificação:**

- [ ] Todas as contas bancárias foram migradas?
- [ ] Os saldos das contas estão corretos?
- [ ] Todas as despesas aparecem?
- [ ] As categorias das despesas estão corretas?
- [ ] As receitas foram migradas?
- [ ] As metas de gastos estão configuradas?
- [ ] A conta padrão está correta?

### Verificação via MySQL

Se você conhece SQL, pode verificar diretamente:

```bash
mysql -u root -p cli_gastos
```

```sql
-- Ver todas as contas
SELECT * FROM contas_bancarias;

-- Contar despesas
SELECT COUNT(*) as total_despesas FROM despesas;

-- Contar receitas
SELECT COUNT(*) as total_receitas FROM receitas;

-- Ver metas
SELECT * FROM metas_gastos;

-- Sair
EXIT;
```

### Comparação de Dados

Compare os totais antes e depois:

**Antes (JSON):**
- Abra `backup_antes_migracao.json` em um editor
- Conte manualmente ou use um contador JSON online

**Depois (MySQL):**
- Use as queries acima
- Os números devem bater exatamente

## 🐛 Solução de Problemas

### Erro: "Access denied for user 'root'@'localhost'"

**Causa:** Senha incorreta no `.env` ou `db_config.py`

**Solução:**
1. Verifique a senha no arquivo de configuração
2. Teste a conexão manualmente:
   ```bash
   mysql -u root -p
   ```
3. Se não conseguir conectar, resete a senha do MySQL

**Resetar senha do MySQL (Windows):**
```cmd
net stop MySQL
mysqld --skip-grant-tables
mysql -u root
USE mysql;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'nova_senha';
FLUSH PRIVILEGES;
EXIT;
net start MySQL
```

### Erro: "Unknown database 'cli_gastos'"

**Causa:** O database não foi criado

**Solução:**
```bash
# Execute o inicializador novamente
python init_database.py
```

### Erro: "Can't connect to MySQL server"

**Causa:** MySQL não está rodando

**Solução:**
```bash
# Windows
net start MySQL

# Linux
sudo systemctl start mysql

# MacOS
brew services start mysql
```

### Erro: "Duplicate entry 'Carteira' for key 'nome'"

**Causa:** As contas padrão já existem no banco

**Solução:** Isso é normal! O script de migração pula contas que já existem. A mensagem "⚠️ Conta 'X' já existe" é esperada.

### Erro: "File not found: dados_financeiros_avancado.json"

**Causa:** Você não tem dados na versão JSON

**Solução:**
- Se você está começando do zero, apenas use `python main_avancado.py`
- O sistema criará as contas padrão automaticamente
- Não precisa migrar nada

### Migração Parcial

**Sintoma:** Algumas despesas não foram migradas

**Diagnóstico:**
```bash
# Compare os números
python -c "import json; data=json.load(open('backup_antes_migracao.json')); print(f'Despesas no JSON: {sum(len(d) for d in data.get(\"despesas\", {}).values())}')"

mysql -u root -p -e "USE cli_gastos; SELECT COUNT(*) FROM despesas;"
```

**Solução:**
1. Verifique os erros na saída do script de migração
2. Corrija os dados no JSON (formato de data, valores inválidos)
3. Execute a migração novamente

### Dados Corrompidos no JSON

**Sintoma:** Erros de parsing JSON

**Solução:**
1. Use um validador JSON online (jsonlint.com)
2. Corrija os erros de sintaxe
3. Execute a migração novamente

## 🔙 Rollback (Reverter)

Se algo der errado e você quiser voltar para o JSON:

### 1. Restaurar o Backup

```bash
# Windows
copy backup_antes_migracao.json dados_financeiros_avancado.json

# Linux/Mac
cp backup_antes_migracao.json dados_financeiros_avancado.json
```

### 2. Usar a Versão JSON

```bash
python main.py
```

### 3. (Opcional) Limpar o MySQL

Se você quiser recomeçar do zero:

```sql
mysql -u root -p

DROP DATABASE cli_gastos;
EXIT;
```

Depois rode `python init_database.py` novamente.

## 📊 Estrutura do Banco de Dados

### Tabelas Criadas

| Tabela | Descrição | Colunas Principais |
|--------|-----------|-------------------|
| `contas_bancarias` | Contas e carteira | id, nome, banco, saldo_atual |
| `historico_saldo` | Movimentações | conta_id, saldo_anterior, saldo_novo, operacao |
| `despesas` | Despesas | descricao, valor, categoria, data_vencimento, pago |
| `receitas` | Receitas | descricao, valor, categoria, data_recebimento |
| `metas_gastos` | Metas por categoria | categoria, limite_mensal, mes, ano |
| `configuracoes` | Configurações | chave, valor |

### Relacionamentos

```
contas_bancarias (1) ←→ (N) historico_saldo
contas_bancarias (1) ←→ (N) despesas
contas_bancarias (1) ←→ (N) receitas
```

### Índices Criados

- `idx_nome` em contas_bancarias
- `idx_mes_ano` em despesas
- `idx_categoria` em despesas
- `idx_pago` em despesas
- `idx_data_vencimento` em despesas
- `idx_conta_data` em historico_saldo

Estes índices tornam as consultas muito mais rápidas! 🚀

## 🎯 Próximos Passos

Depois de migrar com sucesso:

1. **Use a versão MySQL:**
   ```bash
   python main_avancado.py
   ```

2. **Configure backups automáticos:**
   ```bash
   # Criar script de backup (backup.bat no Windows)
   mysqldump -u root -p cli_gastos > backup_diario.sql
   ```

3. **Explore as novas funcionalidades:**
   - Relatórios mais rápidos
   - Consultas complexas
   - Integridade referencial

4. **Delete os arquivos JSON antigos** (depois de confirmar que está tudo OK):
   ```bash
   # Mantenha um backup em local seguro!
   # Não delete ainda se não tiver certeza
   ```

## 📚 Recursos Adicionais

- [Documentação MySQL](https://dev.mysql.com/doc/)
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
- [README do Projeto](README.md)
- [CLAUDE.md](CLAUDE.md) - Documentação técnica

## 🆘 Ajuda

Se você encontrou problemas que não estão documentados aqui:

1. Verifique os logs de erro completos
2. Abra uma [Issue no GitHub](https://github.com/seu-usuario/cli_sistema_gastos/issues)
3. Inclua:
   - Versão do Python (`python --version`)
   - Versão do MySQL (`mysql --version`)
   - Sistema operacional
   - Mensagem de erro completa
   - Passos que você seguiu

---

**💡 Dica Final:** Depois de migrar com sucesso, faça backups regulares do MySQL usando `mysqldump`. Seus dados financeiros são importantes!

**Boa migração! 🚀**
