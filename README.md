# Remarcable — Product Catalog

A small Django application that models **products**, **categories**, and **tags**,
and provides a public page to **search and filter** products by description,
category, and tag (filters can be combined).

## Tech stack

- Python 3.6+, Django 3.2
- SQLite (default development database)
- Django templates + plain CSS (Material Design 3 styling, Material Symbols icons via CDN)
- No front-end build step required

## Setup

```bash
python -m venv venv
venv\Scripts\activate              # Windows  (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python manage.py migrate
```

## Load sample data

The project ships with sample data (5 categories, 10 tags, 20 products).

Option A — load the fixture:

```bash
python manage.py loaddata sample_data.json
```

Option B — run the seeder (idempotent):

```bash
python manage.py seed_products
```

## Run

```bash
python manage.py createsuperuser   # create an admin login to manage data
python manage.py runserver
```

- Catalog / search page: http://127.0.0.1:8000/
- Admin (data entry): http://127.0.0.1:8000/admin/

## How search & filtering works

The filter UI is a single GET form. Query parameters:

- `q` — case-insensitive match against the product **description**
- `category` — a category **slug**
- `tags` — repeatable; matches products having **any** of the selected tags

They combine, e.g. `/?q=wire&category=wire-cable&tags=copper`. The query logic
lives in a custom `ProductQuerySet` in `products/models.py`, keeping the view thin.

## Project structure

```
config/                      project settings, root URLconf, WSGI/ASGI
products/
  models.py                  Category, Tag, Product + ProductQuerySet (filter logic)
  admin.py                   admin registration for all three models
  views.py                   product_list view
  urls.py                    products URL config
  constants.py               field limits, query-param names, context keys
  templates/
    base.html                base layout + Material Design styles
    products/product_list.html
    components/               reusable partials (topbar, filters, card, chip, ...)
  management/commands/
    seed_products.py          sample-data seeder
  fixtures/
    sample_data.json          exported sample data
```

## Assumptions

- The search/filter page is intentionally **public** (no login). Data entry is
  done through the **authenticated Django admin**.
- Tag filtering uses **OR** semantics: a product matches if it has any of the
  selected tags.
- `SECRET_KEY` and `DEBUG` use the development defaults from `django-admin
  startproject`; for production these should be moved to environment variables.

## Note for editors (VS Code)

Auto-formatters (e.g. Prettier) can break Django template tags by wrapping
`{% ... %}` across lines. A `.prettierignore` excludes `templates/`; if you use
VS Code, also disable format-on-save for HTML/Django templates.

## AI usage (per assignment policy)

AI assistance (Claude) was used during development and is disclosed here:

- Front-end **templates and CSS** (Material Design 3 layout, reusable component
  partials) were AI-assisted, then reviewed and adjusted.
- The **`seed_products` command** and the sample-data list were AI-generated.
- AI assisted with **debugging** project configuration and template issues.
- AI helped add **code comments, docstrings (function descriptions), and
  parameter documentation**.

All AI-generated code has been reviewed and is understood by the submitter.
