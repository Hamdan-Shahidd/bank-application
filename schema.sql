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

-- Used to create the short term memory. 
CREATE TABLE IF NOT EXISTS conversation_messages(
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    role        TEXT    NOT NULL CHECK (role IN ('human','ai')),
    content     TEXT    NOT NULL,
    tool_name   TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
) STRICT;

CREATE INDEX IF NOT EXISTS idx_conv_user_time ON conversation_messages(user_id, created_at);

-- For long term facts.
CREATE TABLE IF NOT EXISTS user_memory(
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    key         TEXT    NOT NULL,
    value       TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, key)
) STRICT;

CREATE INDEX IF NOT EXISTS idx_tx_sender    ON transactions(sender_id);
CREATE INDEX IF NOT EXISTS idx_tx_recipient ON transactions(recipient_id);

-- Each chat thread the user can open, rename, continue or delete.
CREATE TABLE IF NOT EXISTS conversations(
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    title       TEXT    NOT NULL DEFAULT 'New chat',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
) STRICT;

CREATE INDEX IF NOT EXISTS idx_conversations_user
    ON conversations(user_id, updated_at);
