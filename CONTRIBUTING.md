# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o Sistema de Controle de Gastos CLI! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Como Contribuir

### 1. Reporte Bugs

Encontrou um bug? Ajude-nos a melhorar!

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/seu-usuario/cli_sistema_gastos/issues)
2. Abra uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Screenshots (se aplicável)
   - Versão do Python e sistema operacional

### 2. Sugira Melhorias

Tem uma ideia para melhorar o sistema?

1. Abra uma issue com a tag `enhancement`
2. Descreva sua sugestão detalhadamente
3. Explique o benefício para os usuários

### 3. Contribua com Código

#### Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/cli_sistema_gastos.git
cd cli_sistema_gastos

# Configure o repositório original como upstream
git remote add upstream https://github.com/usuario-original/cli_sistema_gastos.git
```

#### Configuração do Ambiente

```bash
# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

#### Crie uma Branch

```bash
# Sempre crie uma branch a partir da main
git checkout -b feature/minha-feature

# Ou para correções
git checkout -b fix/correcao-bug
```

#### Desenvolva

1. **Mantenha compatibilidade**: Suas mudanças devem funcionar tanto na versão JSON quanto MySQL
2. **Siga o estilo**: Use o estilo de código existente
3. **Comente**: Adicione comentários em código complexo
4. **Teste**: Teste suas mudanças em ambas versões (JSON e MySQL)

#### Commit

```bash
# Faça commits com mensagens claras
git add .
git commit -m "feat: adiciona funcionalidade X"

# Ou para correções
git commit -m "fix: corrige problema Y"
```

**Padrão de mensagens de commit:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação
- `refactor:` - Refatoração de código
- `test:` - Testes
- `chore:` - Tarefas de manutenção

#### Push e Pull Request

```bash
# Envie suas mudanças
git push origin feature/minha-feature
```

No GitHub:
1. Abra um Pull Request
2. Preencha o template com detalhes da mudança
3. Aguarde o review

## 🎯 Áreas que Precisam de Ajuda

- 📝 Melhorias na documentação
- 🐛 Correção de bugs reportados
- 🧪 Adicionar testes automatizados
- 🌐 Internacionalização (i18n)
- 🎨 Melhorias na interface CLI
- 📊 Novos tipos de relatórios
- 🔒 Melhorias de segurança

## 📝 Estilo de Código

### Python

- Use 4 espaços para indentação
- Siga a PEP 8
- Docstrings para classes e funções públicas
- Type hints quando possível

```python
def adicionar_despesa(self, descricao: str, valor: float, categoria: str) -> bool:
    """
    Adiciona uma nova despesa ao sistema.

    Args:
        descricao: Descrição da despesa
        valor: Valor em reais
        categoria: Categoria da despesa

    Returns:
        True se adicionada com sucesso, False caso contrário
    """
    # Implementação
```

### SQL

- Use UPPERCASE para palavras-chave SQL
- Indente subconsultas
- Adicione comentários em queries complexas

```sql
-- Buscar despesas do mês
SELECT d.*, c.nome as conta_nome
FROM despesas d
LEFT JOIN contas_bancarias c ON d.conta_id = c.id
WHERE d.mes = %s AND d.ano = %s
ORDER BY d.data_vencimento;
```

## 🧪 Testes

Antes de submeter um PR, teste:

### Teste Manual

1. **Versão JSON:**
   ```bash
   python main.py
   ```
   - Teste todas as operações CRUD
   - Verifique se dados são salvos corretamente

2. **Versão MySQL:**
   ```bash
   python main_avancado.py
   ```
   - Teste todas as operações CRUD
   - Verifique integridade referencial
   - Teste triggers e views

3. **Migração:**
   ```bash
   python migrar_json_para_mysql.py
   ```
   - Verifique se todos os dados são migrados

### Checklist de Testes

- [ ] Criar conta bancária
- [ ] Adicionar despesa
- [ ] Adicionar receita
- [ ] Pagar despesa (verifica saldo)
- [ ] Processar receita (verifica saldo)
- [ ] Criar meta de gastos
- [ ] Gerar relatório mensal
- [ ] Exportar para Excel/PDF
- [ ] Transferir entre contas
- [ ] Migração JSON → MySQL

## 📚 Estrutura do Código

### Adicionar Nova Funcionalidade

1. **Versão JSON** ([src/controllers/controle_avancado.py](src/controllers/controle_avancado.py)):
   ```python
   def minha_funcao(self):
       # Implementação com JSON
       self.salvar_dados()
   ```

2. **Versão MySQL** ([src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py)):
   ```python
   def minha_funcao(self):
       # Implementação com MySQL
       query = "INSERT INTO ..."
       self.db.execute_query(query, params)
   ```

3. **Interface CLI** ([main_avancado.py](main_avancado.py)):
   ```python
   def menu_minha_funcao():
       # Interface do usuário
       controle.minha_funcao()
   ```

### Adicionar Nova Tabela MySQL

1. Edite [src/db/migrations.sql](src/db/migrations.sql):
   ```sql
   CREATE TABLE IF NOT EXISTS minha_tabela (
       id INT AUTO_INCREMENT PRIMARY KEY,
       -- colunas
   );
   ```

2. Adicione métodos em [src/db/db_connection.py](src/db/db_connection.py):
   ```python
   def criar_minha_entidade(self, ...):
       query = "INSERT INTO minha_tabela ..."
       return self.execute_query(query, ...)
   ```

3. Use em [src/controllers/controle_avancado_mysql.py](src/controllers/controle_avancado_mysql.py)

## 🚫 O que NÃO fazer

- ❌ Não commite o arquivo `.env` com credenciais reais
- ❌ Não commite arquivos `__pycache__` ou `.pyc`
- ❌ Não commite dados pessoais (JSON com suas finanças)
- ❌ Não quebre compatibilidade sem discussão prévia
- ❌ Não adicione dependências pesadas sem necessidade
- ❌ Não faça mudanças que funcionam apenas em um OS

## 📄 Documentação

Ao adicionar funcionalidades, atualize:

- [ ] [README.md](README.md) - Se afeta o uso básico
- [ ] [CLAUDE.md](CLAUDE.md) - Se afeta a arquitetura
- [ ] [MIGRACAO_MYSQL.md](MIGRACAO_MYSQL.md) - Se afeta migração
- [ ] Comentários no código
- [ ] Docstrings das funções

## 🔍 Code Review

Seu PR será revisado quanto a:

- ✅ Funcionalidade correta
- ✅ Compatibilidade (JSON e MySQL)
- ✅ Qualidade do código
- ✅ Documentação adequada
- ✅ Sem quebra de features existentes

## ❓ Dúvidas?

- Abra uma [Issue](https://github.com/seu-usuario/cli_sistema_gastos/issues) com a tag `question`
- Entre em contato via email: seu-email@exemplo.com

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

**Obrigado por contribuir! 🎉**
