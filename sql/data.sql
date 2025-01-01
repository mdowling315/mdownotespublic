INSERT INTO users(username, password)
VALUES('chickens','sha512$34e94a05cdf247db92a84bc590950336$7eaca2b4169e042120f015666115856c717343f1c75d1c1bd1bf469bd1cd439eb152ccda6a0b8703706dfbcb861b3cef9208325c31f436e8edb9563f01176c48'); 

INSERT INTO categories(desc)
VALUES
    ('Dana Linn Bailey');
INSERT INTO categories(desc)
VALUES
    ('Geoforry Hinton');
INSERT INTO categories(desc)
VALUES
    ('Mark zuckerberg');
INSERT INTO categories(desc)
VALUES
    ('Music');



INSERT INTO videos(url,title, categoryid)
VALUES
    ('zwzMBSsqr_0', 'Time (from "Inception") \\ Hans Zimmer \\ Jacobs Piano', 4);
INSERT INTO videos(url,title, categoryid)
VALUES
    ('6qTghUgMOeY', 'Impossible', 4);
INSERT INTO videos(url,title, categoryid)
VALUES
    ('G-I9csAflBs', 'Welcome To The Black Parade', 4);

INSERT INTO videos(url,title, categoryid)
VALUES
    --('https://www.youtube.com/watch?v=UsCXT3-w9iQ', '#75 - Dana Linn Bailey | Cutler Cast', 1);
    ('UsCXT3-w9iQ', '#75 - Dana Linn Bailey | Cutler Cast', 1);

INSERT INTO posts(text, owner, vid_timestamp, vidid)
VALUES
    ('its difficult to deal with all of the feedback chaos.', 'chickens', 1380, 1);

INSERT INTO comments(owner, postid, text)
VALUES
    ('chickens', 1, 'This might mean she is having trouble with her alledged De bogging her mind') 