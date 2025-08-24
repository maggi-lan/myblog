from flask import Flask, g, redirect, render_template, request, session
from flask_wtf import FlaskForm
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp

from config import Config
from helper import apology, get_db, login_required, time_ago, pfp_check

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config.from_object(Config)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 20), Regexp("^[a-z0-9-_]+$", message="Username can only contain lowercase letters, digits, underscore and hyphen")])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 64)])
    submit = SubmitField("Submit")

class RegisterForm(LoginForm):
    check = PasswordField("Confirm Password", validators=[DataRequired(), Length(8, 64)])

class PostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Submit")

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(max=50)])
    bio = TextAreaField("Bio", validators=[Length(max=300)])
    submit = SubmitField("Submit")

class FollowForm(FlaskForm):
    submit = SubmitField("Submit")




@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    db = get_db()
    cursor = db.cursor()

    if form.validate_on_submit():
        content = form.content.data
        cursor.execute("INSERT INTO posts (user_id, content, post_time) VALUES (?, ?, CURRENT_TIMESTAMP)", (session["user_id"], content))
        db.commit()
        return redirect("/")
    
    else:
        page = int(request.args.get("page", 1))
        per_page = 3
        offset = (page - 1) * per_page

        cursor.execute("SELECT posts.id, username, content, post_time, users.pfp FROM posts JOIN users ON users.id = user_id WHERE users.id IN (SELECT follows_id FROM follows WHERE follower_id = ? UNION SELECT ?) ORDER BY post_time DESC LIMIT ? OFFSET ?", (session["user_id"], session["user_id"], per_page, offset))
        posts = cursor.fetchall()
        for i in range(len(posts)):
            posts[i] = dict(posts[i])
            post = posts[i]
            post["post_time"] = time_ago(post["post_time"])

        cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id IN (SELECT follows_id FROM follows WHERE follower_id = ? UNION SELECT ?)", (session["user_id"], session["user_id"]))
        total_posts = cursor.fetchone()[0]
        total_pages = max(1, (total_posts + per_page - 1) // per_page)
        if page > total_pages:
            return apology("Invalid Page Number")
        return render_template("index.html", posts=posts, form=form, page=page, total_pages=total_pages)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.pop("user_id", None)
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cursor = get_db().cursor()
        cursor.execute("SELECT id, username, hash FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()

        if len(rows) != 1:
            form.username.errors.append("Username doesn't exist.")
            return render_template("login.html", form=form)
        if not check_password_hash(rows[0]["hash"], password):
            form.password.errors.append("Password doesn't match.")
            return render_template("login.html", form=form)
        
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        return redirect("/")
    else:
        return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.pop("user_id", None)
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()
        if len(rows) != 0:
            form.username.errors.append("Username already exists.")
            return render_template("register.html", form=form)
        
        password = form.password.data
        check = form.check.data
        if (password != check):
            form.check.errors.append("Passwords don't match.")
            return render_template("register.html", form=form)
        
        cursor.execute("INSERT INTO users (username, hash, pfp) VALUES (?, ?, '/static/images/1.jpg')", (username, generate_password_hash(password)))
        db.commit()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()
        session["user_id"] = rows[0]["id"]
        session["username"] = username
        return redirect("/")
    else:
        return render_template("register.html", form=form)
    

@app.route("/explore")
@login_required
def explore():
    cursor = get_db().cursor()

    page = int(request.args.get("page", 1))
    per_page = 5
    offset = (page - 1) * per_page

    cursor.execute("SELECT posts.id, username, content, post_time, users.pfp FROM posts JOIN users ON users.id = user_id ORDER BY post_time DESC LIMIT ? OFFSET ?", (per_page, offset))
    posts = cursor.fetchall()
    for i in range(len(posts)):
        posts[i] = dict(posts[i])
        post = posts[i]
        post["post_time"] = time_ago(post["post_time"])

    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]
    total_pages = (total_posts + per_page - 1) // per_page
    print(total_pages)
    return render_template("explore.html", posts=posts, page=page, total_pages=total_pages)


@app.route("/profile")
@login_required
def profile():
    cursor = get_db().cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
    username = cursor.fetchall()[0]["username"]
    return redirect(f"/profile/{username}")


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def user_profile(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, name, bio, pfp FROM users WHERE username = ?", (username,))
    details = cursor.fetchall()
    if not details:
        return apology("Username doesn't exist")
    details = details[0]

    form = EditProfileForm()

    if form.validate_on_submit():
        if session["user_id"] != details["id"]:
            return apology("Forbidden Access")
        
        name = form.name.data.strip() or None
        bio = form.bio.data.strip() or None
        pfp = request.form.get("pfp", details["pfp"])
        if not pfp_check(pfp):
            return apology("Invalid Request")

        db.execute("UPDATE users SET name = ?, bio = ?, pfp = ? WHERE id = ?", (name, bio, pfp, session["user_id"]))
        db.commit()
        return redirect(f"/profile/{username}")
        
    else:
        form.bio.data = details["bio"]

        follow_form = FollowForm()
        cursor.execute("SELECT 1 FROM follows WHERE (follower_id = ?) AND (follows_id = ?)", (session["user_id"], details["id"]))
        follow_bool = bool(cursor.fetchone())

        count = {}
        cursor.execute("SELECT COUNT(*) AS posts FROM posts WHERE user_id = ?", (details["id"],))
        count["posts"] = cursor.fetchone()["posts"]
        cursor.execute("SELECT COUNT(*) AS 'followers' FROM follows WHERE follows_id = ?", (details["id"],))
        count["followers"] = cursor.fetchone()["followers"]
        cursor.execute("SELECT COUNT(*) AS 'following' FROM follows WHERE follower_id = ?", (details["id"],))
        count["following"] = cursor.fetchone()["following"]
        

        page = int(request.args.get("page", 1))
        per_page = 3
        offset = (page - 1) * per_page

        cursor.execute("SELECT posts.id, username, content, post_time, users.pfp FROM posts JOIN users ON users.id = user_id WHERE username = ? ORDER BY post_time DESC LIMIT ? OFFSET ?", (username, per_page, offset))
        posts = cursor.fetchall()
        for i in range(len(posts)):
            posts[i] = dict(posts[i])
            post = posts[i]
            post["post_time"] = time_ago(post["post_time"])

        cursor.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", (details["id"],))
        total_posts = cursor.fetchone()[0]
        total_pages = (total_posts + per_page - 1) // per_page
        return render_template("profile.html", count=count, details=details, posts=posts, user_id=session["user_id"], form=form, follow_form=follow_form, follow_bool=follow_bool, page=page, total_pages=total_pages)
    

@app.route("/search", methods=["GET"])
@login_required
def search():
    q = request.args.get("q").strip()
    if not q or len(q) > 50:
        return apology("Invalid query")

    page = int(request.args.get("page", 1))
    per_page = 5
    offset = (page - 1) * per_page

    query = f"%{q}%"
    cursor = get_db().cursor()
    cursor.execute("SELECT username, name, pfp FROM users WHERE username LIKE ? OR name LIKE ? LIMIT ? OFFSET ?", (query, query, per_page, offset))
    rows = cursor.fetchall()
    if not rows:
        return apology("No Results Found")

    cursor.execute("SELECT COUNT(*) FROM users WHERE username LIKE ? OR name LIKE ?", (query, query))
    total_posts = cursor.fetchone()[0]
    total_pages = (total_posts + per_page - 1) // per_page
    return render_template("search.html", rows=rows, page=page, total_pages=total_pages, query=q)

@app.route("/delete", methods=["POST"])
@login_required
def delete():
    post_id = request.form.get("post_id")
    db = get_db()
    cursor = db.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    rows = cursor.fetchall()
    if not rows:
        return apology("Invalid Request")
    user_id = rows[0]["user_id"]

    if session["user_id"] != user_id:
        return apology("Forbidden Access")
    
    db.execute("DELETE FROM posts WHERE id = ?", (post_id, ))
    db.commit()

    route = request.form.get("route")
    return redirect(route)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def handle_follow(username):
    if session["username"] == username:
        return apology("User can't follow/unfollow themselves")
    
    form = FollowForm()  

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return apology("User doesn't exist")
    follows_id = user["id"]

    cursor.execute("SELECT 1 FROM follows WHERE (follower_id = ?) AND (follows_id = ?)", (session["user_id"], follows_id))
    following = bool(cursor.fetchone())

    if form.validate_on_submit():
        if not following:
            cursor.execute("INSERT INTO follows (follower_id, follows_id) VALUES (?, ?)", (session["user_id"], follows_id))
        else:
            cursor.execute("DELETE FROM follows WHERE (follower_id = ?) AND (follows_id = ?)", (session["user_id"], follows_id))
        
        db.commit()
        return redirect(f"/profile/{username}")
        
    return apology("Invalid Request")







@app.teardown_appcontext # this will automatically close the db connection after each request
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.errorhandler(404)
def page_not_found(e):
    return apology("Page Not Found", 404)

@app.errorhandler(500)
def internal_server_error(e):
    return apology("Internal Server Error", 500)