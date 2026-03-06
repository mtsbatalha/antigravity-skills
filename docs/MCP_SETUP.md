# 🔌 Configuração MCP (Model Context Protocol)

Antigravity Skills oferece suporte a **Model Context Protocol (MCP)** para integração seamless com Claude, VSCode, e outras ferramentas.

---

## 📌 O que é MCP?

**MCP (Model Context Protocol)** é um protocolo aberto que permite que aplicações IA acessem ferramentas e dados externos de forma padronizada.

Com MCP, você pode:
- ✅ Acessar skills diretamente via Claude Desktop
- ✅ Integrar skills em VSCode
- ✅ Usar skills em qualquer ferramenta compatível com MCP
- ✅ Compartilhar um servidor centralizado de skills

---

## 🚀 Instalação Rápida

### Pré-requisitos

```bash
# Python 3.10+
python --version

# Pip
pip --version
```

### Passo 1: Instalar Dependências MCP

```bash
# Instalar mcp package
pip install mcp

# Ou instalar a partir do requirements.txt (se existir)
pip install -r requirements.txt
```

### Passo 2: Configurar Claude Desktop

Adicione a seção MCP ao seu arquivo de configuração do Claude:

**Windows/Linux**: `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["C:\\caminho\\para\\antigravity-skills\\mcp\\skills_mcp.py"],
      "env": {}
    }
  }
}
```

### Passo 3: Reiniciar Claude

Feche e abra Claude Desktop novamente. Você deverá ver o ícone MCP conectado.

---

## 📁 Estrutura MCP

```
antigravity-skills/
├── .mcp.json                    # Configuração MCP
├── mcp/
│   ├── skills_mcp.py           # Servidor MCP principal
│   ├── __init__.py             # Inicializador
│   └── handlers.py             # Manipuladores de requisições
└── docs/
    └── MCP_SETUP.md            # Este arquivo
```

### Arquivo `.mcp.json`

Define como o servidor MCP é executado:

```json
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["mcp/skills_mcp.py"],
      "env": {}
    }
  }
}
```

- **command**: Interpretador Python
- **args**: Caminho para o script principal do MCP
- **env**: Variáveis de ambiente (opcional)

---

## 💻 Usando com Claude Desktop

### 1. Ver Skills Disponíveis

No Claude Desktop, use:

```
What skills are available? (via MCP)
```

Ou:

```
List all available skills for me.
```

### 2. Executar uma Skill

```
Use the @javascript-testing-patterns skill to help me write tests for my Node.js app.
```

### 3. Buscar Skills

```
Find skills related to React development.
```

---

## 🔧 Desenvolvimento Local

### Executar o Servidor MCP Manualmente

```bash
cd antigravity-skills
python mcp/skills_mcp.py
```

### Testar Conexão MCP

```bash
# Verificar se o servidor responde
curl http://localhost:8000/health

# Ou use Python
python -c "from mcp.skills_mcp import main; main()"
```

---

## 🛠️ Configuração Avançada

### Variáveis de Ambiente

```json
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["mcp/skills_mcp.py"],
      "env": {
        "SKILLS_DIR": "/custom/path/to/skills",
        "LOG_LEVEL": "DEBUG",
        "PORT": "8001"
      }
    }
  }
}
```

### Múltiplos Servidores MCP

Se você quiser rodar múltiplos servidores:

```json
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["mcp/skills_mcp.py"],
      "env": {}
    },
    "tools": {
      "command": "python",
      "args": ["mcp/tools_mcp.py"],
      "env": {}
    }
  }
}
```

---

## 🐛 Solução de Problemas MCP

### "MCP não conecta"

1. **Verificar Python**:
   ```bash
   python --version  # Deve ser 3.10+
   pip list | grep mcp
   ```

2. **Verificar caminho do script**:
   - Use caminho absoluto em `claude_desktop_config.json`
   - Separe diretórios com `\\` no Windows

3. **Verificar logs**:
   ```bash
   # No diretório do projeto
   python mcp/skills_mcp.py --debug
   ```

### "Skills não aparecem no Claude"

1. Reinicie Claude Desktop completamente
2. Verifique se `mcp/skills_mcp.py` existe
3. Verifique permissões de arquivo: `ls -la mcp/skills_mcp.py`
4. Tente rodar manualmente: `python mcp/skills_mcp.py`

### "Erro de Porta"

Se a porta padrão está em uso:

```json
{
  "mcpServers": {
    "skills": {
      "command": "python",
      "args": ["mcp/skills_mcp.py"],
      "env": {
        "PORT": "8002"
      }
    }
  }
}
```

---

## 📚 Recursos Adicionais

- [MCP Documentação Oficial](https://modelcontextprotocol.io/)
- [Claude Desktop Docs](https://claude.ai)
- [GitHub MCP Repository](https://github.com/modelcontextprotocol/python-sdk)

---

## 🤝 Contribuir

Quer melhorar a integração MCP? Veja [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Versão**: 1.0  
**Última atualização**: Março 2026  
**Status**: Estável ✅
