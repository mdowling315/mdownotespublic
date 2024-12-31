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
        "SELECT desc FROM categories"
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