/* for staff log in */
DROP TABLE IF EXISTS staffinfo;
drop table if exists users;
    create table users (
    id integer primary key autoincrement,
    username text not null,
    password text not null
);

/* for adding a staff member */
CREATE TABLE IF NOT EXISTS `staffinfo` (
  `ID`		INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `firstName`	TEXT NOT NULL,
  `surname`	TEXT NOT NULL,
  'dateofbirth' numeric,
  `homeLocation`  TEXT NOT NULL,
  'username' TEXT NOT NULL,
  'password' TEXT NOT NULL
);
