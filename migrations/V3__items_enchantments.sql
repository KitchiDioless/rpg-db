CREATE TABLE Item (
    item_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    value INTEGER NOT NULL
);

CREATE TABLE EntityInventory (
    entity_id INTEGER NOT NULL REFERENCES Entity(entity_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES Item(item_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (entity_id, item_id)
);

CREATE TABLE Enchantment (
    enchantment_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    charges INTEGER NOT NULL
);

CREATE TABLE EnchantmentEffect (
    id SERIAL PRIMARY KEY,
    enchantment_id INTEGER REFERENCES Enchantment(enchantment_id) ON DELETE CASCADE,
    effect_type TEXT CHECK (effect_type IN ('fire', 'ice', 'poison', 'healing')),
    duration INTEGER NOT NULL
);

CREATE TABLE EnchantableItem (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES Item(item_id) ON DELETE CASCADE,
    enchantment_id INTEGER REFERENCES Enchantment(enchantment_id) ON DELETE CASCADE
);

CREATE TABLE UnenchantableItem (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES Item(item_id) ON DELETE CASCADE,
    usage TEXT
);