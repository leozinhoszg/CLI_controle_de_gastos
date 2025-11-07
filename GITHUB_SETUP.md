# 🚀 Guia de Setup do GitHub

Este documento explica como subir o projeto para o GitHub pela primeira vez.

## 📋 Pré-requisitos

- [ ] Git instalado ([download aqui](https://git-scm.com/downloads))
- [ ] Conta no GitHub ([criar conta](https://github.com/join))
- [ ] Projeto organizado e limpo

## 🔧 Passo 1: Configurar Git Local

### Primeira vez usando Git?

```bash
# Configure seu nome (aparecerá nos commits)
git config --global user.name "Seu Nome"

# Configure seu email (use o mesmo do GitHub)
git config --global user.email "seu-email@exemplo.com"

# Verifique a configuração
git config --list
```

## 📦 Passo 2: Inicializar Repositório Local

```bash
# Entre no diretório do projeto
cd "c:\Users\lguimaraes\Documents\PROJETOS\PROJETOS\FACU\controle de gastos\cli_sistema_gastos"

# Inicialize o repositório Git
git init

# Verifique o status (deve mostrar arquivos não rastreados)
git status
```

## 🔍 Passo 3: Verificar .gitignore

Certifique-se de que o `.gitignore` está funcionando:

```bash
# Liste arquivos que serão ignorados
git status --ignored

# Arquivos que DEVEM estar ignorados:
# - .env (credenciais)
# - __pycache__/
# - *.pyc
# - docs/
# - build/
# - dist/
# - dados_financeiros*.json
```

## 📝 Passo 4: Primeiro Commit

```bash
# Adicione todos os arquivos (exceto os ignorados)
git add .

# Verifique o que será commitado
git status

# Faça o primeiro commit
git commit -m "Initial commit: Sistema de Controle de Gastos CLI"
```

## 🌐 Passo 5: Criar Repositório no GitHub

### Via Interface Web:

1. Acesse [github.com](https://github.com)
2. Clique em **"New repository"** (botão verde no canto superior direito)
3. Preencha:
   - **Repository name:** `cli-sistema-gastos`
   - **Description:** `Sistema completo em Python para controle de gastos pessoais via CLI com MySQL`
   - **Public** ou **Private** (sua escolha)
   - ❌ **NÃO** marque "Initialize with README" (já temos)
   - ❌ **NÃO** adicione .gitignore (já temos)
   - ❌ **NÃO** adicione license ainda
4. Clique em **"Create repository"**

## 🔗 Passo 6: Conectar Local com GitHub

Após criar o repositório, o GitHub mostrará instruções. Use:

```bash
# Adicione o repositório remoto (substitua SEU-USUARIO)
git remote add origin https://github.com/SEU-USUARIO/cli-sistema-gastos.git

# Verifique se foi adicionado
git remote -v

# Renomeie a branch principal para 'main' (padrão do GitHub)
git branch -M main

# Envie o código para o GitHub
git push -u origin main
```

## ✅ Passo 7: Verificar Upload

1. Acesse seu repositório no GitHub
2. Verifique se os arquivos aparecem
3. Confirme que arquivos sensíveis NÃO foram enviados:
   - `.env` não deve aparecer ✅
   - `docs/` não deve aparecer ✅
   - Arquivos JSON pessoais não devem aparecer ✅

## 🎨 Passo 8: Melhorar Aparência (Opcional)

### Adicionar Tópicos

No GitHub, clique em ⚙️ Settings (do lado direito) → Topics:
- `python`
- `finance`
- `cli`
- `mysql`
- `personal-finance`
- `expense-tracker`

### Adicionar Licença

```bash
# Crie arquivo LICENSE na raiz
# Copie o texto da MIT License de: https://choosealicense.com/licenses/mit/

git add LICENSE
git commit -m "docs: adiciona licença MIT"
git push
```

### Configurar GitHub Pages (se quiser site de documentação)

1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main, pasta /docs (se mover README para docs)

## 📊 Passo 9: Adicionar Badges (Opcional)

Edite o [README.md](README.md) e adicione no topo:

```markdown
# 💰 Sistema de Controle de Gastos CLI

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![MySQL](https://img.shields.io/badge/mysql-5.7%2B-orange)
![Status](https://img.shields.io/badge/status-active-success)

Um sistema completo em Python para gerenciar suas finanças pessoais...
```

Commit e push:
```bash
git add README.md
git commit -m "docs: adiciona badges ao README"
git push
```

## 🔄 Comandos Git para Uso Diário

### Fazer Mudanças

```bash
# 1. Veja o que mudou
git status

# 2. Adicione os arquivos modificados
git add .
# Ou arquivos específicos:
git add arquivo1.py arquivo2.py

# 3. Commit com mensagem descritiva
git commit -m "feat: adiciona funcionalidade X"

# 4. Envie para o GitHub
git push
```

### Antes de Fazer Mudanças

```bash
# Sempre puxe as últimas mudanças antes de trabalhar
git pull
```

### Ver Histórico

```bash
# Ver commits
git log --oneline

# Ver mudanças de um arquivo
git log -p arquivo.py
```

### Desfazer Mudanças (Cuidado!)

```bash
# Descartar mudanças não commitadas
git checkout -- arquivo.py

# Voltar último commit (mantém mudanças)
git reset HEAD~1

# CUIDADO: Apagar último commit (perde mudanças!)
git reset --hard HEAD~1
```

## 🛡️ Segurança: Checklist Final

Antes de tornar o repositório público:

- [ ] `.env` está no `.gitignore`
- [ ] `.env` NÃO foi commitado
- [ ] Senha do MySQL não está em código
- [ ] Arquivos JSON pessoais não foram enviados
- [ ] Dados sensíveis foram removidos

### Verificar se .env foi commitado acidentalmente:

```bash
# Se .env aparecer no histórico:
git log --all --full-history -- .env

# Se aparecer, remova do histórico:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (CUIDADO!)
git push origin --force --all
```

## 📱 Configurar Notifications

No GitHub, vá em Settings → Notifications e configure:
- Issues abertas no seu repositório
- Pull requests
- Menções

## 🤝 Colaboração

### Se outras pessoas forem contribuir:

1. **Proteja a branch main:**
   - Settings → Branches → Add rule
   - Branch name pattern: `main`
   - ✅ Require pull request before merging

2. **Configure templates:**
   ```bash
   # Crie pasta
   mkdir .github

   # Templates de issue/PR (opcional)
   # Ver exemplos em: https://github.com/stevemao/github-issue-templates
   ```

3. **Adicione CONTRIBUTING.md** (já criado ✅)

## 📞 Problemas Comuns

### "Permission denied (publickey)"

**Solução:** Configure SSH ou use HTTPS com token

```bash
# Mudando para HTTPS
git remote set-url origin https://github.com/SEU-USUARIO/cli-sistema-gastos.git
```

### "Updates were rejected"

```bash
# Puxe primeiro
git pull --rebase
git push
```

### "Merge conflict"

```bash
# Veja os conflitos
git status

# Edite os arquivos marcados
# Remova as marcações <<< === >>>

# Adicione e commit
git add .
git commit -m "fix: resolve conflitos"
git push
```

## 📚 Recursos Adicionais

- [GitHub Docs](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## ✨ Próximos Passos

Depois de subir no GitHub:

1. [ ] Compartilhe o link do repositório
2. [ ] Adicione colaboradores (Settings → Collaborators)
3. [ ] Configure GitHub Actions para CI/CD (opcional)
4. [ ] Crie releases (quando tiver versões estáveis)
5. [ ] Considere GitHub Sponsors (se quiser doações)

---

**🎉 Parabéns! Seu projeto está no GitHub!**

Repositório exemplo: `https://github.com/SEU-USUARIO/cli-sistema-gastos`
