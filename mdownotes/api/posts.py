import flask
import mdownotes
import mdownotes.model

# supply all comments 
@mdownotes.app.route("/api/posts/<int:postid_url_slug>/")
def get_post(postid_url_slug):
    # authentication
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    
    
    
    if postid_url_slug < 0:
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    
    cursor = mdownotes.model.get_db().cursor()
    context = cursor.execute(
            "SELECT * "
            "FROM posts "
            "WHERE postid = ?", (postid_url_slug,)
        ).fetchone()
    if context is None:
        context = {"message": "Not Found", "status_code": 404}
        cursor.close()
        return flask.jsonify(**context), 404
    context["ownerShowUrl"] = f"/users/{context["owner"]}/"

    cur = cursor.execute(
            "SELECT owner, text, created, commentid "
            "FROM comments " "WHERE postid = ?",
            (postid_url_slug,),
        ).fetchall()
    for comment in cur:
        comment["url"] = "/api/comments/" + str(comment["commentid"]) + "/"
        comment["logOwnsThis"] = logname == comment["owner"]
    
    # this does not work with us anymore
    #context["comments_url"] = "/api/comments/?postid=" + str(
    #        postid_url_slug
    #)
    if len(cur) != 0:
        context["comments"] = cur
    else:
        context["comments"] = []
    context["logOwnsThis"] = context["owner"] == logname
    cursor.close()
    return flask.jsonify(**context)
        

# our pagination scheme implemented.

@mdownotes.app.route("/api/posts/")
def get_next_posts():
    # authentication
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    
    
    size = flask.request.args.get("size", default=10, type=int)
    timeint = flask.request.args.get("timeint", default=0, type=int)
    minid = flask.request.args.get("minid", default=0, type=int)
    vidid = flask.request.args.get("vidid", default=-1, type=int)
    
    if null_checker(size, timeint, minid, vidid):
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    
    if size < 1 or timeint < 0 or minid < 0 or vidid < 0:
        # bad request
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    
    cursor = mdownotes.model.get_db().cursor()
    (prmstr, posts) = paginate(size, timeint, minid, vidid, cursor)
    for post in posts:
        post["url"] = "/api/posts/" + str(post["postid"]) + "/"
    
    pth = flask.request.full_path
    context = {"next": prmstr, "results": posts, "url": pth.rstrip("?")}
    cursor.close()
    return flask.jsonify(**context)
    
    
def paginate(size: int, timeint: int, minid: int, vidid:int, cursor):
    """Paginate posts from database."""
    cur = cursor.execute(
    "SELECT vid_timestamp, postid FROM posts "
    "WHERE vidid = ? AND vid_timestamp = ? AND postid > ? ORDER BY postid ASC LIMIT ?",
    (vidid, timeint, minid, size),
    ).fetchall()
    rest = size - len(cur)
    if rest != 0:
        cur = cur + cursor.execute(
            "SELECT vid_timestamp, postid FROM posts "
            "WHERE vidid = ? AND vid_timestamp > ? ORDER BY vid_timestamp ASC, postid ASC LIMIT ?",
            (vidid, timeint, rest),
            ).fetchall()
    assert(len(cur) <= size)
    if (len(cur) < size):
        paramstr = ""
    else:
        # is it worth it here to make a seprerate query to limit the unnessecary data from query above?
        # vid_timestamp not used unless ur last in the lsit
        paramstr = (
            "/api/posts/?size="
            + str(size)
            + "&timeint="
            + str(cur[-1]["vid_timestamp"])
            + "&minid="
            + str(cur[-1]["postid"])
            + "&vidid="
            + str(vidid)
        )
    return paramstr, cur

# inserts a batch of posts from the user
@mdownotes.app.route("/api/posts/", methods=["POST"])
def insert_batch():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    
    received_batch = flask.request.json.get('batch')
    id = flask.request.args.get("vidid")
    # not doing any null checks on the values of the dictionary, so could have a dictionary with nulls in it
    # for simplicity now I dont care.
    if null_checker(received_batch, id):
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    cursor = mdownotes.model.get_db().cursor()
    cursor.executemany(
        "INSERT into posts(text, owner, vid_timestamp, vidid) "
        "VALUES(?,?,?,?)", [(a["text"], logname, a["timestamp"], id) for a in received_batch]
    )
    # we dont return any data because the user should trigger a page reload when hitting this route.
    cursor.close() 
    return flask.Response(status=201)

# inserts a comment from the user
@mdownotes.app.route("/api/comments/", methods=["POST"])
def insert_comment():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    # some dict
    received_comment = flask.request.json.get('comment')
    postid = flask.request.json.get('postid')
    
    # not doing any null checks on the values of the dictionary, so could have a dictionary with nulls in it
    # for simplicity now I dont care.
    if null_checker(received_comment, postid):
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    cursor = mdownotes.model.get_db().cursor()
    
    cur = cursor.execute("SELECT owner FROM "
                             "posts Where postid = ?", (postid,))
    if len(cur.fetchall()) == 0:
        context = {"message": "Not Found", "status_code": 404}
        cursor.close()
        return flask.jsonify(**context), 404

    # race condition lol
    cursor.execute(
            "INSERT INTO "
            "comments(owner, postid, text) "
            "VALUES (?, ?, ?)",
            (logname, postid, received_comment),
        )
    cur = cursor.execute('''SELECT created, commentid
                            FROM comments
                        WHERE commentid = (SELECT MAX(commentid) FROM comments);''').fetchall()
    newid = cur[0]["commentid"]
    context = {
            "commentid": newid,
            "logOwnsThis": True,
            "owner": logname,
            "text": received_comment,
            "url": "/api/v1/comments/" + str(newid) + "/",
            "created": cur[0]["created"],
        }
    cursor.close()
    return flask.jsonify(**context)
    
    
# deletes a post
@mdownotes.app.route("/api/posts/", methods=["DELETE"])
def delete_post():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    postid = flask.request.args.get("postid")
    if null_checker(postid):
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    cursor = mdownotes.model.get_db().cursor()
    p = cursor.execute(
        "SELECT owner FROM posts "
        "WHERE postid = ?", (postid,)
    ).fetchall()
    if len(p) == 0:
        context = {"message": "Not Found", "status_code": 404}
        cursor.close()
        return flask.jsonify(**context), 404
    if p[0]["owner"] != logname:
        context = {"message": "Forbidden", "status_code": 403}
        cursor.close()
        return flask.jsonify(**context), 403
    
    cursor.execute(
        "DELETE FROM posts "
        "WHERE postid = ?", (postid,)
    )
    cursor.close()
    return flask.Response(status=204)

# deletes a comment
@mdownotes.app.route("/api/comments/", methods=["DELETE"])
def delete_comment():
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        context = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**context), 403
    commentid = flask.request.args.get("commentid")
    if null_checker(commentid):
        context = {"message": "Bad Request", "status_code": 400}
        return flask.jsonify(**context), 400
    cursor = mdownotes.model.get_db().cursor()
    p = cursor.execute(
        "SELECT owner FROM comments "
        "WHERE commentid = ?", (commentid,)
    ).fetchall()
    if len(p) == 0:
        context = {"message": "Not Found", "status_code": 404}
        cursor.close()
        return flask.jsonify(**context), 404
    if p[0]["owner"] != logname:
        context = {"message": "Forbidden", "status_code": 403}
        cursor.close()
        return flask.jsonify(**context), 403
    
    cursor.execute(
        "DELETE FROM comments "
        "WHERE commentid = ?", (commentid,)
    )
    cursor.close()
    return flask.Response(status=204)


def null_checker(*args):
    """ Checks if args are null"""
    for arg in args:
        if arg is None:
            return True
    return False