
# Patient Record Management System — Secure (Flask)

A minimal, **secure-by-default** patient record management system built with Flask.

## Features
- User authentication (Flask-Login) with hashed passwords
- Roles: **admin**, **clinician** (expandable)
- Patient CRUD (create, read, update, delete)
- Visit/Encounter records for each patient
- **Confidentiality**: Encrypts sensitive PHI fields using Fernet (symmetric encryption)
- CSRF protection (Flask-WTF)
- Authorisation checks (role-based + ownership constraints)
- **Audit logs**: every read/write is logged
- Secure cookies: `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE="Lax"`
- Input validation with WTForms
- SQLite by default; swap to Postgres/MySQL by changing `SQLALCHEMY_DATABASE_URI`

> ⚠️ Run behind HTTPS in production. The app forces secure settings but TLS termination should happen at the reverse proxy (nginx/Caddy).

## Quick Start

1. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create `.env` and initialize DB**
```bash
cp .env.example .env
# Generate a strong Fernet key if you want a new one:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Put that into FERNET_KEY in .env
flask db-init  # custom CLI to create tables and seed an admin
```

4. **Run**
```bash
flask run --debug
# open http://127.0.0.1:5000
# Default admin: admin@example.com / Admin@12345
```

## Roles
- **admin**: manage users, all patients, view audit log
- **clinician**: manage patients/visits, view only

## Security Notes
- Change the default admin password immediately.
- Store `.env` outside VCS. Rotate `FERNET_KEY` if compromised.
- Use **HTTPS** and set `SESSION_COOKIE_SECURE=1` when behind TLS.
- Database backups must be encrypted at rest.

## Project Structure
```
patient-records-secure/
├─ app.py
├─ config.py
├─ models.py
├─ forms.py
├─ security.py
├─ audit.py
├─ requirements.txt
├─ .env.example
├─ templates/
│  ├─ base.html
│  ├─ login.html
│  ├─ dashboard.html
│  ├─ patients.html
│  ├─ patient_form.html
│  ├─ patient_detail.html
│  ├─ visit_form.html
│  ├─ users.html
│  ├─ audit.html
└─ static/
   └─ styles.css
```

## Migrations
This starter keeps it simple by creating tables programmatically with a small CLI. For production, add Alembic/Flask-Migrate.

## License
MIT (educational starter).
