import hashlib
import uuid
import flask
import arrow
import mdownotes
import mdownotes.model


def clean_notifs(cursor):
    cursor.execute(
        "DELETE FROM notifs "
        "WHERE notifid NOT IN (SELECT notifid FROM notifs ORDER BY notifid DESC LIMIT 100)"
        )

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
    clean_notifs(cursor)
    d = cursor.execute(
        "SELECT created, desc "
        "FROM notifs " 
        "ORDER BY notifid DESC "
        "LIMIT 25"
    ).fetchall()
    for a in d:
        a["created"] = arrow.get(a["created"]).humanize()
    for a in y:
        if  not (a["last_feed_activity"] is None):
            a["last_feed_activity"] = arrow.get(a["last_feed_activity"]).humanize()
        if  not (a["last_insdel"] is None):
            a["last_insdel"] = arrow.get(a["last_insdel"]).humanize()
    context = {"logname": logname,
               "cat_list": y,
               "notif_list": d}
    cursor.close()
    return flask.render_template("index.html", **context)

@mdownotes.app.route('/', methods=["POST"])
def create_category():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    d = flask.request.form["New Category"]
    cursor.execute(
        "INSERT INTO categories(desc) "
        "VALUES(?)",
        (d,)
        )
    cursor.execute("INSERT INTO notifs(desc) "
                "VALUES(?) ",
            (f"{logname} created category '{d}'", ))
    cursor.close()
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
    for a in z:
        if not (a["last_activity"] is None):
            a["last_activity"] = arrow.get(a["last_activity"]).humanize()
    context = {
        "category" : y[0]["desc"],
        "vid_list": z,
        "categoryid": cat_id
    }
    cursor.close()
    return flask.render_template("category.html", **context)

@mdownotes.app.route('/<cat_id>/', methods=["POST"])
def make_video(cat_id):
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y1 = cursor.execute(
        "SELECT * FROM categories "
        "WHERE categoryid = ?",
        (cat_id, )
        ).fetchall()
    d = len(y1)
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
    
    # the url is 100% not valid
    if len(url) != 11:
        flask.abort(403)
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
        cursor.close()
      
        return flask.redirect(f"/{cat_id}/")
    d1 = flask.request.form["title"]
    cursor.execute(
            "INSERT INTO videos(url, title, categoryid) "
            "VALUES(?, ?, ?)",
            (url, d1, cat_id)
        )
    cursor.execute( "UPDATE categories "                   
    "SET last_insdel = CURRENT_TIMESTAMP "
    "WHERE categoryid = ?", (cat_id)
    )
    cursor.execute("INSERT INTO notifs(desc) "
                "VALUES(?) ",
            (f"{logname} created video '{d1}' in category '{y1[0]["desc"]}'", ))
    
    cursor.close()
  
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
        "id": cat_id,
        "category": y[0]["desc"],
        "vididSQL": z[0]["vidid"]
    }
    cursor.close()
    
    return flask.render_template("video3.html", **context)

@mdownotes.app.route('/login/', methods=["GET"])
def login():
    """Render login page."""
    if "username" in flask.session:
        return flask.redirect("/")
    return flask.render_template('login.html')

@mdownotes.app.route('/delete_cat/', methods=["POST"])
def delete_cat():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    id = flask.request.form["id"]
    if flask.request.form["confirm"] != "Confirm Delete":
        cursor.close()
       
        return flask.redirect(f"/{id}/")
    y = cursor.execute(
        "SELECT desc FROM categories "
        "WHERE categoryid = ?",
        (int(id),)
    ).fetchall()
    if len(y) != 0:
        cursor.execute(
                "DELETE FROM categories "
                "WHERE categoryid = ?",
                (int(id),)
            )
        cursor.execute("INSERT INTO notifs(desc) "
                "VALUES(?) ",
                (f"{logname} deleted category '{y[0]["desc"]}'", ))
    cursor.close()
    
    return flask.redirect("/")


@mdownotes.app.route('/delete_vid/', methods=["POST"])
def delete_vid():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return flask.redirect("/login/")
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    id = flask.request.form["id"]
    nonce = flask.request.form["nonce"]
    if flask.request.form["confirm"] != "Confirm Delete":
        cursor.close()
        return flask.redirect(f"/{id}/{nonce}")
    y = cursor.execute(
            "SELECT title FROM videos "
            "WHERE categoryid = ? "
            "AND url = ?",
            (id,nonce)
    ).fetchall()
    if len(y) != 0:
        d = cursor.execute(
            "SELECT desc FROM categories "
            "WHERE categoryid = ? ",
            (id,)
        ).fetchall()
        cursor.execute("INSERT INTO notifs(desc) "
            "VALUES(?) ",
            (f"{logname} deleted video '{y[0]["title"]}' from category '{d[0]["desc"]}'", ))
        cursor.execute(
                "DELETE FROM videos "
                "WHERE categoryid = ? "
                "AND url = ?",
                (id,nonce)
            )
        cursor.execute( "UPDATE categories "                   
        "SET last_insdel = CURRENT_TIMESTAMP "
        "WHERE categoryid = ?", (id)
        )
    cursor.close()
  
    return flask.redirect(f"/{id}/")
    # get the form value for the category id
    
    
    

@mdownotes.app.route("/accounts/", methods=["POST"])
def post_accounts():
    """POST METHOD: Accounts."""
    

    if flask.request.form["operation"] == "login":
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        # Check if username and password fields are invalid
        null_checker(username, password)
        
        connection = mdownotes.model.get_db()
        cursor = connection.cursor()

        if user_authentication(username, password, cursor):
            # Set the cookies!!!
            flask.session["username"] = username
            cursor.close()
          
            return flask.redirect(p_tar(flask.request.args.get('target')))
        # Password did not match
        flask.abort(403)

    # create operation
    elif flask.request.form["operation"] == "create":

        username = flask.request.form["username"]
        password = flask.request.form["password"]

        # make sure form was complete
        null_checker(username, password)

        connection = mdownotes.model.get_db()
        cursor = connection.cursor()
        # request to see if user exists already in table
        cur = cursor.execute(
            "SELECT username "
            "FROM users "
            "WHERE username = ?",
            (username,)
        )
        # login_list = cur.fetchall()
        if len(cur.fetchall()) != 0:
            cursor.close()
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
        
        cursor.execute("INSERT INTO notifs(desc) "
            "VALUES(?) ",
            (f"welcome {username} to the secret society!", ))
        cursor.close()
       
        return flask.redirect(p_tar(flask.request.args.get('target')))

    # delete operation
    elif flask.request.form["operation"] == "delete":
        not_logged_abort()
        # connection = insta485.model.get_db()
        # cursor = connection.cursor()
        if flask.request.form["confirm"] != "Confirm Delete":
            flask.abort(403)
        logname = flask.session["username"]

        connection = mdownotes.model.get_db()
        cursor = connection.cursor()
        # do the delete cascade
        cursor.execute("DELETE FROM users WHERE username = ?", (logname,))

        flask.session.pop("username", None)
        
        cursor.execute("INSERT INTO notifs(desc) "
            "VALUES(?) ",
            (f"{logname} terminated account", ))
        
        cursor.close()
       
        return flask.redirect(p_tar(flask.request.args.get('target')))

    elif flask.request.form["operation"] == "update_password":
        not_logged_abort()
        password = flask.request.form["password"]
        password1 = flask.request.form["new_password1"]
        password2 = flask.request.form["new_password2"]
        null_checker(password, password1, password2)

        connection = mdownotes.model.get_db()
        cursor = connection.cursor()

        # make sure form was right in its reqs
        if user_authentication(flask.session["username"], password, cursor):
            if password1 != password2:
                cursor.close()
                flask.abort(401)
        else:
            cursor.close()
            flask.abort(403)

        # update the password
        cursor.execute(
            'UPDATE users SET password = ?'
            ' WHERE username = ?',
            (get_db_ps_str(password1), flask.session["username"])
            )
        cursor.close()
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
    cursor.close()
  
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


# @mdownotes.app.route("/assets/index-B0wtBSaw.js/", methods = ["GET"])
# def serve_file():
    
#     return flask.send_from_directory(mdownotes.app.static_folder, "assets/index-B0wtBSaw.js")

@mdownotes.app.route("/assets/<string:thing_to_get>/", methods = ["GET"])
def serve_file1(thing_to_get):
    #print("hi")
    print(thing_to_get)
    return flask.send_from_directory(mdownotes.app.static_folder, "assets/" + thing_to_get)

# @mdownotes.app.route("/assets/react-CHdo91hT.svg/", methods = ["GET"])
# def serve_file2():
    
#     return flask.send_from_directory(mdownotes.app.static_folder, "assets/react-CHdo91hT.svg")

    