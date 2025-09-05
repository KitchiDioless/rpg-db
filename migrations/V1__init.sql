CREATE TABLE Race (
    race_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    bonuses TEXT
);

CREATE TABLE Location (
    location_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE Entity (
    entity_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    race_id INTEGER REFERENCES Race(race_id),
    gender TEXT CHECK (gender IN ('male', 'female')),
    level INTEGER NOT NULL
);

CREATE TABLE Character (
    character_id SERIAL PRIMARY KEY,
    entity_id INTEGER UNIQUE REFERENCES Entity(entity_id) ON DELETE CASCADE,
    home_location_id INTEGER REFERENCES Location(location_id)
);

CREATE TABLE Player (
    player_id SERIAL PRIMARY KEY,
    entity_id INTEGER UNIQUE REFERENCES Entity(entity_id) ON DELETE CASCADE,
    last_save_coords_x FLOAT,
    last_save_coords_y FLOAT,
    last_save_coords_z FLOAT
);

CREATE TABLE PlayerJournal (
    journal_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES Player(player_id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    text TEXT
);

CREATE TABLE Faction (
    faction_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE CharacterFaction (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    faction_id INTEGER REFERENCES Faction(faction_id) ON DELETE CASCADE,
    reputation INTEGER,
    title TEXT
);