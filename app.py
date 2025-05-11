from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
from flask_cors import CORS
import psycopg2
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

app.logger.addHandler(log_handler)

# Connect to your PostgreSQL database
for attempt in range(10):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Connected to the database!")
        break
    except psycopg2.OperationalError as e:
        print(f"Database not ready, retrying in 2s... ({attempt + 1}/10)")
        time.sleep(2)
else:
    raise Exception("Failed to connect to the database after several attempts")

cur = conn.cursor()

class User(UserMixin):
    def __init__(self, id_, username, password_hash, is_admin):
        self.user_id = id_
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

    def get_id(self):
        return str(self.user_id)

@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT user_id, username, password_hash, is_admin FROM users WHERE user_id = %s", (user_id,))
    user_data = cur.fetchone()
    if user_data:
        return User(id_=user_data[0], username=user_data[1], password_hash=user_data[2], is_admin=user_data[3])
    return None

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]

        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash("Username already exists. Please choose another.", "warning")
            return redirect(url_for("signup"))


        hashed_pw = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_pw)
        )
        conn.commit()
        return redirect("/")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]

        cur.execute("SELECT user_id, username, password_hash, is_admin FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()

        if user_data and check_password_hash(user_data[2], password):
            user = User(id_=user_data[0], username=user_data[1], password_hash=user_data[2], is_admin=user_data[3])
            login_user(user)
            return redirect(request.args.get('next') or "/")

        flash("Invalid username or password", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    if user_count > 0:
        return redirect("/login")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)

        cur.execute("""
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (%s, %s, %s)
        """, (username, hashed_pw, True))
        conn.commit()
        return redirect("/login")

    return render_template("setup.html")

@app.before_request
def check_first_user():
    # Avoid redirect loop or static file issues
    if request.endpoint in [None, 'setup', 'static']:
        return

    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    if user_count == 0:
        return redirect("/setup")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    cur.execute("SELECT project_id, name FROM projects")
    projects = cur.fetchall()

    if request.method == "POST":
        task = request.form["task"]
        comments = request.form["comments"]
        task_date = request.form["task_date"]
        project_id = request.form["project"]
        time_spent = request.form["time_spent"]

        cur.execute("""
            INSERT INTO tasks (task, comments, task_date, project_id, time_spent, user_id)
            VALUES (%s, %s, %s, %s, make_interval(mins => %s), %s)
        """, (task, comments, task_date, project_id, time_spent, current_user.user_id))
        conn.commit()
        return redirect("/")

    project_filter = request.args.get('project_filter')
    start_date = request.args.get('start_date') or date.today().isoformat()
    end_date = request.args.get('end_date') or date.today().isoformat()

    query = """
        SELECT tasks.id, tasks.task, tasks.comments, tasks.task_date, tasks.time_spent, projects.name
        FROM tasks
        JOIN projects ON tasks.project_id = projects.project_id
        WHERE tasks.user_id = %s
    """
    params = [current_user.user_id]

    if project_filter:
        query += " AND projects.name = %s"
        params.append(project_filter)
    if start_date:
        query += " AND tasks.task_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND tasks.task_date <= %s"
        params.append(end_date)

    query += " ORDER BY tasks.task_date DESC"

    cur.execute(query, tuple(params))
    tasks = cur.fetchall()

    return render_template("index.html", projects=projects, tasks=tasks, current_date=date.today().isoformat())

@app.route("/submit", methods=["POST"])
@login_required
def submit():
    data = request.get_json()
    task = data.get("task")
    comments = data.get("comments")
    task_date = data.get("task_date")
    project_id = data.get("project")
    time_spent = data.get("time_spent")

    cur.execute(
        "INSERT INTO tasks (task, comments, task_date, project_id, time_spent, user_id) VALUES (%s, %s, %s, %s, make_interval(mins => %s), %s)",
        (task, comments, task_date, project_id, time_spent, current_user.user_id)
    )
    conn.commit()
    return "Saved!"

@app.route("/aggregate")
@login_required
def aggregate():
    current_month = datetime.now().strftime('%Y-%m')

    cur.execute("""
        SELECT tasks.task, tasks.comments, tasks.task_date, tasks.time_spent, projects.name AS project_name
        FROM tasks
        JOIN projects ON tasks.project_id = projects.project_id
        WHERE tasks.user_id = %s AND TO_CHAR(tasks.task_date, 'YYYY-MM') = %s
        ORDER BY tasks.task_date DESC
    """, (current_user.user_id, current_month))
    task_details = cur.fetchall()

    cur.execute("""
        SELECT
            TO_CHAR(task_date, 'YYYY-MM') AS month,
            SUM(time_spent) AS total_time
        FROM tasks
        WHERE user_id = %s
        GROUP BY month
        ORDER BY month DESC
    """, (current_user.user_id,))
    monthly_totals = cur.fetchall()

    return render_template("aggregate.html", task_details=task_details, monthly_totals=monthly_totals)

@app.template_filter('format_month')
def format_month(value):
    try:
        return datetime.strptime(value, "%Y-%m").strftime("%B %Y")
    except Exception:
        return value

@app.route("/delete_task/<int:task_id>", methods=["GET"])
@login_required
def delete_task(task_id):
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, current_user.user_id))
    conn.commit()
    return redirect("/")

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    if request.method == "POST":
        task = request.form["task"]
        comments = request.form["comments"]
        task_date = request.form["task_date"]
        project_id = request.form["project"]  # Now it will be the project ID
        time_spent = request.form["time_spent"]

        # Execute the update query with the correct project_id
        cur.execute("""
            UPDATE tasks
            SET task = %s, comments = %s, task_date = %s, project_id = %s, time_spent = make_interval(mins => %s)
            WHERE id = %s AND user_id = %s
        """, (task, comments, task_date, project_id, time_spent, task_id, current_user.user_id))
        conn.commit()
        return redirect("/")
    else:
        # Fetch the task for the given task_id
        cur.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, current_user.user_id))
        task = cur.fetchone()
        if not task:
            return "Task not found or access denied", 404

        # Fetch all projects to show in the dropdown
        cur.execute("SELECT project_id, name FROM projects")
        projects = cur.fetchall()

        return render_template("edit_task.html", task=task, projects=projects)

@app.route("/admin", methods=["GET"])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return "Access denied", 403
    return render_template("admin/dashboard.html")

@app.route("/admin/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        return "Access denied", 403

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_admin = request.form.get("is_admin") == "on"

        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            return "Username already exists", 400

        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                    (username, hashed_pw, is_admin))
        conn.commit()
        return redirect("/admin/users")

    return render_template("admin/create_user.html")

@app.route("/admin/logs")
@login_required
def view_logs():
    if not current_user.is_admin:
        return "Access denied", 403

    with open("app.log") as f:
        lines = f.readlines()[-100:]  # Get last 100 lines

    return render_template("admin/logs.html", logs=lines)


@app.route("/admin/stats")
@login_required
def admin_stats():
    if not current_user.is_admin:
        return "Access denied", 403

    cur.execute("""
        SELECT username, SUM(EXTRACT(EPOCH FROM time_spent)/60) AS total_minutes
        FROM tasks
        JOIN users ON tasks.user_id = users.user_id
        GROUP BY username
        ORDER BY total_minutes DESC
    """)
    user_stats = cur.fetchall()

    return render_template("admin/stats.html", user_stats=user_stats)

@app.route("/admin/projects", methods=["GET", "POST"])
@login_required
def manage_projects():
    if not current_user.is_admin:
        return "Access denied", 403

    if request.method == "POST":
        project_name = request.form["name"]
        project_description = request.form["description"]

        cur.execute("INSERT INTO projects (name, description) VALUES (%s, %s)", (project_name, project_description))
        conn.commit()
        return redirect("/admin/projects")

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()

    return render_template("admin/admin_projects.html", projects=projects)

@app.route("/admin/projects/delete/<int:project_id>")
@login_required
def delete_project(project_id):
    if not current_user.is_admin:
        return "Access denied", 403

    cur.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
    conn.commit()
    return redirect("/admin/projects")

@app.route("/add_project", methods=["GET", "POST"])
@login_required
def add_project():
    if request.method == "POST":
        project_name = request.form["project_name"].strip()

        if not project_name:
            return "Project name cannot be empty", 400

        cur.execute("SELECT COUNT(*) FROM projects WHERE name = %s", (project_name,))
        count = cur.fetchone()[0]
        if count > 0:
            return "Project already exists", 400

        cur.execute("INSERT INTO projects (name) VALUES (%s)", (project_name,))
        conn.commit()
        return redirect("/")
    else:
        return render_template("add_project.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
