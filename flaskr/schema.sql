DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS space;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS price;

CREATE TABLE price (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  price REAL NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL
);

CREATE TABLE space (
  id INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE reservation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  space_id INTEGER NOT NULL,
  reservation_datetime INTEGER NOT NULL,
  entry_datetime INTEGER,
  exit_datetime INTEGER,
  status TEXT NOT NULL,
  cost REAL,
  code TEXT UNIQUE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (space_id) REFERENCES space(id)
);

CREATE TABLE message (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message TEXT NOT NULL,
  readed INTEGER
);

/* ... (todo tu código anterior) ... */

CREATE TABLE assisted_reservation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  space_id INTEGER NOT NULL,
  entry_datetime INTEGER NOT NULL,
  exit_datetime INTEGER,
  status TEXT NOT NULL,
  cost REAL,
  code TEXT UNIQUE NOT NULL,
  FOREIGN KEY (space_id) REFERENCES space(id)
);

INSERT INTO price (price) VALUES (25);

INSERT INTO space (id) VALUES (1);
INSERT INTO space (id) VALUES (2);
INSERT INTO space (id) VALUES (3);
INSERT INTO space (id) VALUES (4);
INSERT INTO space (id) VALUES (5);
INSERT INTO space (id) VALUES (6);
INSERT INTO space (id) VALUES (7);
INSERT INTO space (id) VALUES (8);
INSERT INTO space (id) VALUES (9);
INSERT INTO space (id) VALUES (10);
INSERT INTO space (id) VALUES (11);
INSERT INTO space (id) VALUES (12);
INSERT INTO space (id) VALUES (13);
INSERT INTO space (id) VALUES (14);
INSERT INTO space (id) VALUES (15);

INSERT INTO user (name, last_name, email, password, role) VALUES ("", "", "timeparking.admin@gmail.com","scrypt:32768:8:1$ANuSlWwAqv4TR8je$57d9747d45aa7ecb5e312a9a448ffcff9048a3faef3c3e4ad49fcc621aa2939578cca07784d35982ce1b8e1a3592a41a0937485a1864f6b83c63b3df72300e54", "admin");

-- Agrega esto a la definición de tus tablas en schema.sql
ALTER TABLE reservation ADD COLUMN type TEXT DEFAULT 'hour'; -- 'hour' o 'pension'
ALTER TABLE assisted_reservation ADD COLUMN type TEXT DEFAULT 'hour';