
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from config import Config
from models import db, User, Patient, Visit
from forms import LoginForm, PatientForm, VisitForm
from security import encrypt_field, decrypt_field
from audit import log_event

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.cli.command("db-init")
    def db_init():
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(email="admin@example.com").first():
                admin = User(email="admin@example.com", name="Admin", role="admin")
                admin.set_password("Admin@12345")
                db.session.add(admin)
                db.session.commit()
                print("Created default admin: admin@example.com / Admin@12345")
            else:
                print("Admin already exists")

    def require_role(*roles):
        def wrapper(fn):
            def inner(*args, **kwargs):
                if not current_user.is_authenticated:
                    return login_manager.unauthorized()
                if current_user.role not in roles:
                    abort(403)
                return fn(*args, **kwargs)
            inner.__name__ = fn.__name__
            return inner
        return wrapper

    @app.route("/", methods=["GET"])
    @login_required
    def index():
        return render_template("dashboard.html")

    @app.route("/login", methods=["GET","POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                log_event(user.id, "login", "user", user.id, {"email": user.email})
                return redirect(url_for("index"))
            flash("Invalid credentials", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        log_event(current_user.id, "logout", "user", current_user.id, {})
        logout_user()
        return redirect(url_for("login"))

    # Patients
    @app.route("/patients")
    @login_required
    def patients_list():
        q = request.args.get("q", "").strip()
        if q:
            patients = Patient.query.filter(
                (Patient.first_name.ilike(f"%{q}%")) | (Patient.last_name.ilike(f"%{q}%"))
            ).order_by(Patient.last_name).all()
        else:
            patients = Patient.query.order_by(Patient.last_name).all()
        log_event(current_user.id, "read", "patient", None, {"query": q})
        return render_template("patients.html", patients=patients, q=q, decrypt=decrypt_field)

    @app.route("/patients/new", methods=["GET","POST"])
    @login_required
    def patient_new():
        form = PatientForm()
        if form.validate_on_submit():
            p = Patient(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                dob=form.dob.data,
                gender=form.gender.data,
                address_enc=encrypt_field(form.address.data or ""),
                phone_enc=encrypt_field(form.phone.data or ""),
                medical_history_enc=encrypt_field(form.medical_history.data or ""),
            )
            db.session.add(p)
            db.session.commit()
            log_event(current_user.id, "create", "patient", p.id, {})
            flash("Patient created", "success")
            return redirect(url_for("patients_list"))
        return render_template("patient_form.html", form=form, action="New")

    @app.route("/patients/<int:pid>")
    @login_required
    def patient_detail(pid):
        p = Patient.query.get_or_404(pid)
        log_event(current_user.id, "read", "patient", p.id, {})
        return render_template("patient_detail.html", p=p, decrypt=decrypt_field)

    @app.route("/patients/<int:pid>/edit", methods=["GET","POST"])
    @login_required
    def patient_edit(pid):
        p = Patient.query.get_or_404(pid)
        form = PatientForm(
            first_name=p.first_name,
            last_name=p.last_name,
            dob=p.dob,
            gender=p.gender,
            address=decrypt_field(p.address_enc),
            phone=decrypt_field(p.phone_enc),
            medical_history=decrypt_field(p.medical_history_enc),
        )
        if form.validate_on_submit():
            p.first_name = form.first_name.data.strip()
            p.last_name = form.last_name.data.strip()
            p.dob = form.dob.data
            p.gender = form.gender.data
            p.address_enc = encrypt_field(form.address.data or "")
            p.phone_enc = encrypt_field(form.phone.data or "")
            p.medical_history_enc = encrypt_field(form.medical_history.data or "")
            db.session.commit()
            log_event(current_user.id, "update", "patient", p.id, {})
            flash("Patient updated", "success")
            return redirect(url_for("patient_detail", pid=p.id))
        return render_template("patient_form.html", form=form, action="Edit")

    @app.route("/patients/<int:pid>/delete", methods=["POST"])
    @login_required
    def patient_delete(pid):
        p = Patient.query.get_or_404(pid)
        db.session.delete(p)
        db.session.commit()
        log_event(current_user.id, "delete", "patient", pid, {})
        flash("Patient deleted", "warning")
        return redirect(url_for("patients_list"))

    # Visits
    @app.route("/patients/<int:pid>/visits/new", methods=["GET","POST"])
    @login_required
    def visit_new(pid):
        p = Patient.query.get_or_404(pid)
        form = VisitForm()
        if form.validate_on_submit():
            v = Visit(
                patient_id=p.id,
                clinician_id=current_user.id,
                visit_date=form.visit_date.data,
                reason_enc=encrypt_field(form.reason.data or ""),
                notes_enc=encrypt_field(form.notes.data or ""),
            )
            db.session.add(v)
            db.session.commit()
            log_event(current_user.id, "create", "visit", v.id, {"patient_id": p.id})
            flash("Visit added", "success")
            return redirect(url_for("patient_detail", pid=p.id))
        return render_template("visit_form.html", form=form, p=p)

    @app.route("/patients/<int:pid>/visits/<int:vid>/delete", methods=["POST"])
    @login_required
    def visit_delete(pid, vid):
        v = Visit.query.get_or_404(vid)
        if v.patient_id != pid:
            abort(404)
        db.session.delete(v)
        db.session.commit()
        log_event(current_user.id, "delete", "visit", vid, {"patient_id": pid})
        flash("Visit deleted", "warning")
        return redirect(url_for("patient_detail", pid=pid))

    # Admin: users and audit log
    @app.route("/admin/users")
    @login_required
    def users_page():
        if current_user.role != "admin":
            abort(403)
        users = User.query.order_by(User.id).all()
        return render_template("users.html", users=users)

    @app.route("/admin/audit")
    @login_required
    def audit_page():
        if current_user.role != "admin":
            abort(403)
        from models import AuditLog
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(500).all()
        return render_template("audit.html", logs=logs)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
