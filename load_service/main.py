import os
import time
import random
import json
import psycopg2
from prometheus_client import start_http_server, Counter, Histogram
import threading

QUERY_TIME = Histogram('query_execution_seconds', 'Time spent executing query', ['query_type'])
QUERY_COUNT = Counter('query_total', 'Total queries executed', ['query_type', 'status'])
QUERY_INDEX_USAGE = Counter('query_index_usage_total', 'Number of index-scan nodes detected in EXPLAIN', ['query_type'])

DB_PARAMS = {
    'dbname': 'migrator',
    'user': 'migrator',
    'password': 'sosiska',
    'host': 'haproxy',
    'port': '5432'
}

QUERIES_WITH_IDX = {
    'complex_join': """
    WITH target_race AS (
        SELECT race_id
        FROM Race
        WHERE name = %(race_name)s
    ),
    target_entities AS (
        SELECT e.entity_id, e.name, e.race_id
        FROM Entity e
        WHERE e.race_id = (SELECT race_id FROM target_race)
    )
    SELECT te.name,
        r.name AS race,
        l.name AS location,
        f.name AS faction,
        cf.reputation,
        cf.title,
        COUNT(DISTINCT s.skill_id) AS skills_count
    FROM target_entities te
    INNER JOIN Race r ON te.race_id = r.race_id
    INNER JOIN Character c ON te.entity_id = c.entity_id
    INNER JOIN Location l ON c.home_location_id = l.location_id
    LEFT JOIN CharacterFaction cf ON te.entity_id = cf.entity_id
    LEFT JOIN Faction f ON cf.faction_id = f.faction_id
    LEFT JOIN EntitySkill s ON te.entity_id = s.entity_id
    WHERE (cf.reputation IS NULL OR cf.reputation >= %(min_reputation)s)
    GROUP BY te.entity_id, te.name, r.name, l.name, f.name, cf.reputation, cf.title
    ORDER BY cf.reputation DESC NULLS LAST;
    """,
    'low_selectivity': """
    SELECT r.name AS race,
        COUNT(DISTINCT e.entity_id) AS entity_count,
        COUNT(DISTINCT s.skill_id) AS total_skills,
        COUNT(DISTINCT sp.spell_id) AS total_spells
    FROM Race r
    LEFT JOIN LATERAL (
        SELECT e.entity_id
        FROM Entity e
        WHERE e.race_id = r.race_id
        LIMIT 10000
    ) e ON true
    LEFT JOIN EntitySkill s ON e.entity_id = s.entity_id
    LEFT JOIN EntitySpell sp ON e.entity_id = sp.entity_id
    WHERE (r.name = %(race_name)s OR %(race_name)s IS NULL)
    GROUP BY r.race_id, r.name
    HAVING COUNT(DISTINCT e.entity_id) > 0;
    """,
    'high_selectivity': """
    WITH target_location AS (
        SELECT location_id
        FROM Location
        WHERE name = %(location_name)s
    ),
    entities_in_location AS (
        SELECT c.entity_id
        FROM Character c
        WHERE c.home_location_id = (SELECT location_id FROM target_location)
    )
    SELECT e.name,
        l.name AS location,
        COUNT(DISTINCT i.item_id) AS inventory_items,
        SUM(ei.quantity) AS total_items,
        STRING_AGG(DISTINCT s.name, ', ') AS skills
    FROM Entity e
    INNER JOIN entities_in_location el ON e.entity_id = el.entity_id
    INNER JOIN Character c ON e.entity_id = c.entity_id
    INNER JOIN Location l ON c.home_location_id = l.location_id
    LEFT JOIN EntityInventory ei ON e.entity_id = ei.entity_id
    LEFT JOIN Item i ON ei.item_id = i.item_id
    LEFT JOIN EntitySkill es ON e.entity_id = es.entity_id
    LEFT JOIN Skill s ON es.skill_id = s.skill_id
    GROUP BY e.entity_id, e.name, l.name
    HAVING COUNT(DISTINCT i.item_id) > %(min_items)s
    ORDER BY total_items DESC
    LIMIT 10;
    """,
    'multi_join': """
    WITH players AS (
        SELECT p.player_id, p.entity_id
        FROM Player p
        WHERE p.player_id = %(player_id)s
    ),
    player_journal AS (
        SELECT j.player_id, j.journal_id
        FROM PlayerJournal j
        WHERE j.player_id = %(player_id)s
    )
    SELECT p.player_id,
        e.name,
        COUNT(DISTINCT j.journal_id) AS journal_entries,
        COUNT(DISTINCT q.quest_id) AS active_quests,
        STRING_AGG(DISTINCT f.name, ', ') AS factions,
        STRING_AGG(DISTINCT i.name, ', ') AS inventory_items
    FROM players p
    INNER JOIN Entity e ON p.entity_id = e.entity_id
    LEFT JOIN player_journal j ON p.player_id = j.player_id
    LEFT JOIN CharacterQuest cq ON e.entity_id = cq.entity_id
    LEFT JOIN Quest q ON cq.quest_id = q.quest_id
    LEFT JOIN CharacterFaction cf ON e.entity_id = cf.entity_id
    LEFT JOIN Faction f ON cf.faction_id = f.faction_id
    LEFT JOIN EntityInventory ei ON e.entity_id = ei.entity_id
    LEFT JOIN Item i ON ei.item_id = i.item_id
    GROUP BY p.player_id, e.entity_id, e.name
    HAVING COUNT(DISTINCT j.journal_id) > 0;
    """
}

QUERIES_WITHOUT_IDX = {
    'complex_join': """
        SELECT e.name, r.name as race, l.name as location, 
               f.name as faction, cf.reputation, cf.title,
               COUNT(DISTINCT s.skill_id) as skills_count
        FROM Entity e
        INNER JOIN Race r ON e.race_id = r.race_id
        INNER JOIN Character c ON e.entity_id = c.entity_id
        INNER JOIN Location l ON c.home_location_id = l.location_id
        LEFT JOIN CharacterFaction cf ON e.entity_id = cf.entity_id
        LEFT JOIN Faction f ON cf.faction_id = f.faction_id
        LEFT JOIN EntitySkill s ON e.entity_id = s.entity_id
        GROUP BY e.entity_id, e.name, r.name, l.name, f.name, cf.reputation, cf.title
        ORDER BY cf.reputation DESC NULLS LAST
    """,
    'low_selectivity': """
        SELECT r.name as race, 
               COUNT(DISTINCT e.entity_id) as entity_count,
               COUNT(DISTINCT s.skill_id) as total_skills,
               COUNT(DISTINCT sp.spell_id) as total_spells
        FROM Race r
        LEFT JOIN Entity e ON r.race_id = e.race_id
        LEFT JOIN EntitySkill s ON e.entity_id = s.entity_id
        LEFT JOIN EntitySpell sp ON e.entity_id = sp.entity_id
        GROUP BY r.race_id, r.name
        HAVING COUNT(DISTINCT e.entity_id) > 0
    """,
    'high_selectivity': """
        SELECT e.name, l.name as location,
               COUNT(DISTINCT i.item_id) as inventory_items,
               SUM(ei.quantity) as total_items,
               STRING_AGG(DISTINCT s.name, ', ') as skills
        FROM Entity e
        INNER JOIN Character c ON e.entity_id = c.entity_id
        INNER JOIN Location l ON c.home_location_id = l.location_id
        LEFT JOIN EntityInventory ei ON e.entity_id = ei.entity_id
        LEFT JOIN Item i ON ei.item_id = i.item_id
        LEFT JOIN EntitySkill es ON e.entity_id = es.entity_id
        LEFT JOIN Skill s ON es.skill_id = s.skill_id
        GROUP BY e.entity_id, e.name, l.name
        HAVING COUNT(DISTINCT i.item_id) > 0
        ORDER BY total_items DESC
        LIMIT 10
    """,
    'multi_join': """
        SELECT p.player_id, e.name,
               COUNT(DISTINCT j.journal_id) as journal_entries,
               COUNT(DISTINCT q.quest_id) as active_quests,
               STRING_AGG(DISTINCT f.name, ', ') as factions,
               STRING_AGG(DISTINCT i.name, ', ') as inventory_items
        FROM Player p
        INNER JOIN Entity e ON p.entity_id = e.entity_id
        LEFT JOIN PlayerJournal j ON p.player_id = j.player_id
        LEFT JOIN CharacterQuest cq ON e.entity_id = cq.entity_id
        LEFT JOIN Quest q ON cq.quest_id = q.quest_id
        LEFT JOIN CharacterFaction cf ON e.entity_id = cf.entity_id
        LEFT JOIN Faction f ON cf.faction_id = f.faction_id
        LEFT JOIN EntityInventory ei ON e.entity_id = ei.entity_id
        LEFT JOIN Item i ON ei.item_id = i.item_id
        GROUP BY p.player_id, e.entity_id, e.name
        HAVING COUNT(DISTINCT j.journal_id) > 0
    """
}

SAMPLE_PARAMS = {
    'complex_join': {'race_name': 'Elf', 'min_reputation': 0},
    'low_selectivity': {'race_name': None},
    'high_selectivity': {'location_name': 'Novigrad', 'min_items': 0},
    'multi_join': {'player_id': 1}
}

QUERIES = QUERIES_WITH_IDX

def has_index_scans(plan_node):
    count = 0
    node_type = plan_node.get('Node Type', '')
    if 'Index Scan' in node_type or 'Bitmap Index Scan' in node_type:
        count += 1
    for key in ('Plans', 'Plan', 'Inner Plan', 'Outer Plan'):
        children = plan_node.get(key)
        if isinstance(children, list):
            for c in children:
                count += has_index_scans(c)
        elif isinstance(children, dict):
            count += has_index_scans(children)
    return count

def explain_index_count(cursor, sql, params):
    explain_sql = "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql
    cursor.execute(explain_sql, params)
    row = cursor.fetchone()
    if not row:
        return 0
    plan_json = row[0]
    if isinstance(plan_json, str):
        plan = json.loads(plan_json)[0]['Plan']
    else:
        plan = plan_json[0]['Plan']
    return has_index_scans(plan)

def execute_query(conn, query_type):
    query = QUERIES[query_type]
    params = SAMPLE_PARAMS.get(query_type, {})
    cursor = conn.cursor()
    start_time = time.time()
    try:
        try:
            idx_nodes = explain_index_count(cursor, query, params)
            QUERY_INDEX_USAGE.labels(query_type=query_type).inc(idx_nodes)
        except Exception as e:
            print("EXPLAIN failed:", e)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        duration = time.time() - start_time
        QUERY_TIME.labels(query_type=query_type).observe(duration)
        QUERY_COUNT.labels(query_type=query_type, status='success').inc()
    except Exception as e:
        QUERY_COUNT.labels(query_type=query_type, status='error').inc()
        print(f"Error executing {query_type}: {e}")
    finally:
        cursor.close()

def worker():
    while True:
        try:
            with psycopg2.connect(**DB_PARAMS) as conn:
                query_type = random.choice(list(QUERIES.keys()))
                execute_query(conn, query_type)
                time.sleep(random.uniform(0.1, 1.0))
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(5)

def main():
    start_http_server(8000)
    num_workers = 5
    for _ in range(num_workers):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()
