from flask import Flask, render_template, redirect, url_for, request, session
from models import db, user
from werkzeug.security import check_password_hash, generate_password_hash


app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dulieunguoidung.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.app_context():
    db.create_all()


app.secret_key = "sdkhfhoshfsm%#$"

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/rank")
def rank():
    leaderboard = [
        {"name": "NIGHTFALL", "role": "SQUAD LEADER", "score": "18,420", "kd": "4.82", "wins": "26", "online": True},
        {"name": "RAVEN_07", "role": "RECON", "score": "16,905", "kd": "4.35", "wins": "22", "online": True},
        {"name": "MAMBA", "role": "ASSAULT", "score": "15,770", "kd": "3.98", "wins": "19", "online": False},
        {"name": "GHOSTLINE", "role": "SUPPORT", "score": "14,210", "kd": "3.64", "wins": "17", "online": True},
        {"name": "IRON_HAWK", "role": "BREACHER", "score": "13,884", "kd": "3.41", "wins": "15", "online": False},
        {"name": "DELTAFOX", "role": "MEDIC", "score": "12,608", "kd": "3.09", "wins": "13", "online": True},
    ]
    return render_template("rank.html", leaderboard=leaderboard)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        account = user.query.filter_by(username=username).first()
        if account and check_password_hash(account.password, password):
            session["username"] = account.username
            return redirect(url_for("home"))
        error = "Sai tên đăng nhập hoặc mật khẩu."
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if len(username) < 3:
            error = "Tên đăng nhập cần ít nhất 3 ký tự."
        elif len(password) < 6:
            error = "Mật khẩu cần ít nhất 6 ký tự."
        elif password != confirm_password:
            error = "Mật khẩu xác nhận không trùng khớp."
        elif user.query.filter_by(username=username).first():
            error = "Tên đăng nhập này đã được sử dụng."
        else:
            account = user(username=username, password=generate_password_hash(password))
            db.session.add(account)
            db.session.commit()
            session["username"] = account.username
            return redirect(url_for("home"))
    return render_template("register.html", error=error)

@app.route("/user", methods=["GET", "POST"])
def user_login_legacy():
    return redirect(url_for("login"), code=307 if request.method == "POST" else 302)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)



