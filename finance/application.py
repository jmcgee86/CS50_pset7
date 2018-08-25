import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        print("post buy execute")
        if not request.form.get("stockSymbol"):
            return apology("must enter a stock symbol")
        elif not request.form.get("quant"):
            return apology("must enter number of shares")

        symbol = request.form.get("stockSymbol")
        quote = lookup(symbol)

        if not quote:
            return apology("must enter valid stock symbol")

        user = db.execute("SELECT cash FROM users WHERE id=:userId;", userId=session["user_id"])
        userBalance = float(user[0]["cash"])
        totalCost = quote["price"]*int(request.form.get("quant"))
        if totalCost>userBalance:
            return apology("not enough funds for purchase")
        else:
            db.execute("INSERT INTO stocks (symbol, shares, price, user_id) VALUES (:symbol, :shares, :price, :user_id);", symbol=symbol, shares=request.form.get("quant"), price=quote['price'], user_id=session["user_id"])
            db.execute("UPDATE users SET cash=cash-:cost WHERE id=:userId;", cost=totalCost, userId=session["user_id"])
            print("bought stocks")
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must enter a stock symbol")
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if quote:
            return render_template("display.html", quote=quote, price=usd(quote["price"]))
        else:
            return apology("must enter valid stock symbol")

    else:
        return render_template("quote.html")

@app.route("/display")
@login_required
def display():
    """display quote"""
    return render_template("display.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("username must be entered", 403)
        elif not request.form.get("password"):
            return apology("must enter a password", 403)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password confirmation must match password")

        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username=request.form.get("username"), hash = generate_password_hash(request.form.get("password")))
        if not result:
            return apology("username already exists")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/")
        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
