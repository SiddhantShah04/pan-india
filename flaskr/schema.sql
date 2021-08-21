DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS activityLog;
CREATE TABLE users (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(30) NOT NULL,
    password VARCHAR(20) NOT NULL,
    phone INTEGER(10),
    CompanyName VARCHAR(255),
    userName VARCHAR(20),
    firstName VARCHAR(20),
    lastName VARCHAR(20),
    registeredTime TIMESTAMP,
    isDeleted BOOLEAN,
    isSuspended BOOLEAN,
    groups VARCHAR(10)
  )

CREATE TABLE activityLog (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
     userId INTEGER(6),
    tableName VARCHAR(10) ,
    description VARCHAR(255) NOT NULL,
    event VARCHAR(10));

