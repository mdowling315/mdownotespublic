import pathlib
# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = \
    b'!y(\x97\xa8\xbdR\xb9\xc3!\xb6\x92t\xe9\xe4s?\xd0P\x0bV\x0e\x19\x15'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
MDOWNOTES_ROOT = pathlib.Path(__file__).resolve().parent.parent
# UPLOAD_FOLDER = MDOWNOTES_ROOT/'var'/'uploads'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/insta485.sqlite3
DATABASE_FILENAME = MDOWNOTES_ROOT/'var'/'mdownotes.sqlite3'
