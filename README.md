# Archforge

CLI de scaffolding arquitetural para projetos Python — inspirado em Cookiecutter, porém opinativo, incremental e focado em consistência estrutural.

## Instalação

Com [uv](https://docs.astral.sh/uv/):

```bash
uv tool install archforge
```

Com pip:

```bash
pip install archforge
```

Desenvolvimento local:

```bash
uv sync --all-extras
uv run archforge --version
```

## Comandos

### Criar projeto

Modo interativo:

```bash
archforge init
```

Modo não interativo:

```bash
archforge init \
  --name ridehub \
  --framework fastapi \
  --architecture pragmatic \
  --docker \
  --tests \
  --ci
```

> `--style` continua funcionando como alias deprecated de `--architecture`.

### Criar módulo

Dentro de um projeto archforge (detectado via `.archforge.toml`):

```bash
archforge make module rides
```

Opções:

```bash
archforge make module rides --crud --integration --worker --domain
```

## Arquiteturas (capabilities)

Cada **architecture** define uma capability estrutural independente. Hoje:

| Architecture | Estrutura |
|--------------|-----------|
| **pragmatic** | `src/app/<module>/{entities,services,repositories,routes,schemas,tests}` |
| **canonical** | `src/{domain,application,infrastructure,interfaces}/` |

Preparado para crescer com `modular-monolith`, `hexagonal`, `event-driven`, `cqrs`, `mcp-native`, etc. — basta adicionar em `templates/architectures/<architecture>/`.

O `.archforge.toml` grava `architecture = "pragmatic"`. Projetos antigos com `style` continuam sendo lidos normalmente.

## Frameworks

| Framework | MVP |
|-----------|-----|
| FastAPI + Pragmatic | ✅ |
| Django + Pragmatic | ✅ |
| FastAPI + Canonical | 🔜 |
| Django + Canonical | 🔜 |
| MCP | 🔜 |
| CLI | 🔜 |

## Stack

- Python 3.12+
- [Typer](https://typer.tiangolo.com/) — CLI
- [Rich](https://rich.readthedocs.io/) — terminal
- [Questionary](https://questionary.readthedocs.io/) — wizard interativo
- [Jinja2](https://jinja.palletsprojects.com/) — templates
- [uv](https://docs.astral.sh/uv/) — ambientes e dependências

## Arquitetura do CLI

```
src/archforge/
├── cli.py              # Typer app
├── core/               # config, renderer, filesystem, project detection
├── wizard/             # Questionary wizards
├── generators/         # project & module orchestration
└── templates/          # Jinja2 templates desacoplados
    └── architectures/
        └── pragmatic/fastapi/
            ├── project/
            └── module/
```

**Separação de responsabilidades:**

- `core/renderer.py` — apenas renderização Jinja2
- `core/filesystem.py` — apenas escrita em disco
- `core/templates.py` — resolução de paths `architectures/{architecture}/{framework}/`
- `generators/` — orquestração (sem lógica de template inline)
- `templates/` — artefatos desacoplados por architecture/framework

## Licença

MIT
