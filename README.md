# M&M Vendedores — Full-Stack E-commerce
# This whole document have been written by Claude Fable 5.

A clothing e-commerce application with product catalog, user accounts, Stripe checkout, and purchase history. The project consists of a **Django REST backend** and a **Next.js frontend**.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router), React, Tailwind CSS, Axios |
| Backend | Django 5.1, Django REST Framework |
| Auth | JWT (`djangorestframework_simplejwt`) + Google OAuth (`django-allauth`) |
| Payments | Stripe Checkout + Webhooks |
| Database | SQLite (development) |
| Email | SMTP (registration confirmation, password reset) |

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────────┐
│  Next.js frontend   │  HTTP   │       Django backend         │
│  localhost:3000     │────────▶│       localhost:8000         │
│                     │  JSON   │                              │
│  - Catalog/filters  │         │  users/        auth, forms,  │
│  - Login/Register   │         │                search        │
│  - Product page     │         │  Api_Clothes/  product CRUD  │
│  - Payment history  │         │  payments/     Stripe        │
└─────────────────────┘         └──────────────┬───────────────┘
                                               │
                       Stripe ─── webhook ─────┘
```

- **`users/`** — registration, login (issues JWT pair), logout, password reset via email, product search, category filter, shipping estimate (Correios).
- **`Api_Clothes/`** — product models (clothes, sizes, colors, categories, per-variant stock) and the catalog API.
- **`payments/`** — creates Stripe Checkout sessions and receives the `checkout.session.completed` webhook, which records the purchase in `HistoryPayments` and decrements stock.

**Authentication flow:** `POST /forms/process_login/` returns an `access` (30 min) and `refresh` (7 days) token pair. The frontend stores them in `localStorage` and sends `Authorization: Bearer <access>` on protected calls. On a 401, it calls `POST /api/token/refresh/`; if the refresh also fails, the user is redirected to login.

### Main API endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/API/Crud/` | GET | — | Product catalog |
| `/forms/process_register/` | POST | — | Create account |
| `/forms/process_login/` | POST | — | Login, returns JWT pair |
| `/api/token/refresh/` | POST | — | Refresh the access token |
| `/forms/process_users/` | POST | JWT | Current user data |
| `/forms/process_user_payments/` | GET | JWT | Purchase history |
| `/forms/process_search/` | POST | — | Product search by name |
| `/forms/process_category/` | POST | — | Filter by category |
| `/forms/calculo_frete_prazo/` | POST | — | Shipping estimate (Correios) |
| `/Payments/create-checkout-session/` | POST | — | Start Stripe Checkout |
| `/Payments/webhook/` | POST | Stripe signature | Payment confirmation |

## Running locally

Requirements: Python 3.10+, Node.js 18+.

**Backend:**

```bash
cp .env.example .env        # then fill in the values (see below)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # http://localhost:8000
```

**Frontend:**

```bash
cd setup_frontend
npm install
npm run dev                 # http://localhost:3000
```

### Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django signing key (also signs JWTs). Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `STRIPE_SECRET_KEY` | Stripe API key |
| `WEBHOOK_KEY` | Stripe webhook signing secret |
| `CLIENT_ID_GOOGLE` / `SECRET` | Google OAuth (django-allauth) |
| `EMAIL_HOST_PASSWORD` | SMTP password for transactional email |

Never commit `.env` — it is gitignored. Rotating `SECRET_KEY` invalidates all outstanding JWTs (users must log in again).

### Stripe webhook in development

Point a webhook at the backend with the Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/Payments/webhook/
```

and put the printed signing secret in `WEBHOOK_KEY`.

## Project layout

```
├── manage.py
├── setup_back_end/      # Django project (settings, root urls)
├── users/               # auth, account flows, search
├── Api_Clothes/         # product domain (models, catalog API)
├── payments/            # Stripe checkout + webhook
├── static/              # source static files
├── templates/           # server-rendered pages (admin-facing/legacy)
└── setup_frontend/      # Next.js application
    └── src/app/         # App Router pages and components
```

## Notes

- `staticfiles/` is build output (`python manage.py collectstatic`) and is not tracked.
- The repository previously contained C# (ASP.NET) and Node/Express services; both were removed and their responsibilities consolidated into Django.
