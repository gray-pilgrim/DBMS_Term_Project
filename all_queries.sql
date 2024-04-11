CREATE TABLE IF NOT EXISTS user_database_list
(
    username VARCHAR(20) NOT NULL,
    password  VARCHAR(255),
    email VARCHAR(50),
    database_name VARCHAR(100),
    PRIMARY KEY (username, database_name)
);

INSERT INTO table2 VALUES ('ss', './multimedia/abir_newdb/Screnshot_1.png');