CREATE INDEX idx_entity_race ON Entity (race_id);
CREATE INDEX idx_character_entity ON Character (entity_id);
CREATE INDEX idx_character_location ON Character (home_location_id);
CREATE INDEX idx_player_entity ON Player (entity_id);

CREATE INDEX idx_entity_name ON Entity (name);
CREATE INDEX idx_race_name ON Race (name);
CREATE INDEX idx_location_name ON Location (name);
CREATE INDEX idx_faction_name ON Faction (name);

CREATE INDEX idx_character_faction_entity ON CharacterFaction (entity_id);
CREATE INDEX idx_character_faction_faction ON CharacterFaction (faction_id);
CREATE INDEX idx_character_faction_reputation ON CharacterFaction (reputation);

CREATE INDEX idx_player_journal_player ON PlayerJournal (player_id);
CREATE INDEX idx_player_journal_date ON PlayerJournal (date); 