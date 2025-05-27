PRAGMA foreign_keys = ON;
-- cant have an entry without a foreign key?


--CREATE TABLE users(
--  username VARCHAR(20) NOT NULL,
--  fullname VARCHAR(40) NOT NULL,
--  PRIMARY KEY(username)
--);

-- schema.sql

CREATE TABLE users (
    username VARCHAR(20) PRIMARY KEY,
    -- filename VARCHAR(64) NOT NULL,
    password VARCHAR(256) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifs (
    notifid INTEGER PRIMARY KEY AUTOINCREMENT,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    desc VARCHAR(1024) NOT NULL
);

CREATE TABLE videos (
    vidid INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(1024) NOT NULL,
    title VARCHAR(1024) NOT NULL,
    categoryid INTEGER NOT NULL,
    last_activity DATETIME DEFAULT NULL,
    owner VARCHAR(20) NOT NULL,
    comments_public INTEGER DEFAULT 0,
    FOREIGN KEY (categoryid) REFERENCES categories(categoryid) ON DELETE CASCADE
);

CREATE TABLE categories (
    categoryid INTEGER PRIMARY KEY AUTOINCREMENT,
    last_feed_activity DATETIME DEFAULT NULL,
    last_insdel DATETIME DEFAULT NULL,
    desc VARCHAR(20) NOT NULL
);

CREATE TABLE posts (
    postid INTEGER PRIMARY KEY AUTOINCREMENT,
    text VARCHAR(1024) NOT NULL,
    owner VARCHAR(20) NOT NULL,
    vid_timestamp INTEGER NOT NULL,
    vidid INTEGER NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner) REFERENCES users(username) ON DELETE CASCADE
    FOREIGN KEY (vidid) REFERENCES videos(vidid) ON DELETE CASCADE
);

CREATE TABLE comments (
    commentid INTEGER PRIMARY KEY AUTOINCREMENT,
    owner VARCHAR(20) NOT NULL,
    postid INTEGER NOT NULL,
    text VARCHAR(1024) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (postid) REFERENCES posts(postid) ON DELETE CASCADE
);