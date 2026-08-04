---
name: create-view
description: Generate a read-only views.py file plus list.jinja2 and detail.jinja2 templates for a Flask blueprint following project conventions.
---

# Create View

You are an expert in Flask views and Jinja2 templates for this project. Use this skill when the user asks to create the read-only views (active/inactive listings and detail) for a blueprint.

## When to Use

- The user asks to create `views.py`, `list.jinja2` and `detail.jinja2` for a blueprint
- The blueprint directory already exists under `pjecz_can_mayor_flask/blueprints/`
- The blueprint already has a `models.py` with the model defined

Do NOT use this skill for:

- Modifying existing `views.py` files or templates
- Creating `new`, `edit`, `delete` or `recover` views (or `new.jinja2`/`edit.jinja2` templates)
- Creating models (use the `create-model` skill) or forms

## Step-by-Step Workflow

1. Confirm the blueprint directory exists under `pjecz_can_mayor_flask/blueprints/` and read its `models.py` to learn the class name, columns and relationships
2. Ask the user for:
   - **MODULO constant**: uppercase name used for permissions (e.g. `DISTRITOS`). It must match the `nombre` in `seed/modulos.csv`
   - **List columns**: which columns the DataTable shows, in order, and which of them are filterable
   - **Link column**: which column renders as the link to the detail page (usually `clave`, `nombre` or `email`)
   - **Order column**: the column used in `order_by`
   - **Detail fields**: which fields the detail page shows, and which one is the "big" value (title)
   - **Parent links**: for FK fields, whether to link to the parent's detail page
3. Generate `views.py` following the canonical template below (read-only: `datatable_json`, `list_active`, `list_inactive`, `detail`)
4. Generate `templates/<blueprint>/list.jinja2`
5. Generate `templates/<blueprint>/detail.jinja2`
6. Write the files to `pjecz_can_mayor_flask/blueprints/<blueprint>/`

## Placeholders

| Placeholder | Meaning | Example |
|---|---|---|
| `<blueprint>` | Blueprint directory/name, plural snake_case | `distritos` |
| `<Model>` | Model class, singular PascalCase | `Distrito` |
| `<singular>` | Model instance variable, singular snake_case | `distrito` |
| `<Plural>` | Display name, plural | `Distritos` |
| `<Singular>` | Display name, singular | `Distrito` |
| `<MODULO>` | Permission module name, uppercase | `DISTRITOS` |
| `<PluralCamel>` | Plural in PascalCase for JS variables | `Distritos` |

## views.py Canonical Template

Read-only imports: no `flash`, `redirect`, `current_user`, `Bitacora`, `Modulo` or forms are needed. Import only the `safe_*` helpers actually used by the filters (`safe_clave` only when there is a clave-like filter).

```python
"""
<Plural>, vistas
"""

import json

from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from pjecz_can_mayor_flask.blueprints.<blueprint>.models import <Model>
from pjecz_can_mayor_flask.blueprints.permisos.models import Permiso
from pjecz_can_mayor_flask.blueprints.usuarios.decorators import permission_required
from pjecz_can_mayor_flask.lib.datatables import get_datatable_parameters, output_datatable_json
from pjecz_can_mayor_flask.lib.safe_string import safe_clave, safe_string

MODULO = "<MODULO>"

<blueprint> = Blueprint("<blueprint>", __name__, template_folder="templates")


@<blueprint>.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@<blueprint>.route("/<blueprint>/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de <Plural>"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = <Model>.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # ... filtros por columnas (ver "Filter Patterns") ...
    # Ordenar y paginar
    registros = consulta.order_by(<Model>.<order_column>).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "<link_column>": resultado.<link_column>,
                    "url": url_for("<blueprint>.detail", <singular>_id=resultado.id),
                },
                "<column_2>": resultado.<column_2>,
                "<column_3>": resultado.<column_3>,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@<blueprint>.route("/<blueprint>")
def list_active():
    """Listado de <Plural> activos"""
    return render_template(
        "<blueprint>/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="<Plural>",
        estatus="A",
    )


@<blueprint>.route("/<blueprint>/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de <Plural> inactivos"""
    return render_template(
        "<blueprint>/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="<Plural> inactivos",
        estatus="B",
    )


@<blueprint>.route("/<blueprint>/<int:<singular>_id>")
def detail(<singular>_id):
    """Detalle de <un/una> <Model>"""
    <singular> = <Model>.query.get_or_404(<singular>_id)
    return render_template("<blueprint>/detail.jinja2", <singular>=<singular>)
```

### Filter Patterns for `datatable_json`

The `estatus` filter always comes first (shown in the template). Add the other filters as needed, in the same order as the list columns.

**Clave-like column** (validated with `safe_clave`, wrapped in try/except):

```python
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(<Model>.clave.contains(clave))
        except ValueError:
            pass
```

**Free-text column** (validated with `safe_string`, always `save_enie=True`):

```python
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(<Model>.nombre.contains(nombre))
```

**Foreign key id column** (exact match by integer):

```python
    if "distrito_id" in request.form:
        try:
            distrito_id = int(request.form["distrito_id"])
            consulta = consulta.filter(<Model>.distrito_id == distrito_id)
        except ValueError:
            pass
```

**Parent table column** (join after the own-column filters, under the comment `# Luego filtrar por columnas de otras tablas`; requires importing the parent model):

```python
    # Luego filtrar por columnas de otras tablas
    if "distrito_nombre" in request.form:
        distrito_nombre = safe_string(request.form["distrito_nombre"], save_enie=True)
        if distrito_nombre != "":
            consulta = consulta.join(Distrito).filter(Distrito.nombre.contains(distrito_nombre))
```

### Data Row Rules

- The first key is always `"detalle"`: a dict with the link column value and the detail `url`
- Parent columns are flattened with a prefix: `"distrito_clave": resultado.distrito.clave`
- Every key (except `detalle`) maps 1:1 to an entry in the template's `columns` array

### Docstring and Wording Rules

- Module docstring: `"""<Plural>, vistas"""` (e.g. `"""Distritos, vistas"""`)
- Respect grammatical gender: `"""Listado de Autoridades activas"""` vs `"""Listado de Distritos activos"""`; `"""Detalle de una Autoridad"""` vs `"""Detalle de un Distrito"""`; `"Autoridades inactivas"` vs `"Distritos inactivos"`
- Keep the Spanish section comments exactly as in the template: `# Tomar parámetros de Datatables`, `# Consultar`, `# Primero filtrar por columnas propias`, `# Luego filtrar por columnas de otras tablas`, `# Ordenar y paginar`, `# Elaborar datos para DataTable`, `# Entregar JSON`

## list.jinja2 Canonical Template

```jinja2
{% extends 'layouts/app.jinja2' %}
{% import 'macros/list.jinja2' as list %}
{% import 'macros/topbar.jinja2' as topbar %}

{% block title %}{{ titulo }}{% endblock %}

{% block topbar_actions %}
    {% call topbar.page_buttons(titulo) %}
        {% if current_user.can_admin('<MODULO>') %}
            {% if estatus == 'A' %}{{ topbar.button_list_inactive('Inactivos', url_for('<blueprint>.list_inactive')) }}{% endif %}
            {% if estatus == 'B' %}{{ topbar.button_list_active('Activos', url_for('<blueprint>.list_active')) }}{% endif %}
        {% endif %}
    {% endcall %}
{% endblock %}

{% block content %}
    {% call list.card() %}
        <!-- Filtros <Plural> -->
        <div class="row">
            <div class="col">
                <form class="row g-1 mb-3" id="filtradorForm" onsubmit="filtros<PluralCamel>.buscar(); return false;">
                    <div class="col-4">
                        <div class="form-floating">
                            <input id="filtro<Model><Campo>" type="text" class="form-control" aria-label="<Label>" style="text-transform: uppercase;">
                            <label for="filtro<Model><Campo>"><Label></label>
                        </div>
                    </div>
                    <div class="col-4 text-end">
                        <button title="Buscar" class="btn btn-primary btn-lg" onclick="filtros<PluralCamel>.buscar(); return false;" id="button-buscar"><span class="mdi mdi-magnify"></span></button>
                        <button title="Limpiar" class="btn btn-warning btn-lg" type="reset" onclick="filtros<PluralCamel>.limpiar();" id="button-limpiar"><span class="mdi mdi-broom"></span></button>
                    </div>
                </form>
            </div>
        </div>
        <!-- Datatable <Plural> -->
        <table id="<blueprint>_datatable" class="table {% if estatus == 'B'%}table-dark{% endif %} display nowrap" style="width:100%">
            <thead>
                <tr>
                    <th><Column 1 header></th>
                    <th><Column 2 header></th>
                    <th><Column 3 header></th>
                </tr>
            </thead>
        </table>
    {% endcall %}
{% endblock %}

{% block custom_javascript %}
    <script src="/static/js/datatables-constructor.js"></script>
    <script src="/static/js/datatables-filtros.js"></script>
    <script>
        // DataTable <Plural>
        const constructorDataTable = new ConfigDataTable( '{{ csrf_token() }}' );
        let configDT<PluralCamel> = constructorDataTable.config();
        configDT<PluralCamel>['ajax']['url'] = "{{ url_for('<blueprint>.datatable_json') }}";
        configDT<PluralCamel>['ajax']['data'] = {{ filtros }};
        configDT<PluralCamel>['columns'] = [
            { data: 'detalle' },
            { data: '<column_2>' },
            { data: '<column_3>' }
        ];
        configDT<PluralCamel>['columnDefs'] = [
            {
                targets: 0, // detalle
                data: null,
                render: function(data, type, row, meta) {
                    return '<a href="' + data.url + '">' + data.<link_column> + '</a>';
                }
            }
        ];
        // Filtros <Plural>
        const filtros<PluralCamel> = new FiltrosDataTable('#<blueprint>_datatable', configDT<PluralCamel>);
        filtros<PluralCamel>.agregarInput('filtro<Model><Campo>', '<campo>');
        filtros<PluralCamel>.precargar();
    </script>
{% endblock %}
```

### list.jinja2 Rules

- The topbar only has the Inactivos/Activos toggle, guarded by `current_user.can_admin('<MODULO>')`. There is no `button_new` because this skill does not create the `new` view
- One filter `<input>` per filterable column; adjust the Bootstrap `col-*` classes so the row adds up to 12 (inputs typically `col-2` to `col-4`, buttons cell takes the rest with `text-end`)
- Filter input ids are camelCase: `filtro<Model><Campo>` (e.g. `filtroDistritoClave`); the second argument of `agregarInput` is the snake_case key read from `request.form` in `views.py` (e.g. `'clave'`)
- Text filter inputs use `style="text-transform: uppercase;"`
- The `<th>` order, the `columns` array and the `data` keys in `views.py` must match exactly; the first column is always `detalle`
- Keep the `{% if estatus == 'B'%}table-dark{% endif %}` class on the table

## detail.jinja2 Canonical Template

```jinja2
{% extends 'layouts/app.jinja2' %}
{% import 'macros/detail.jinja2' as detail %}
{% import 'macros/topbar.jinja2' as topbar %}

{% block title %}<Singular> {{ <singular>.<link_column> }}{% endblock %}

{% block topbar_actions %}
    {% call topbar.page_buttons('<Singular> ' + <singular>.<link_column>) %}
        {{ topbar.button_previous('<Plural>', url_for('<blueprint>.list_active')) }}
    {% endcall %}
{% endblock %}

{% block content %}
    {% call detail.card(estatus=<singular>.estatus) %}
        <div class="row">
            {{ detail.label_value_big('<Label>', <singular>.<link_column>) }}
            {{ detail.label_value('<Label>', <singular>.<column_2>) }}
            {{ detail.label_value_boolean('<Label>', <singular>.<bool_column>) }}
        </div>
    {% endcall %}
{% endblock %}
```

### detail.jinja2 Rules

- The topbar only has `button_previous` back to `list_active`. There are no edit/delete/recover buttons because this skill does not create those views
- There is no `custom_javascript` block: without delete/recover there are no modals, and without related listings there are no DataTables
- Use `detail.label_value_big` for the main identifying field and `detail.label_value` for the rest; use `detail.label_value_boolean` for booleans
- For a foreign key field, link to the parent's detail guarded by `can_view` on the parent module:

```jinja2
            {% if current_user.can_view('<PARENT_MODULO>') %}
                {{ detail.label_value('<Parent label>', <singular>.<parent>.<parent_field>, url_for('<parent_blueprint>.detail', <parent_singular>_id=<singular>.<parent>_id)) }}
            {% else %}
                {{ detail.label_value('<Parent label>', <singular>.<parent>.<parent_field>) }}
            {% endif %}
```

## Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Route: list | `/<blueprint>` | `/distritos` |
| Route: inactive list | `/<blueprint>/inactivos` | `/distritos/inactivos` |
| Route: detail | `/<blueprint>/<int:<singular>_id>` | `/distritos/<int:distrito_id>` |
| Route: datatable | `/<blueprint>/datatable_json` | `/distritos/datatable_json` |
| Endpoint references | `<blueprint>.<view>` | `url_for('distritos.detail', distrito_id=...)` |
| MODULO constant | Uppercase, matches `nombre` in `seed/modulos.csv` | `DISTRITOS` |
| Template folder | `templates/<blueprint>/` | `templates/distritos/` |
| Detail template variable | Singular snake_case | `distrito=distrito` |
| Table element id | `<blueprint>_datatable` | `distritos_datatable` |
| JS config variable | `configDT<PluralCamel>` | `configDTDistritos` |
| JS filters variable | `filtros<PluralCamel>` | `filtrosDistritos` |

## Macros Reference

- `macros/topbar.jinja2`: `page_buttons(title)`, `button_previous(label, url)`, `button_list_active(label, url)`, `button_list_inactive(label, url)`
- `macros/list.jinja2`: `card(title='')` (used as `{% call list.card() %}...{% endcall %}`)
- `macros/detail.jinja2`: `card(title='', estatus='')`, `label_value(label, value, link='')`, `label_value_big(label, value)`, `label_value_boolean(label, value)`
- Permission helpers in templates: `current_user.can_view('<MODULO>')`, `current_user.can_admin('<MODULO>')`

## After Creating the Files

Remind the user to:

1. Register the blueprint in `pjecz_can_mayor_flask/app.py` (import from `<blueprint>.views` and add `app.register_blueprint(<blueprint>)`) if not already done
2. Add the module to `seed/modulos.csv` if it is not there yet (the `MODULO` constant must match its `nombre`, and permissions are generated per module)
3. Run `python3 cli/app.py db reiniciar` if a new module was added to the seed
