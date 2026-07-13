# AGENTS.md

Flask app for PJECZ Defensoría case management. Spanish-language codebase.

## Quick commands

```bash
# Run dev server (uvicorn with reload)
python main.py

# CLI (Typer-based, in cli/app.py)
python cli/app.py db reiniciar        # drop tables + seed from CSV (DEVELOPMENT only)
python cli/app.py db inicializar      # drop + create tables
python cli/app.py db alimentar        # seed from seed/*.csv
python cli/app.py db respaldar        # export DB to CSV
python cli/app.py usuarios nueva-api-key EMAIL
python cli/app.py usuarios nueva-contrasena EMAIL

# Formatting & linting (line-length=128 everywhere)
black .
isort .
ruff check .

# Type checking (excludes tests)
basedpyright
```

## Architecture

- **Entry**: `main.py` → uvicorn loads `pjecz_delphinus_flask.app:app`
- **App factory**: `pjecz_delphinus_flask/app.py` creates Flask app, registers blueprints, inits extensions
- **Blueprints** in `pjecz_delphinus_flask/blueprints/`: each has `views.py`, `models.py`, `forms.py`, `templates/`
- **Models** in `pjecz_delphinus_flask/blueprints/models.py`: database models (SQLAlchemy) a class named in singular (e.g. `Usuario`, `Rol`)
- **Views** in `pjecz_delphinus_flask/blueprints/views.py`: view functions (Flask views) for handling HTTP requests, the basic functions are `datatable_json`, `list_active`, `list_inactive`, `new`, `edit`, `delete` and `recover`
- **Forms** in `pjecz_delphinus_flask/blueprints/forms.py`: form classes (Flask-WTF) for validating user input
- **CLI** in `cli/`: separate Typer app with `db` and `usuarios` subcommands
- **Lib** in `pjecz_delphinus_flask/lib/`: shared utils (safe_string, datatables, cryptography, pwgen)
- **Config** in `pjecz_delphinus_flask/config/`: `settings.py` (pydantic-settings), `extensions.py` (Flask extensions)
- **Seed data**: CSV files in `seed/` for database seeding

## Key patterns

- All models inherit `UniversalMixin` which adds `creado`, `modificado`, `estatus` columns and `save()`/`delete()` methods
- Soft delete: `estatus="A"` active, `estatus="B"` deleted
- IDs exposed via HashIDs (salt from env `SALT`), use `model.encode_id()` / `Model.decode_id()`
- Passwords hashed with passlib `pbkdf2_sha256`
- Permissions system: `Usuario` → `UsuarioRol` → `Rol` → `Permiso` → `Modulo`, levels 0-4 (VER, CREAR, MODIFICAR, ADMINISTRAR)
- Templates use Jinja2 with `.jinja2` extension

## Environment

- Python 3.14, managed by uv
- PostgreSQL via psycopg2-binary
- `.env` loaded by python-dotenv (not committed)
- Key env vars: `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY`, `SALT`, `DEPLOYMENT_ENVIRONMENT`
- `DEPLOYMENT_ENVIRONMENT=PRODUCTION` prevents DB reset commands

## Gotchas

- CLI commands push app context at import time: `app.app_context().push()`
- F821 suppressed in ruff (undefined variable warnings ignored)
- No test suite yet (tests/ is empty)
