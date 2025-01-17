SET session_replication_role = 'replica';

CREATE TABLE players (
    id CHAR(16) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    rounds_won INT DEFAULT 0,
    rounds_lost INT DEFAULT 0,
    games_won INT DEFAULT 0,
    games_lost INT DEFAULT 0
);
CREATE TABLE passwords (
    player_id CHAR(16) PRIMARY KEY REFERENCES players(id),
    password_hash VARCHAR(255) NOT NULL
);
CREATE TABLE games (
    id CHAR(16) PRIMARY KEY,
    player1_id CHAR(16) REFERENCES players(id),
    player2_id CHAR(16) REFERENCES players(id),
    winner_id CHAR(16) REFERENCES players(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE game_rounds (
    id SERIAL PRIMARY KEY,
    game_id CHAR(16) REFERENCES games(id),
    player1_id CHAR(16) REFERENCES players(id),
    rounds_won1 INT DEFAULT 0,
    rounds_lost1 INT DEFAULT 0
);
CREATE TABLE logged_in_users (
    id SERIAL PRIMARY KEY,
    user_id CHAR(16) REFERENCES players(id),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SET session_replication_role = 'origin';