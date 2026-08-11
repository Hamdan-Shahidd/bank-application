CREATE TABLE IF NOT EXISTS users(
    id             INTEGER PRIMARY KEY,
    username       TEXT    NOT NULL CHECK (length(trim(username)) > 0),
    gmail          TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    account_number TEXT    NOT NULL UNIQUE,
    password       TEXT    NOT NULL CHECK (length(password) > 0),
    balance        INTEGER NOT NULL DEFAULT 0 CHECK (balance >= -200000),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
) STRICT;

CREATE TABLE IF NOT EXISTS transactions(
    id             INTEGER PRIMARY KEY,
    sender_id      INTEGER REFERENCES users(id),
    recipient_id   INTEGER REFERENCES users(id),
    amount         INTEGER NOT NULL CHECK (amount > 0),
    kind           TEXT    NOT NULL CHECK (kind IN ('deposit','transfer','withdrawal')),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tx_sender    ON transactions(sender_id);
CREATE INDEX IF NOT EXISTS idx_tx_recipient ON transactions(recipient_id);