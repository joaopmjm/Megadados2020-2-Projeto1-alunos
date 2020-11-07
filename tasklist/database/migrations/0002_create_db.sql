DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    owner_uuid BINARY(16) PRIMARY KEY,
    name NVARCHAR(1024)
);

CREATE TABLE tasks (
    uuid BINARY(16) PRIMARY KEY,
    descricao NVARCHAR(1024),
    owner_uuid BINARY(16),
    completed BOOLEAN,
    FOREIGN KEY (owner_uuid) REFERENCES users(owner_uuid) ON DELETE SET NULL
);