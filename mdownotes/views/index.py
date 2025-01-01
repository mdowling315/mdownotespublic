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
    connection = mdownotes.model.get_db()
    cursor = connection.cursor()
    y = cursor.execute(
        "SELECT * FROM categories"
        ).fetchall()
    #print("y")
    #print(y)
    context = {"logname": "chickens",
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