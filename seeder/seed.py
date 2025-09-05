import os
import psycopg2
import random
from faker import Faker
from packaging import version

print("=== START SEEDING ===")

fake = Faker()

conn = psycopg2.connect(
    dbname="migrator",
    user="migrator",
    password="sosiska",
    host="haproxy"
)

cur = conn.cursor()
SEED_COUNT = int(os.environ.get("SEED_COUNT", 1000))

def get_flyway_version():
    cur.execute("""
        SELECT version 
        FROM flyway_schema_history 
        WHERE success = TRUE 
        ORDER BY installed_rank DESC 
        LIMIT 1
    """)
    v = cur.fetchone()
    return v[0] if v else "0"

current_version = get_flyway_version()

def is_table_empty(table_name):
    cur.execute(f"SELECT COUNT(*) = 0 FROM {table_name};")
    empty = cur.fetchone()[0]
    print(f"Table '{table_name}' empty: {empty}")
    return empty

def should_seed(table_name, min_version):
    print(f"Checking {table_name}: Flyway version = {current_version}, required = {min_version}")
    if version.parse(current_version) < version.parse(min_version):
        print(f"SKIP {table_name} — version too low")
        return False
    if not is_table_empty(table_name):
        print(f"SKIP {table_name} — table not empty")
        return False
    print(f"SEED {table_name}")
    return True

def seed_race():
    if not should_seed("Race", "1"):
        return

    for _ in range(SEED_COUNT // 3):
        cur.execute("INSERT INTO Race (name, bonuses) VALUES (%s, %s)", (fake.word(), fake.sentence()))

def seed_entity():
    if not should_seed("Entity", "1"):
        return
    
    for _ in range(SEED_COUNT):
        cur.execute("""
            INSERT INTO Entity (name, race_id, gender, level)
            VALUES (%s, (SELECT race_id FROM Race ORDER BY RANDOM() LIMIT 1), %s, %s)
        """, (fake.name(), random.choice(['male', 'female']), random.randint(1, 20)))

def seed_location():
    if not should_seed("Location", "1"):
        return
    
    for _ in range(int(SEED_COUNT * 1.5)):
        cur.execute("INSERT INTO Location (name, description) VALUES (%s, %s)", (fake.city(), fake.text(max_nb_chars=100)))

def seed_item():
    if not should_seed("Item", "3"):
        return
    
    for _ in range(SEED_COUNT * 10):
        cur.execute("""
            INSERT INTO Item (name, description, value)
            VALUES (%s, %s, %s)
        """, (fake.word().capitalize(), fake.sentence(), random.randint(10, 1000)))

def seed_quest():
    if not should_seed("Quest", "2"):
        return

    for _ in range(SEED_COUNT * 2):
        cur.execute("""
            INSERT INTO Quest (title, description, reward)
            VALUES (%s, %s, %s)
        """, (fake.bs().capitalize(), fake.paragraph(), random.randint(100, 1000)))

def seed_entity_quests():
    if not should_seed("EntityQuest", "2"):
        return
    
    for _ in range(SEED_COUNT):
        cur.execute("""
            INSERT INTO EntityQuest (entity_id, quest_id, status)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                (SELECT quest_id FROM Quest ORDER BY RANDOM() LIMIT 1),
                %s
            )
        """, (random.choice(['started', 'completed', 'failed']),))

def seed_character():
    if not should_seed("Character", "1"):
        return
    
    cur.execute("SELECT entity_id FROM Entity")
    entity_ids = [row[0] for row in cur.fetchall()]

    random.shuffle(entity_ids)
    selected_entities = entity_ids[:SEED_COUNT]
    
    for entity_id in selected_entities:
        cur.execute("""
            INSERT INTO Character (entity_id, home_location_id)
            VALUES (
                %s,
                (SELECT location_id FROM Location ORDER BY RANDOM() LIMIT 1)
            )
        """, (entity_id,))

def seed_player():
    if not should_seed("Player", "1"):
        return
    
    for _ in range(SEED_COUNT // SEED_COUNT):
        cur.execute("""
            INSERT INTO Player (entity_id, last_save_coords_x, last_save_coords_y, last_save_coords_z)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                %s, %s, %s
            )
        """, (
            round(random.uniform(-1000, 1000), 2),
            round(random.uniform(-1000, 1000), 2),
            round(random.uniform(-1000, 1000), 2)
        ))

def seed_player_journal():
    if not should_seed("PlayerJournal", "1"):
        return
    
    for _ in range(int(SEED_COUNT * 1.5)):
        cur.execute("""
            INSERT INTO PlayerJournal (player_id, date, text)
            VALUES (
                (SELECT player_id FROM Player ORDER BY RANDOM() LIMIT 1),
                %s, %s
            )
        """, (fake.date_time_this_year(), fake.text(max_nb_chars=200)))

def seed_faction():
    if not should_seed("Faction", "1"):
        return
    
    for _ in range(int(SEED_COUNT * 1.5)):
        cur.execute("""
            INSERT INTO Faction (name)
            VALUES (%s)
        """, (fake.company(),))

def seed_character_faction():
    if not should_seed("CharacterFaction", "1"):
        return
    
    for _ in range(SEED_COUNT):
        cur.execute("""
            INSERT INTO CharacterFaction (entity_id, faction_id, reputation, title)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                (SELECT faction_id FROM Faction ORDER BY RANDOM() LIMIT 1),
                %s, %s
            )
        """, (random.randint(-100, 100), fake.job().title()))

def seed_character_quests():
    if not should_seed("CharacterQuest", "2"):
        return
    
    for _ in range(SEED_COUNT * 2):
        cur.execute("""
            INSERT INTO CharacterQuest (entity_id, quest_id, status)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                (SELECT quest_id FROM Quest ORDER BY RANDOM() LIMIT 1),
                %s
            )
        """, (random.choice(['started', 'completed', 'failed']),))

def seed_skill():
    if not should_seed("Skill", "2"):
        return
    
    for _ in range(SEED_COUNT * 3):
        cur.execute("""
            INSERT INTO Skill (name, description)
            VALUES (%s, %s)
        """, (fake.word().capitalize(), fake.text(max_nb_chars=100)))

def seed_entity_skills():
    if not should_seed("EntitySkill", "2"):
        return
    
    for _ in range(SEED_COUNT + 1):
        cur.execute("""
            INSERT INTO EntitySkill (entity_id, skill_id, level)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                (SELECT skill_id FROM Skill ORDER BY RANDOM() LIMIT 1),
                %s
            )
        """, (random.randint(1, 10),))

def seed_spell():
    if not should_seed("Spell", "2"):
        return
    
    for _ in range(SEED_COUNT * 5):
        cur.execute("""
            INSERT INTO Spell (name, mana_cost, effect)
            VALUES (%s, %s, %s)
        """, (fake.word().capitalize(), random.randint(5, 50), fake.text(max_nb_chars=80)))

def seed_entity_spells():
    if not should_seed("EntitySpell", "2"):
        return
    
    for _ in range(SEED_COUNT + 1):
        cur.execute("""
            INSERT INTO EntitySpell (entity_id, spell_id)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                (SELECT spell_id FROM Spell ORDER BY RANDOM() LIMIT 1)
            )
        """)

def seed_dialogue():
    if not should_seed("Dialogue", "2"):
        return
    
    for _ in range(SEED_COUNT):
        cur.execute("""
            INSERT INTO Dialogue (entity_id, text, response_type)
            VALUES (
                (SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1),
                %s, %s
            )
        """, (fake.text(max_nb_chars=100), random.choice(['neutral', 'aggressive', 'friendly'])))

def seed_entity_inventory():
    if not should_seed("EntityInventory", "3"):
        return
    
    used_pairs = set()
    for _ in range(SEED_COUNT):
        while True:
            entity_id_query = "SELECT entity_id FROM Entity ORDER BY RANDOM() LIMIT 1"
            item_id_query = "SELECT item_id FROM Item ORDER BY RANDOM() LIMIT 1"
            cur.execute(entity_id_query)
            entity_id = cur.fetchone()[0]
            cur.execute(item_id_query)
            item_id = cur.fetchone()[0]
            pair = (entity_id, item_id)
            if pair not in used_pairs:
                used_pairs.add(pair)
                break
        cur.execute("""
            INSERT INTO EntityInventory (entity_id, item_id, quantity)
            VALUES (%s, %s, %s)
        """, (entity_id, item_id, random.randint(1, 5)))

def seed_enchantments():
    if not should_seed("Enchantment", "3"):
        return
    
    for _ in range(SEED_COUNT * 2):
        cur.execute("""
            INSERT INTO Enchantment (name, description, charges)
            VALUES (%s, %s, %s)
        """, (fake.word().capitalize(), fake.sentence(), random.randint(1, 10)))

def seed_enchantment_effects():
    if not should_seed("EnchantmentEffect", "3"):
        return
    
    for _ in range(SEED_COUNT * 2):
        cur.execute("""
            INSERT INTO EnchantmentEffect (enchantment_id, effect_type, duration)
            VALUES (
                (SELECT enchantment_id FROM Enchantment ORDER BY RANDOM() LIMIT 1),
                %s, %s
            )
        """, (random.choice(['fire', 'ice', 'poison', 'healing']), random.randint(1, 5)))

def seed_enchantable_items():
    if not should_seed("EnchantableItem", "3"):
        return
    
    for _ in range(SEED_COUNT * 5):
        cur.execute("""
            INSERT INTO EnchantableItem (item_id, enchantment_id)
            VALUES (
                (SELECT item_id FROM Item ORDER BY RANDOM() LIMIT 1),
                (SELECT enchantment_id FROM Enchantment ORDER BY RANDOM() LIMIT 1)
            )
        """)

def seed_unenchantable_items():
    if not should_seed("UnenchantableItem", "3"):
        return
    
    for _ in range(SEED_COUNT * 5):
        cur.execute("""
            INSERT INTO UnenchantableItem (item_id, usage)
            VALUES (
                (SELECT item_id FROM Item ORDER BY RANDOM() LIMIT 1),
                %s
            )
        """, (fake.text(max_nb_chars=60),))


if os.environ.get("APP_ENV") == "dev":
    seed_race()
    seed_location()
    seed_entity()
    seed_character()
    seed_player()
    seed_player_journal()
    seed_faction()
    seed_character_faction()
    seed_quest()
    seed_character_quests()
    seed_skill()
    seed_entity_skills()
    seed_spell()
    seed_entity_spells()
    seed_dialogue()
    seed_item()
    seed_entity_inventory()
    seed_enchantments()
    seed_enchantment_effects()
    seed_enchantable_items()
    seed_unenchantable_items()


conn.commit()
cur.close()
conn.close()

print("=== END SEEDING ===")