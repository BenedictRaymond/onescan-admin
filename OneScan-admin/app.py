from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import qrcode
from io import BytesIO
import base64
import pymysql
import urllib.parse

load_dotenv()  # Load environment variables from .env file

# MySQL Configuration
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "form_builder"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "FLASK_SECRET_KEY", "fallback-secret-key-change-this"
)

# Properly encode the password for the MySQL connection string
encoded_password = urllib.parse.quote_plus(MYSQL_CONFIG["password"])
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql://{MYSQL_CONFIG['user']}:{encoded_password}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


def create_dynamic_table(form_id, fields):
    """Create a dynamic table based on form fields"""
    table_name = f"form_data_{form_id}"

    # Start building the CREATE TABLE statement
    columns = [
        "id INT AUTO_INCREMENT PRIMARY KEY",
        "submission_time DATETIME DEFAULT CURRENT_TIMESTAMP",
    ]

    # Add columns based on form fields
    for field in fields:
        field_type = "VARCHAR(255)"  # Default type
        if field["type"] == "number":
            field_type = "DECIMAL(10,2)"
        elif field["type"] == "date":
            field_type = "DATE"

        # Sanitize field name for SQL
        field_name = field["label"].lower().replace(" ", "_")
        nullable = "" if field.get("required") else "NULL"
        columns.append(f"{field_name} {field_type} {nullable}")

    # Create the table
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns)}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    try:
        with db.engine.connect() as conn:
            conn.execute(db.text(create_table_sql))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False


# Database Models
class Organization(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    org_type = db.Column(db.String(50), nullable=False)
    forms = db.relationship("Form", backref="organization", lazy=True)


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    fields = db.Column(db.Text, nullable=False)  # JSON string of form fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organization.id"), nullable=False
    )
    table_name = db.Column(db.String(100), unique=True)

    def generate_qr_data(self):
        """Generate QR code data containing form structure and database config"""
        fields_dict = json.loads(self.fields)
        # Create database configuration (excluding sensitive data)
        db_config = {
            "host": MYSQL_CONFIG["host"],
            "port": MYSQL_CONFIG["port"],
            "password": MYSQL_CONFIG["password"],
            "database": MYSQL_CONFIG["database"],
            "table": f"form_data_{self.id}",
        }

        # Extract field information
        form_structure = {
            "form_id": self.id,
            "title": self.title,
            "fields": [
                {
                    "name": field["label"].lower().replace(" ", "_"),
                    "type": field["type"],
                    "label": field["label"],
                    "required": field.get("required", False),
                }
                for field in fields_dict
            ],
            "database": db_config,
        }
        return json.dumps(form_structure)

    def generate_qr_code(self):
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.generate_qr_data())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Organization, int(user_id))


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        org_type = request.form.get("org_type")

        if Organization.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        org = Organization(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            org_type=org_type,
        )
        db.session.add(org)
        db.session.commit()

        flash("Registration successful")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        org = Organization.query.filter_by(email=email).first()

        if org and check_password_hash(org.password_hash, password):
            login_user(org)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    forms = Form.query.filter_by(organization_id=current_user.id).all()
    # Generate QR codes for each form
    forms_with_qr = [(form, form.generate_qr_code()) for form in forms]
    return render_template("dashboard.html", forms=forms_with_qr)


@app.route("/form_qr/<int:form_id>")
@login_required
def form_qr(form_id):
    form = Form.query.get_or_404(form_id)
    if form.organization_id != current_user.id:
        flash("Unauthorized access")
        return redirect(url_for("dashboard"))

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(form.generate_qr_data())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(
        img_io, mimetype="image/png", download_name=f"form_{form_id}_qr.png"
    )


@app.route("/create_form", methods=["GET", "POST"])
@login_required
def create_form():
    if request.method == "POST":
        data = request.get_json()
        new_form = Form(
            title=data["title"],
            fields=json.dumps(data["fields"]),
            organization_id=current_user.id,
        )
        db.session.add(new_form)
        db.session.commit()

        # Create the dynamic table for this form
        if create_dynamic_table(new_form.id, data["fields"]):
            new_form.table_name = f"form_data_{new_form.id}"
            db.session.commit()
            return jsonify({"success": True, "form_id": new_form.id})
        else:
            db.session.delete(new_form)
            db.session.commit()
            return jsonify({"success": False, "error": "Failed to create form table"})

    return render_template("create_form.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
