# 🌌 Antigravity Awesome Skills

**Coleção definitiva de 1006+ Skills Agenticos para Assistentes de Código IA**

Compatível com: Claude Code, Gemini CLI, GitHub Copilot, Cursor, e muito mais.

---

## 📚 Índice

- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Bundles Recomendados](#bundles-recomendados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Explorar Skills](#explorar-skills)
- [MCP Integration](#-mcp-model-context-protocol)
- [Scripts de Desenvolvimento](#-scripts-de-desenvolvimento)
- [Documentação Completa](#documentação-completa)
- [Solução de Problemas](#-solução-de-problemas)

---

## 🚀 Instalação

### Opção 1: Instalação Global (Recomendado)

```bash
npx antigravity-awesome-skills
```

Isso instalará as skills em `~/.gemini/antigravity/skills/` por padrão.

### Opção 2: Instalar em Local Customizado

```bash
npx antigravity-awesome-skills --path /seu/caminho/personalizado
```

### Opção 3: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/antigravity-skills.git
cd antigravity-skills
npm install
node bin/install.js
```

---

## 💡 Como Usar

### Passo 1: Entender o Conceito de "Skills"

Skills são arquivos markdown que ensinam ao seu Assistente IA como fazer tarefas específicas. Após a instalação, todas as 1006+ skills estarão disponíveis para seu agente usar.

### Passo 2: Usar uma Skill

Basta pedir naturalemente ao seu Assistente:

```
"Use a skill @brainstorming para me ajudar a planejar um MVP de SaaS"
"Execute @lint-and-validate neste arquivo"
"Crie um teste usando @javascript-testing-patterns"
```

### Passo 3: Escolher um Bundle

Bundles são coleções recomendadas de skills por função/role:

- **Web Wizard**: Para desenvolvedores web e frontend
- **Security Engineer**: Para especialistas em segurança
- **Essentials**: Coleção geral para todos

👉 **Veja a lista completa em**: [docs/BUNDLES.md](docs/BUNDLES.md)

---

## 📦 Bundles Recomendados

### Por Função

| Função | Bundle | Skills |
|--------|--------|--------|
| **Desenvolvedor Web** | Web Wizard | 15+ skills |
| **Especialista em Segurança** | Security Engineer | 12+ skills |
| **Full Stack** | Essentials | 20+ skills |
| **DevOps** | Cloud Master | 18+ skills |
| **Data Science** | Data Maestro | 14+ skills |

👉 Para a lista completa com descrições, veja [BUNDLES.md](docs/BUNDLES.md)

---

## 🗂️ Estrutura do Projeto

```
.
├── skills/                  # 1006+ arquivos de skills
│   ├── [skill-folders]/     # Skills organizadas por categoria
│   └── README.md            # Índice de skills
├── docs/                    # Documentação completa
│   ├── USAGE.md            # Guia detalhado de uso
│   ├── BUNDLES.md          # Coleções recomendadas
│   ├── FAQ.md              # Perguntas frequentes
│   └── GETTING_STARTED.md  # Primeiros passos
├── data/                    # Índices e catálogos
│   ├── catalog.json        # Catálogo de skills
│   ├── bundles.json        # Definição de bundles
│   └── skills_index.json   # Índice completo
├── scripts/                 # Utilitários e scripts
└── web-app/                # Aplicação web para explorar skills
```

---

## 🎯 Casos de Uso

### Exemplo 1: Desenvolvedor Web
```
1. Instalar: npx antigravity-awesome-skills
2. Escolher bundle: "Web Wizard"
3. Usar skills: @react-best-practices, @frontend-design, etc.
```

### Exemplo 2: Especialista em Segurança
```
1. Instalar as skills
2. Usar @sql-injection-testing
3. Usar @security-audit
4. Usar @cc-skill-security-review
```

### Exemplo 3: Full Stack
```
1. Instalar com bundle "Essentials"
2. Explorar skills de backend e frontend
3. Usar @nodejs-best-practices, @database-migrations-sql-migrations
```

---

## 📖 Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| [USAGE.md](docs/USAGE.md) | **Comece aqui!** Guia completo de como usar |
| [MCP_SETUP.md](docs/MCP_SETUP.md) | 🔌 Integração com Claude Desktop via MCP |
| [BUNDLES.md](docs/BUNDLES.md) | Coleções recomendadas por função |
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Primeiros passos |
| [FAQ.md](docs/FAQ.md) | Perguntas frequentes |
| [SKILL_ANATOMY.md](docs/SKILL_ANATOMY.md) | Anatomia de uma skill |
| [CATALOG.md](CATALOG.md) | Catálogo completo de skills |

---

## 🔍 Explorar Skills

### Via Linha de Comando

```bash
# Listar todas as skills
ls skills/

# Procurar por uma skill específica
grep -r "@react" skills/
```

### Via Web App (Experimental)

```bash
cd web-app
npm install
npm run dev
```

Isso abre uma interface web para explorar as skills interativamente.

---

## 🔌 MCP (Model Context Protocol)

Use Antigravity Skills diretamente no **Claude Desktop** e outras ferramentas compatíveis com MCP.

### ⚡ Quick Setup

```bash
# 1. Instalar MCP
pip install mcp

# 2. Adicionar ao Claude Desktop config (~/.config/Claude/claude_desktop_config.json)
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["/caminho/para/antigravity-skills/mcp/skills_mcp.py"],
      "env": {}
    }
  }
}

# 3. Reiniciar Claude Desktop
```

### 💡 Usar no Claude Desktop

Basta conversar naturalmente:

```
"Use a skill de testes para JavaScript"
"Encontre skills relacionadas a React"
"Execute @security-audit neste código"
```

### 📖 Documentação Completa

👉 Veja [docs/MCP_SETUP.md](docs/MCP_SETUP.md) para:
- Instalação detalhada
- Configuração avançada  
- Troubleshooting
- Ambientes customizados

---

## ⚙️ Scripts de Desenvolvimento

Os scripts auxiliam na manutenção, validação e construção do catálogo de skills.

### 📋 Scripts Disponíveis

#### Validação e Qualidade

```bash
# Validar todas as skills
npm run validate

# Modo strict (mais rigoroso)
npm run validate:strict

# Rodar suite de testes
npm run test

# Testes com conexão de rede
npm run test:network
```

#### Índices e Catálogos

```bash
# Regenerar índice de skills
npm run index

# Construir catálogo JSON
npm run catalog

# Pipeline completo: validar + gerar índice + atualizar README
npm run chain

# Build final (com todas as validações)
npm run build
```

#### Sincronização

```bash
# Sincronizar skills oficiais da Microsoft
npm run sync:microsoft

# Sincronizar todas as oficial skills (Microsoft + cadeia completa)
npm run sync:all-official

# Atualizar skills customizadas
npm run update:skills
```

#### Aplicação Web

```bash
# Setup da aplicação web
npm run app:setup

# Instalar dependências da web app
npm run app:install

# Rodar em modo desenvolvimento
npm run app:dev

# Build da aplicação
npm run app:build

# Preview for build
npm run app:preview
```

### 🔄 Workflow Recomendado para Contribuições

Se você está adicionando novas skills:

```bash
# 1. Validar suas novas skills
npm run validate:strict

# 2. Gerar índices atualizados
npm run index

# 3. Construir catálogo
npm run catalog

# 4. Rodar testes
npm run test:local

# 5. Se tudo passou, fazer commit e push
git add .
git commit -m "Add new skills"
git push
```

### 📊 Script Detalhados

| Script | Arquivo | Função |
|--------|---------|--------|
| **validate** | `validate_skills.py` | Valida estrutura YAML das skills |
| **index** | `generate_index.py` | Gera arquivo de índice JSON |
| **catalog** | `build-catalog.js` | Constrói catálogo otimizado |
| **sync:microsoft** | `sync_microsoft_skills.py` | Sincroniza skills oficiais |
| **readme** | `update_readme.py` | Atualiza seções automáticas do README |
| **test** | `run-test-suite.js` | Executa testes completos |

### 🛠️ Scripts Utilitários

```bash
# Scripts auxiliares em scripts/
scripts/auto_activate.py           # Ativar skills automaticamente
scripts/auto_categorize_skills.py # Categorizar skills
scripts/fix_dangling_links.py      # Corrigir links quebrados
scripts/fix_skills_metadata.py     # Corrigir metadados
scripts/generate_skills_report.py  # Gerar relatório de skills
scripts/manage_skill_dates.py      # Gerenciar datas de skills
scripts/sync_recommended_skills.sh # Sincronizar skills recomendadas
```

---

## 🛠️ Solução de Problemas

### "Skills não aparecem no meu Assistente IA"

1. Verifique se as skills foram instaladas em `~/.gemini/antigravity/skills/`
2. Reinicie seu Assistente IA (ex: Claude Code, Cursor, etc.)
3. Tente pedir explicitamente: `@skill-name`

### "Qual é o formato correto para usar uma skill?"

Use `@nome-da-skill` ou simplesmente descreva o que precisa. Exemplo:
```
"Use a skill de brainstorming para me ajudar com..."
"Execute o linter e validador neste código"
```

### "Preciso de mais help?"

- Leia [USAGE.md](docs/USAGE.md) para guia completo
- Veja [FAQ.md](docs/FAQ.md) para perguntas comuns
- Verifique a [semantica em CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🤝 Contribuir

Quer adicionar sua própria skill? Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes.

### Passos Rápidos

1. Crie uma pasta em `skills/`
2. Adicione arquivo `SKILL.md` com metadados YAML
3. Escreva instruções claras
4. Teste com seu Assistente IA
5. Faça PR para o repositório

---

## 📊 Estatísticas

- **1006+** Skills disponíveis
- **20+** Categorias
- **15+** Bundles pré-configurados
- **Compatível** com 10+ Assistentes IA

---

## 📜 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## ☕ Suporte

Se este projeto te ajuda, considera apoiar:

- ⭐ Star no GitHub
- ☕ [Comprar um livro/café](https://buymeacoffee.com/sickn33)
- 🐛 Reportar bugs e sugestões

---

**Versão:** 6.10.0  
**Última atualização:** Março 2026  
**Mantido por:** Antigravity Community
