import os, random, pip

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helper import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bjj_app.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return redirect("/logininvalid")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """register user"""
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("missing username")
        elif not request.form.get("password"):
            return apology("missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("confirmation missmatch")

        username = request.form.get("username")
        password = request.form.get("password")
        hash = generate_password_hash(password)


        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 0:
            print("Name already taken or already existing account")
            return apology("Name already taken or already existing account")

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
        id = db.execute("SELECT id FROM users WHERE username = :username AND hash = :hash", username=username, hash=hash)
        user_id = id[0]['id']
        for h in range(2):
            for i in range(5):
                db.execute("INSERT INTO streak (rank, points, game, userid) VALUES (:rank, :points, :game, :userid)", rank=i, points=0, game=h, userid=user_id)

        return redirect("/")


    else:
        return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        index=request.form.get("index")
        if index == 'visualise':
            return redirect("/visualise")
        elif index == 'modify':
            return redirect("/modify")
        return render_template("index.html")

@app.route("/features", methods=["GET", "POST"])
@login_required
def features():
    if request.method == "GET":
        return render_template("features.html")




@app.route("/invite", methods=["GET", "POST"])
@login_required
def invite():
    if request.method == "GET":
        return render_template("invite.html")



@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    rows1 = db.execute("SELECT * FROM positions WHERE userid = :id", id=session["user_id"])
    rows2 = db.execute("SELECT * FROM techniques WHERE userid = :id", id=session["user_id"])
    if request.method == "GET":
        return render_template("modify.html", rows1=rows1, rows2=rows2)
    else:
        modify=request.form.get("modify")
        if modify == 'positions':
            return redirect("/positions")
        elif modify == 'techniques':
            if len(rows1) <= 1:
                return apology("Not enough positions, please insert more in the position menu")
            return redirect("/techniques")
        return render_template("modify.html", rows1=rows1, rows2=rows2)




@app.route("/visualise", methods=["GET", "POST"])
@login_required
def visualise():
    rows1 = db.execute("SELECT * FROM positions WHERE userid = :id", id=session["user_id"])
    rows2 = db.execute("SELECT * FROM techniques WHERE userid = :id", id=session["user_id"])
    if request.method == "GET":
        return render_template("visualise.html", rows1=rows1, rows2=rows2)
    else:
        visualise=request.form.get("visualise")
        if visualise == 'solution':
            return redirect("/solution")
        elif visualise == 'run':
            return redirect("/run")
        return render_template("visualise.html", rows1=rows1, rows2=rows2)




@app.route("/techniques", methods=["GET", "POST"])
@login_required
def techniques():
    if request.method == "GET":
        return render_template("techniques.html")
    else:
        select = request.form.get("select")

        b_t1 = request.form.get("b_t1")
        pos1 = request.form.get("position1")
        name = request.form.get("technique")
        difficulty = request.form.get("difficulty")
        b_t2 = request.form.get("b_t2")
        pos2 = request.form.get("position2")

        row1 = db.execute("SELECT * FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t",
                          id=session["user_id"], position=pos1, b_t=b_t1)
        if len(row1) == 0:
            return apology("Origin position must be provided")
        pos_id1 = db.execute("SELECT pos_id FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t LIMIT 1",
                             id=session["user_id"], position=pos1, b_t=b_t1)
        if pos_id1:
            pos_id1 = pos_id1[0]["pos_id"]

        row2 = db.execute("SELECT * FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t",
                          id=session["user_id"], position=pos2, b_t=b_t2)
        if len(row2) == 0:
            return apology("Ending position must be provided")
        pos_id2 = db.execute("SELECT pos_id FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t LIMIT 1",
                             id=session["user_id"], position=pos2, b_t=b_t2)
        if pos_id2:
            pos_id2 = pos_id2[0]["pos_id"]

        row = db.execute("SELECT * FROM techniques WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                         id=session["user_id"], name=name, pos_id1=pos_id1, pos_id2=pos_id2)
        if select == "insert":
            if difficulty.isdigit() == False:
                return apology("Please provide a difficulty rating")
            if len(row) != 0:
                return apology("Technique already registered in your database")
            db.execute("INSERT INTO techniques (pos_id1, name, pos_id2, difficulty, favorite, userid) VALUES (:pos_id1, :name, :pos_id2, :difficulty, :favorite, :id)",
                       pos_id1=pos_id1, name=name, pos_id2=pos_id2, difficulty=difficulty, favorite='/', id=session["user_id"])
            return render_template("techniques.html")

        elif select == "delete":
            if len(row) == 0:
                return apology("Technique not registered in you database")
            db.execute("DELETE FROM techniques WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                       id=session["user_id"], name = name, pos_id1=pos_id1, pos_id2=pos_id2)
            return render_template("positions.html")

        elif select == "upgrade":
            if len(row) == 0:
                return apology("Technique not registered in you database")
            if difficulty.isdigit() == False:
                db.execute("UPDATE techniques SET favorite = ';]' WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                           id=session["user_id"], name = name, pos_id1=pos_id1, pos_id2=pos_id2)
                return render_template("techniques.html")
            db.execute("UPDATE techniques SET favorite = ';]', difficulty = :difficulty WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                       id=session["user_id"], name = name, pos_id1=pos_id1, pos_id2=pos_id2, difficulty=difficulty)

        elif select == "downgrade":
            if len(row) == 0:
                return apology("Technique not registered in you database")
            if difficulty.isdigit() == False:
                db.execute("UPDATE techniques SET favorite = '/' WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                           id=session["user_id"], name = name, pos_id1=pos_id1, pos_id2=pos_id2)
                return render_template("techniques.html")
            db.execute("UPDATE techniques SET favorite = '/', difficulty = :difficulty WHERE userid = :id AND name = :name AND pos_id1 = :pos_id1 AND pos_id2 = :pos_id2",
                       id=session["user_id"], name = name, pos_id1=pos_id1, pos_id2=pos_id2, difficulty=difficulty)

        else:
            return apology("Please select your action")

        return render_template("techniques.html")





@app.route("/positions", methods=["GET", "POST"])
@login_required
def positions():
    print("Route hit")
    if request.method == "GET":
        return render_template("positions.html")
    else:
        select = request.form.get("select")
        position = request.form.get("position")
        b_t = request.form.get("b_t")
        print(f"select: {select}, position: {position}, b_t: {b_t}")
        rows = db.execute("SELECT * FROM positions WHERE userid = :id AND name = :position",
                          id=session["user_id"], position=position)

        if b_t == 'bottom' or b_t == 'top':

            rows = db.execute("SELECT * FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t",
                              id=session["user_id"], position=position, b_t=b_t)
            if select == "insert":
                if len(rows) != 0:
                    print("Already inserted position")
                    return apology("Already inserted position")
                db.execute("INSERT INTO positions (name, userid, b_t, favorite) VALUES (:name, :id, :b_t, :favorite)",
                       name = position, id=session["user_id"], b_t = b_t, favorite = '/')
                return render_template("positions.html")
            elif select == "delete":
                if len(rows) == 0:
                    print("No position with this name to be found")
                    return apology("No position with this name to be found")
                db.execute("DELETE FROM positions WHERE userid = :id AND name = :position AND b_t = :b_t",
                           id=session["user_id"], position = position, b_t = b_t)
                return render_template("positions.html")

            elif select == 'upgrade':
                db.execute("UPDATE positions SET favorite = ';]' WHERE userid = :id AND name = :position AND b_t = :b_t",
                           id=session["user_id"], position=position, b_t=b_t)
                return render_template("positions.html")
            elif select == 'downgrade':
                db.execute("UPDATE positions SET favorite = '/' WHERE userid = :id AND name = :position AND B_t = :b_t",
                           id=session["user_id"], position=position, b_t=b_t)
                return render_template("positions.html")
            else:
                return apology("Please select your action")


        elif b_t == 'both':
            if select == "insert":
                if len(rows) != 0:
                    print("Already inserted position")
                    return apology("Already inserted position")
                db.execute("INSERT INTO positions (name, userid, b_t, favorite) VALUES (:name, :id, :b_t, :favorite)",
                       name = position, id=session["user_id"], b_t = 'top', favorite = '/')
                db.execute("INSERT INTO positions (name, userid, b_t, favorite) VALUES (:name, :id, :b_t, :favorite)",
                       name = position, id=session["user_id"], b_t = 'bottom', favorite = '/')
                return render_template("positions.html")

            elif select == "delete":
                if len(rows) == 0:
                    print("No position with this name to be found")
                    return apology("No position with this name to be found")
                db.execute("DELETE FROM positions WHERE userid = :id AND name = :position",
                           id=session["user_id"], position = position)
                return render_template("positions.html")

            elif select == 'upgrade':
                db.execute("UPDATE positions SET favorite = ';]' WHERE userid = :id AND name = :position",
                           id=session["user_id"], position=position)
                return render_template("positions.html")

            elif select == 'downgrade':
                db.execute("UPDATE positions SET favorite = '/' WHERE userid = :id AND name = :position",
                           id=session["user_id"], position=position)
                return render_template("positions.html")
            else:
                return apology("Please select your action")


        else:
            print("Incorrect input Selected")
            return apology("Incorrect input Selected")





@app.route("/solution", methods=["GET", "POST"])
@login_required
def solution():
    streak = db.execute("SELECT * FROM streak WHERE userid = :id AND game=1 ORDER BY points DESC LIMIT 1", id=session["user_id"])
    if "points" not in session:
        session["points"] = 0
    points = session["points"]
    if request.method == "GET":
        random_position1 = db.execute("SELECT positions.pos_id, positions.name FROM positions JOIN techniques ON techniques.pos_id1 = positions.pos_id WHERE positions.userid = :id AND techniques.userid = :id  ORDER BY RANDOM() LIMIT 1",
                                    id=session["user_id"])
        pos_id1 = random_position1[0]["pos_id"]
        session["pos_id1"] = pos_id1
        random_position1 = random_position1[0]["name"]

        random_position2 = db.execute("SELECT pos_id2 FROM techniques WHERE pos_id1 = :pos_id1 AND userid = :id ORDER BY RANDOM() LIMIT 1",
                             pos_id1=pos_id1, id=session["user_id"])

        pos_id2 = random_position2[0]["pos_id2"]
        session["pos_id2"] = pos_id2
        random_position2 = db.execute("SELECT name FROM positions WHERE pos_id = :pos_id2 AND userid = :id",
                                      pos_id2=pos_id2, id=session["user_id"])
        random_position2 = random_position2[0]["name"]

        points = 0
        session["points"] = points

        return render_template("solution.html", random_position1=random_position1, random_position2=random_position2, points=points, streak=streak)

    else:
        technique = request.form.get("technique")
        pos_id1 = session["pos_id1"]
        pos_id2 = session["pos_id2"]
        rows = db.execute("SELECT name FROM techniques WHERE pos_id1 = :pos_id1 AND pos_id2 = :pos_id2 AND userid = :id",
                          pos_id1=pos_id1, pos_id2=pos_id2, id=session["user_id"])
        for i in range(len(rows)):
            if technique == rows[i]["name"] :
                points += 1
                session["points"] = points
                random_position1 = db.execute("SELECT positions.pos_id, positions.name FROM positions JOIN techniques ON techniques.pos_id1 = positions.pos_id WHERE positions.userid = :id AND techniques.userid = :id ORDER BY RANDOM() LIMIT 1",
                                            id=session["user_id"])
                pos_id1 = random_position1[0]["pos_id"]
                session["pos_id1"] = pos_id1
                random_position1 = random_position1[0]["name"]

                random_position2 = db.execute("SELECT pos_id2 FROM techniques WHERE pos_id1 = :pos_id1 AND userid = :id ORDER BY RANDOM() LIMIT 1",
                                    pos_id1=pos_id1, id=session["user_id"])

                pos_id2 = random_position2[0]["pos_id2"]
                session["pos_id2"] = pos_id2
                random_position2 = db.execute("SELECT name FROM positions WHERE pos_id = :pos_id2 AND userid = :id",
                                            pos_id2=pos_id2, id=session["user_id"])
                random_position2 = random_position2[0]["name"]

                return render_template("solution.html", random_position1=random_position1, random_position2=random_position2, points=points, streak=streak)

            points = session["points"]
            if streak[0]["points"] <= points:
                db.execute("INSERT INTO streak (points, userid, game) VALUES (:points, :id, :game)",
                           points = points, id=session["user_id"], game=1)

            return redirect("/solution")








@app.route("/run", methods=["GET", "POST"])
@login_required
def run():
    streak = db.execute("SELECT * FROM streak WHERE userid = :id AND game=0 ORDER BY points DESC LIMIT 1", id=session["user_id"])
    if "points" not in session:
        session["points"] = 0
    points = session["points"]
    if request.method == "GET":
        random_position1 = db.execute("SELECT positions.pos_id, positions.name FROM positions JOIN techniques ON techniques.pos_id1 = positions.pos_id WHERE positions.userid = :id AND techniques.userid = :id  ORDER BY RANDOM() LIMIT 1",
                                    id=session["user_id"])
        pos_id1 = random_position1[0]["pos_id"]
        session["pos_id1"] = pos_id1
        random_position1 = random_position1[0]["name"]

        random_position2 = db.execute("SELECT pos_id2 FROM techniques WHERE pos_id1 = :pos_id1 AND userid = :id ORDER BY RANDOM() LIMIT 1",
                             pos_id1=pos_id1, id=session["user_id"])

        pos_id2 = random_position2[0]["pos_id2"]
        session["pos_id2"] = pos_id2
        random_position2 = db.execute("SELECT name FROM positions WHERE pos_id = :pos_id2 AND userid = :id",
                                      pos_id2=pos_id2, id=session["user_id"])
        random_position2 = random_position2[0]["name"]

        points = 0
        session["points"] = points

        return render_template("run.html", random_position1=random_position1, random_position2=random_position2, points=points, streak=streak)

    else:
        technique = request.form.get("technique")
        pos_id1 = session["pos_id1"]
        pos_id2 = session["pos_id2"]
        rows = db.execute("SELECT name FROM techniques WHERE pos_id1 = :pos_id1 AND pos_id2 = :pos_id2 AND userid = :id",
                          pos_id1=pos_id1, pos_id2=pos_id2, id=session["user_id"])
        for i in range(len(rows)):
            if technique == rows[i]["name"] :
                points += 1
                session["points"] = points

                pos_id1 = pos_id2
                session["pos_id1"] = pos_id1
                random_position1 = db.execute("SELECT name FROM positions WHERE pos_id = :pos_id1 AND userid = :id",
                                            pos_id1=pos_id1, id=session["user_id"])
                random_position1 = random_position1[0]["name"]
                random_position2 = db.execute("SELECT * FROM techniques WHERE pos_id1 = :pos_id1 AND userid = :id ORDER BY RANDOM() LIMIT 1",
                              pos_id1=pos_id1, id=session["user_id"])

                if not random_position2:
                    points = session["points"]
                    if streak[0]["points"] <= points:
                        db.execute("INSERT INTO streak (points, userid, game) VALUES (:points, :id, :game)",
                                   points = points, id=session["user_id"], game=0)
                    return redirect("/run")

                pos_id2 = random_position2[0]["pos_id2"]
                session["pos_id2"] = pos_id2
                random_position2 = db.execute("SELECT name FROM positions WHERE pos_id = :pos_id2 AND userid = :id",
                                            pos_id2=pos_id2, id=session["user_id"])
                random_position2 = random_position2[0]["name"]

                return render_template("run.html", random_position1=random_position1, random_position2=random_position2, points=points, streak=streak)


            points = session["points"]
            if streak[0]["points"] <= points:
                db.execute("INSERT INTO streak (points, userid, game) VALUES (:points, :id, :game)",
                           points = points, id=session["user_id"], game=0)

            return redirect("/run")

pos_id1 = 0
pos_id2 = 0
