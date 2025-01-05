import flask

app = flask.Flask(__name__, static_folder='static', static_url_path='/static')


app.config.from_object('mdownotes.config')


import mdownotes.api  # noqa: E402  pylint: disable=wrong-import-position
import mdownotes.views  # noqa: E402  pylint: disable=wrong-import-position
import mdownotes.model  # noqa: E402  pylint: disable=wrong-import-position