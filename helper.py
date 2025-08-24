from datetime import datetime, timezone
from flask import g, redirect, render_template, session
from sqlite3 import connect, Row
from functools import wraps

def apology(message, code=400):
    def escape(s):
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def get_db():
    if 'db' not in g:  # 'g' is a temporary storage object
        g.db = connect("blog.db") # 'db' is an attribute in which we are going to store the connection
        g.db.row_factory = Row  #rows will be a list while row will be an object
    return g.db

def login_required(main): # decorator function
    @wraps(main) # helps in importing some meta data to the inner function --> no use, it just makes stuff easier for the intepreter
    def inner(*args, **kwargs):  # args and kwargs already represent the arguements the main arguement recieves
        if not session.get("user_id"):
            return redirect("/login")
        return main(*args, **kwargs)
    return inner

def pfp_check(path):
    paths = [f"/static/images/{i}.jpg" for i in range(1, 8)]
    if path not in paths:
        return False
    return True

def time_ago(post_time):
    post_time = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    seconds = int((now - post_time).total_seconds())
    if seconds < 60:
        return f"{seconds} seconds" if (seconds != 1) else f"{seconds} second"
    elif seconds < 60*60:
        minutes =  seconds // 60
        return f"{minutes} minutes" if (minutes > 1) else f"{minutes} minute"
    elif seconds < 60*60*24:
        hours = seconds // (60 * 60) 
        return f"{hours} hours" if (hours > 1) else f"{hours} hour"
    else:
        days = seconds // (60*60*24)
        return f"{days} days" if (days > 1) else f"{days} day"
