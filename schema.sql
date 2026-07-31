CREATE TABLE IF NOT EXISTS users(
    id             INTEGER PRIMARY KEY,
    username       TEXT    NOT NULL CHECK (length(trim(username)) > 0),
    gmail          TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    account_number TEXT    NOT NULL UNIQUE,
    password       TEXT    NOT NULL CHECK (length(password) > 0),
    balance        INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
) STRICT;
