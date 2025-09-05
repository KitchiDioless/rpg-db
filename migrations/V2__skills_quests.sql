CREATE TABLE Quest (
    quest_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    reward INTEGER
);

CREATE TABLE EntityQuest (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    quest_id INTEGER REFERENCES Quest(quest_id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('started', 'completed', 'failed'))
);

CREATE TABLE CharacterQuest (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    quest_id INTEGER REFERENCES Quest(quest_id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('started', 'completed', 'failed'))
);

CREATE TABLE Skill (
    skill_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE EntitySkill (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES Skill(skill_id) ON DELETE CASCADE,
    level INTEGER NOT NULL
);

CREATE TABLE Spell (
    spell_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mana_cost INTEGER NOT NULL,
    effect TEXT
);

CREATE TABLE EntitySpell (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    spell_id INTEGER REFERENCES Spell(spell_id) ON DELETE CASCADE
);

CREATE TABLE Dialogue (
    dialogue_id SERIAL PRIMARY KEY,
    entity_id INTEGER REFERENCES Entity(entity_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    response_type TEXT CHECK (response_type IN ('neutral', 'aggressive', 'friendly'))
);