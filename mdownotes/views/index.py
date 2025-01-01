import hashlib
import uuid
import flask
import mdownotes
import mdownotes.model


@mdownotes.app.route('/', methods=["GET"])
def show_index():
    """Display / route."""
    # check if client is logged in
    #if "username" in flask.session:
    #    logname = flask.session["username"]
    #else:
    #    return flask.redirect("/accounts/login/")
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y = cursor.execute(
        "SELECT * FROM categories"
        ).fetchall()
    #print("y")
    #print(y)
    context = {"logname": logname,
               "cat_list": y}
    return flask.render_template("index.html", **context)

@mdownotes.app.route('/', methods=["POST"])
def create_category():
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO categories(desc) "
        "VALUES(?)",
        (flask.request.form["New Category"],)
        )
    return flask.redirect("/")


@mdownotes.app.route('/<cat_id>/', methods=["GET"])
def show_category(cat_id):
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y = cursor.execute(
        "SELECT * FROM categories "
        "WHERE categoryid = ?",
        (cat_id, )
        ).fetchall()
    d = len(y)
    if d == 0:
        flask.abort(404)
    assert(d == 1)
    z = cursor.execute(
        "SELECT * FROM videos "
        "WHERE categoryid = ?",
        (cat_id, )
        ).fetchall()
    context = {
        "category" : y[0]["desc"],
        "vid_list": z,
        "categoryid": cat_id
    }
    return flask.render_template("category.html", **context)

@mdownotes.app.route('/<cat_id>/', methods=["POST"])
def make_video(cat_id):
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y = cursor.execute(
        "SELECT * FROM categories "
        "WHERE categoryid = ?",
        (cat_id, )
        ).fetchall()
    d = len(y)
    if d == 0:
        flask.abort(404)
    assert(d == 1)
    url = flask.request.form["url"]
    pos = url.find("?v=")
    if pos == -1:
        flask.abort(403)
    url = url[pos+3:]
    pos = url.find("&")
    if pos != -1:
        url = url[:pos]
    #print("This should be just the nonce now")
    #print(url)
    
    # prevent double video, this allows us to use cat + uniqvid 
    y = cursor.execute(
        "SELECT * FROM videos "
        "WHERE categoryid = ? "
        "AND url = ?",
        (cat_id, url)
        ).fetchall()
    if len(y) == 1:
        return flask.redirect(f"/{cat_id}/")
    
    cursor.execute(
            "INSERT INTO videos(url, title, categoryid) "
            "VALUES(?, ?, ?)",
            (url, flask.request.form["title"], cat_id)
        )
    return flask.redirect(f"/{cat_id}/")


@mdownotes.app.route('/<cat_id>/<nonce>/', methods=["GET"])
def serve_video_page(cat_id, nonce):
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y = cursor.execute(
        "SELECT * FROM categories "
        "WHERE categoryid = ?",
        (cat_id, )
        ).fetchall()
    d = len(y)
    if d == 0:
        flask.abort(404)
    assert(d == 1)
    # ensure the video is in our database
    z = cursor.execute(
        "SELECT * FROM videos "
        "WHERE categoryid = ? "
        "AND url = ? ",
        (cat_id, nonce)
        ).fetchall()
    d = len(z)
    if d == 0:
        flask.abort(404)
    assert(d == 1)
    context = {
        "VIDEO_ID": nonce,
        "title": z[0]["title"],
        "id": cat_id
    }
    return flask.render_template("video.html", **context)

@mdownotes.app.route('/login/', methods=["GET"])
def login():
    """Render login page."""
    if "username" in flask.session:
        return flask.redirect("/")
    return flask.render_template('login.html')

@mdownotes.app.route('/delete_cat/', methods=["POST"])
def delete_cat():
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    id = flask.request.form["id"]
    if flask.request.form["confirm"] != "Confirm Delete":
        return flask.redirect(f"/{id}/")
    cursor.execute(
            "DELETE FROM categories "
            "WHERE categoryid = ?",
            (int(id),)
        )
    return flask.redirect("/")


@mdownotes.app.route('/delete_vid/', methods=["POST"])
def delete_vid():
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    id = flask.request.form["id"]
    nonce = flask.request.form["nonce"]
    if flask.request.form["confirm"] != "Confirm Delete":
        return flask.redirect(f"/{id}/{nonce}")
    cursor.execute(
            "DELETE FROM videos "
            "WHERE categoryid = ? "
            "AND url = ?",
            (id,nonce)
        )
    return flask.redirect(f"/{id}/")
    # get the form value for the category id
    
    
    

@mdownotes.app.route("/accounts/", methods=["POST"])
def post_accounts():
    """POST METHOD: Accounts."""
    cursor = mdownotes.model.get_db().cursor()

    if flask.request.form["operation"] == "login":
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        # Check if username and password fields are invalid
        null_checker(username, password)

        if user_authentication(username, password, cursor):
            # Set the cookies!!!
            flask.session["username"] = username

            return flask.redirect(p_tar(flask.request.args.get('target')))
        # Password did not match
        flask.abort(403)

    # create operation
    elif flask.request.form["operation"] == "create":

        username = flask.request.form["username"]
        password = flask.request.form["password"]

        # make sure form was complete
        null_checker(username, password)

        # request to see if user exists already in table
        cur = cursor.execute(
            "SELECT username "
            "FROM users "
            "WHERE username = ?",
            (username,)
        )
        # login_list = cur.fetchall()
        if len(cur.fetchall()) != 0:
            flask.abort(409)

        # Please keep note that save() method edits the uploads dir
        # We are doing this to save 1 local variable count lol
        cursor.execute(
            "INSERT INTO users(username, password) "
            "VALUES(?,?) ",
            (username, get_db_ps_str(password))
            )
        # now we copy behavior of login operation
        flask.session["username"] = username
        return flask.redirect(p_tar(flask.request.args.get('target')))

    # delete operation
    elif flask.request.form["operation"] == "delete":
        not_logged_abort()
        # connection = insta485.model.get_db()
        # cursor = connection.cursor()
        if flask.request.form["confirm"] != "Confirm Delete":
            flask.abort(403)
        logname = flask.session["username"]

        # do the delete cascade
        cursor.execute("DELETE FROM users WHERE username = ?", (logname,))

        flask.session.pop("username", None)
        return flask.redirect(p_tar(flask.request.args.get('target')))

    elif flask.request.form["operation"] == "update_password":
        not_logged_abort()
        password = flask.request.form["password"]
        password1 = flask.request.form["new_password1"]
        password2 = flask.request.form["new_password2"]
        null_checker(password, password1, password2)

        # make sure form was right in its reqs
        if user_authentication(flask.session["username"], password, cursor):
            if password1 != password2:
                flask.abort(401)
        else:
            flask.abort(403)

        # update the password
        cursor.execute(
            'UPDATE users SET password = ?'
            ' WHERE username = ?',
            (get_db_ps_str(password1), flask.session["username"])
            )
        return flask.redirect(p_tar(flask.request.args.get('target')))
    flask.abort(500)

def null_checker(*args):
    """POST METHOD: Accounts helper."""
    for arg in args:
        if arg is None:
            # flask.abort(400)
            context = {
                "message": "Bad Request",
                "status_code": 400
            }
            return flask.jsonify(**context), 400
    return None

def p_tar(target):
    """POST METHOD: Accounts helper."""
    if target is None:
        target = "/"
    return target

def get_db_ps_str(password: str):
    """POST METHOD Helper: get databse password."""
    # Given a password, generates salted hash password string to put
    # into the user database, with unique identifier
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string

def user_authentication(username: str, password: str, cursor):
    """POST METHOD: Accounts helper.

    returns True if user successfully authenticates
    returns False if users does not
    """
    # Check if username is valid
    login_cur = cursor.execute(
        "SELECT username, password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )
    login_list = login_cur.fetchall()
    if len(login_list) == 0:
        flask.abort(403)

    # Get the password from the db and parse it
    password_db = login_list[0]["password"]
    password_parts = password_db.split('$')

    # Check the password and salt
    parsed_password = password_parts[-1]
    salt = password_parts[-2]
    algorithm = "sha512"

    m = hashlib.new(algorithm)
    m.update((salt + password).encode('utf-8'))
    password_hash = m.hexdigest()

    return password_hash == parsed_password

def not_logged_abort():
    """POST METHOD: aborts if the user is not logged in """
    if "username" not in flask.session:
        flask.abort(403)
        

@mdownotes.app.route("/users/<user_url_slug>/", methods = ["GET"])
def render_user_page(user_url_slug):
    """Render the user's information onto the user's page."""
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()

    # check for existence
    # query the users table for the dudes name
    cur = cursor.execute(
        "SELECT username FROM users WHERE username = ?", (user_url_slug,)
        )
    y = cur.fetchall()
    if len(y) == 0:
        flask.abort(404)
    context = {"username": user_url_slug,
               "logname": logname}
    
    return flask.render_template("user.html", **context)


@mdownotes.app.route('/logout/', methods = ["POST"])
def logout():
    """POST METHOD: Logout."""
    flask.session.pop('username', None)  # Remove username from session
    return flask.redirect("/login/")

@mdownotes.app.route('/create/', methods = ["GET"])
def create_acc():
    """Create account."""
    if "username" in flask.session:
        return flask.redirect("/")
    return flask.render_template("create.html")

@mdownotes.app.route('/edit/', methods = ["GET"])
def edit_acc():
    """Delete account"""
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    context = {"logname": logname}
    return flask.render_template("edit_acc.html", **context)

    