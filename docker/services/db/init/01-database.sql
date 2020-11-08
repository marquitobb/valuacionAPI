CREATE DATABASE IF NOT EXISTS `mewtwo`;

CREATE USER 'ashketchum'@'localhost' IDENTIFIED BY 'secret';
GRANT ALL PRIVILEGES ON *.* TO 'ashketchum'@'%';