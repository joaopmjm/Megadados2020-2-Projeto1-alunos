DROP TABLE IF EXISTS users;
CREATE TABLE users (
    owner_uuid BINARY(16) PRIMARY KEY,
    name NVARCHAR(1024),
);

ALTER TABLE tasks ADD owner_uuid BINARY(16);
ALTER TABLE tasks ADD FOREIGN KEY (owner_uuid) REFERENCES users(owner_uuid);