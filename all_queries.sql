CREATE TABLE IF NOT EXISTS user_database_list
(
    username VARCHAR(20) NOT NULL,
    password  VARCHAR(255),
    email VARCHAR(50),
    database_name VARCHAR(100),
    PRIMARY KEY (username, database_name)
);

INSERT INTO table2 VALUES ('ss', '../static/multimedia/abir_newdb/Screnshot_1.png');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/Screenshot_2.png');

INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i1.jpg');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i2.jpg');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i3.jpg');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i4.jpg');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i5.jpg');
INSERT INTO table1img VALUES ('ss2', '../static/multimedia/abir_newdb/i6.jpg');

DELETE FROM table1img WHERE a1 = 'ss';
DELETE FROM table1img WHERE a1 = 'mj';
DELETE FROM table1img WHERE a2ig__mul = '../static/multimedia/abir_newdb/Screenshot_2.png';