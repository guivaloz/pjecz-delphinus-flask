---
name: create-model
description: Generate a models.py file for a Flask blueprint following project conventions.
---

# Create Model

You are an expert in SQLAlchemy models for this Flask project. Use this skill when the user asks to create a `models.py` file for a blueprint.

## When to Use

- The user asks to create a new model or `models.py` for a blueprint
- The blueprint directory already exists under `pjecz_can_mayor_flask/blueprints/`
- The blueprint has only an `__init__.py` (stub) and needs its model defined

Do NOT use this skill for modifying existing `models.py` files or for creating blueprints themselves.

## Step-by-Step Workflow

1. Confirm the blueprint directory exists under `pjecz_can_mayor_flask/blueprints/`
2. Ask the user for:
   - **Class name** (singular PascalCase, e.g. `Documento`, `Remesa`)
   - **Table name** (plural snake_case, e.g. `documentos`, `remesas`)
   - **Columns**: name, type, constraints (unique, nullable, default)
   - **Foreign keys**: which parent tables this model references
   - **Child relationships**: which models reference this one as a parent
   - **Properties or special methods** needed
3. Determine the import tier (A, B, or C) based on what the model needs
4. Generate the file following the canonical template below
5. Write the file to `pjecz_can_mayor_flask/blueprints/<blueprint>/models.py`

## Import Tiers

### Tier A — Minimal (no FK, no children, no extras)

```python
"""
<Plural name>
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_can_mayor_flask.config.extensions import database
from pjecz_can_mayor_flask.lib.universal_mixin import UniversalMixin
```

### Tier B — With foreign keys and/or children

```python
"""
<Singular name>, modelos
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_can_mayor_flask.config.extensions import database
from pjecz_can_mayor_flask.lib.universal_mixin import UniversalMixin
```

### Tier C — Complex (datetime, Optional, Enum, cross-blueprint imports)

```python
"""
<Singular name>, modelos
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_can_mayor_flask.config.extensions import database
from pjecz_can_mayor_flask.lib.universal_mixin import UniversalMixin
```

Add cross-blueprint imports only when needed:

```python
from pjecz_can_mayor_flask.blueprints.<other>.models import <OtherClass>
```

## Column Type Reference

| Python type | SQLAlchemy usage | Example |
|---|---|---|
| `str` required | `Mapped[str] = mapped_column(String(N))` | `nombre: Mapped[str] = mapped_column(String(256), unique=True)` |
| `str` nullable | `Mapped[Optional[str]] = mapped_column(String(N))` | `titulo: Mapped[Optional[str]] = mapped_column(String(256))` |
| `str` with default | `Mapped[str] = mapped_column(String(N), default="", server_default="")` | `curp: Mapped[str] = mapped_column(String(256), default="", server_default="")` |
| `int` | `Mapped[int]` | `nivel: Mapped[int]` |
| `bool` | `Mapped[bool] = mapped_column(default=False)` | `en_navegacion: Mapped[bool] = mapped_column(default=False)` |
| `datetime` | `Mapped[datetime]` (from `datetime` stdlib) | `api_key_expiracion: Mapped[Optional[datetime]]` |
| `Enum` | `Mapped[str] = mapped_column(Enum(*CONSTANT, name="...", native_enum=False))` | See below |

### Common String sizes

- `String(16)` — claves, short codes
- `String(48)` — icons
- `String(64)` — routes, IPs, short descriptions, short names
- `String(128)` — API keys
- `String(256)` — names, descriptions, emails, titles
- `String(512)` — URLs
- `String(1024)` — messages, long text

### Enum pattern

```python
TIPOS = {"INGRESO": "Ingreso", "SALIO": "Salio"}

# In the class body:
tipo: Mapped[str] = mapped_column(
    Enum(*TIPOS, name="entradas_salidas_tipos", native_enum=False),
    index=True,
)
```

## Relationship Patterns

### Child → Parent (many-to-one)

Always a pair: FK column + relationship.

```python
# Claves foráneas
distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"))
distrito: Mapped["Distrito"] = relationship(back_populates="distritos")
```

- FK column name: `<singular>_id`
- ForeignKey string: `"tablename.id"` (plural table name)
- `back_populates` value: the attribute name on the parent that holds the list of children

### Parent → Children (one-to-many)

```python
# Hijos
autoridades: Mapped[list["Autoridad"]] = relationship(back_populates="distrito")
```

- Uses `Mapped[list["ChildClassName"]]` with forward-reference string
- Always `back_populates`, never `backref`

### Matching rule

If parent has `back_populates="autoridades"`, the child must have `back_populates="distrito"`. The names must be consistent.

## Canonical Template

```python
"""
<Plural name>
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_can_mayor_flask.config.extensions import database
from pjecz_can_mayor_flask.lib.universal_mixin import UniversalMixin


class <ClassName>(database.Model, UniversalMixin):
    """<ClassName>"""

    # Nombre de la tabla
    __tablename__ = "<table_name>"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    padre_id: Mapped[int] = mapped_column(ForeignKey("padres.id"))
    padre: Mapped["Padre"] = relationship(back_populates="hijos")

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)

    # Hijos
    hijos: Mapped[list["Hijo"]] = relationship(back_populates="<ClassName_snake>")

    def __repr__(self):
        """Representación"""
        return f"<<ClassName> {self.nombre}>"
```

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Table name | Plural, snake_case | `documentos`, `usuarios_roles` |
| Class name | Singular, PascalCase | `Documento`, `UsuarioRol` |
| FK column | `<singular>_id` | `distrito_id`, `usuario_id` |
| Blueprint dir | Matches table name | `blueprints/documentos/` |

## Section Comments

Use these Spanish comment headers inside the class, in this order:

1. `# Nombre de la tabla` — before `__tablename__`
2. `# Clave primaria` — before `id`
3. `# Claves foráneas` — before FK columns and their relationships
4. `# Columnas` — before data columns
5. `# Columnas que NO deben ser expuestas` — for sensitive fields (api_key, contrasena)
6. `# Hijos` — before child relationships
7. `# Propiedades` — before class-level cached attributes

## Docstring Conventions

- Module-level: triple-quoted, in Spanish. With ", modelos" suffix: `"""Autoridad, modelos"""`
- Class-level: triple-quoted, singular name: `"""Distrito"""`
- Method-level: triple-quoted, in Spanish: `"""Representación"""`

## Special Cases

### UserMixin (only for Usuario)

```python
class Usuario(database.Model, UserMixin, UniversalMixin):
```

Import `UserMixin` from `flask_login`.

### Class-level constants

```python
class Permiso(database.Model, UniversalMixin):
    VER = 1
    MODIFICAR = 2
    CREAR = 3
    ADMINISTRAR = 4
    NIVELES = {1: "Ver", 2: "Modificar", 3: "Crear", 4: "Administrar"}
```

### Properties with caching

```python
class Usuario(database.Model, UserMixin, UniversalMixin):
    modulos_menu_principal_consultados = []
    permisos_consultados = {}

    @property
    def nombre(self):
        """Junta nombres, apellido primero y apellido segundo"""
        ...
```

### No `__init__` method

Never define `__init__`. SQLAlchemy's declarative base provides the constructor automatically.

## After Creating the File

Remind the user to:

1. Register the blueprint in `pjecz_can_mayor_flask/app.py` if not already done
2. Add the module to `seed/modulos.csv`
3. Run `python3 cli/app.py db reiniciar` to recreate tables (no Alembic in this project)
