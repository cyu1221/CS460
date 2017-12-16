DROP DATABASE photoshare1;
CREATE DATABASE photoshare1;
USE photoshare1;

-- CREATE USER TABLE
CREATE TABLE USER (
    UID INT NOT NULL AUTO_INCREMENT,
    GENDER enum('M','F'),
    EMAIL VARCHAR(40) UNIQUE,
    PASSWORD VARCHAR(40) NOT NULL,
    DOB DATE,
    HOMETOWN VARCHAR(40),
    FNAME VARCHAR(40) NOT NULL,
    LNAME VARCHAR(40) NOT NULL,
    PRIMARY KEY (UID)
);

-- CREATE FRIENDSHIP TABLE
CREATE TABLE FRIENDSHIP(
	UID1 INT NOT NULL,
	UID2 INT NOT NULL,
	PRIMARY KEY(UID1, UID2),
	FOREIGN KEY (UID1) REFERENCES USER(UID) ON DELETE CASCADE,
	FOREIGN KEY (UID2) REFERENCES USER(UID) ON DELETE CASCADE
);


-- CREATE Album TABLE (include album entity and 'own' relationship)
CREATE TABLE ALBUM(
	AID INT NOT NULL AUTO_INCREMENT,
	NAME VARCHAR(40) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PRIMARY KEY (AID),
	FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE
);

-- CREATE Photo TABLE (include photo entity and 'contains' relationship)
CREATE TABLE PHOTO(
	PID INT NOT NULL AUTO_INCREMENT,
	CAPTION VARCHAR(200),
	DATA longBLOB NOT NULL,
	AID INT NOT NULL,
	UID INT NOT NULL,
	PRIMARY KEY (PID),
	FOREIGN KEY (AID) REFERENCES ALBUM(AID) ON DELETE CASCADE,
  FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE
);

-- CREATE Comment TABLE (include comment entity and 'comment' relationship)
CREATE TABLE COMMENT(
	CID INT NOT NULL AUTO_INCREMENT,
	CONTENT VARCHAR(200) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PID INT,
	PRIMARY KEY (CID),
	FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

-- CREATE THE LIKETABLE. WE CAN'T name it LIKE
CREATE TABLE LIKETABLE(
	UID INT NOT NULL,
	PID INT NOT NULL,
	DOC TIMESTAMP NOT NULL,
        PRIMARY KEY (UID, PID),
	FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);


-- CREATE Tag TABLE
CREATE TABLE TAG(
	HASHTAG VARCHAR(40) NOT NULL,
	PRIMARY KEY (HASHTAG)
);

-- CREATE Associate Table
CREATE TABLE ASSOCIATE(
	PID INT NOT NULL,
	HASHTAG VARCHAR(40) NOT NULL,
        PRIMARY KEY (PID, HASHTAG),
	FOREIGN KEY (HASHTAG) REFERENCES TAG(HASHTAG) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);