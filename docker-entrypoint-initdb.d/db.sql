CREATE DATABASE workshop;
CREATE USER 'ffuser'@'%' IDENTIFIED BY 'ffuser';
GRANT ALL PRIVILEGES ON *.* TO 'ffuser'@'%';
