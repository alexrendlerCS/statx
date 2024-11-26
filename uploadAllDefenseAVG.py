import psycopg2
from psycopg2.extras import execute_values

# Supabase connection details
SUPABASE_HOST = "aws-0-us-west-1.pooler.supabase.com"
SUPABASE_PORT = 6543
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres.xrstrludepuahpovxpzb"
SUPABASE_PASSWORD = "AZ1d3Tab7my1TubG"

# Connect to Supabase database
def connect_db():
    try:
        return psycopg2.connect(
            host=SUPABASE_HOST,
            port=SUPABASE_PORT,
            dbname=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            sslmode="require"
        )
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# Fetch and calculate all-team averages from defense_averages and defense_averages_qb
def calculate_all_defense_averages():
    conn = connect_db()
    cursor = conn.cursor()

    # General Defense Averages
    cursor.execute("""
        SELECT 
            position_id,
            AVG(avg_rushing_attempts) AS avg_rushing_attempts,
            AVG(avg_rushing_yards) AS avg_rushing_yards,
            AVG(avg_yards_per_carry) AS avg_yards_per_carry,
            AVG(avg_rushing_tds) AS avg_rushing_tds,
            AVG(avg_targets) AS avg_targets,
            AVG(avg_receptions) AS avg_receptions,
            AVG(avg_receiving_yards) AS avg_receiving_yards,
            AVG(avg_yards_per_catch) AS avg_yards_per_catch,
            AVG(avg_receiving_tds) AS avg_receiving_tds
        FROM defense_averages
        GROUP BY position_id;
    """)
    general_averages = cursor.fetchall()

    # QB Defense Averages
    cursor.execute("""
        SELECT 
            AVG(avg_passing_attempts) AS avg_passing_attempts,
            AVG(avg_completions) AS avg_completions,
            AVG(avg_passing_yards) AS avg_passing_yards,
            AVG(avg_passing_tds) AS avg_passing_tds,
            AVG(avg_interceptions) AS avg_interceptions,
            AVG(avg_rate) AS avg_rate,
            AVG(avg_qb_rushing_attempts) AS avg_qb_rushing_attempts,
            AVG(avg_qb_rushing_yards) AS avg_qb_rushing_yards,
            AVG(avg_qb_avg_rushing_yards) AS avg_qb_avg_rushing_yards,
            AVG(avg_qb_rushing_tds) AS avg_qb_rushing_tds
        FROM defense_averages_qb;
    """)
    qb_averages = cursor.fetchone()

    cursor.close()
    conn.close()

    return general_averages, qb_averages

# Insert all-team averages into a new table
def insert_all_defense_averages(general_averages, qb_averages):
    conn = connect_db()
    cursor = conn.cursor()

    # Insert General Averages
    general_query = """
    INSERT INTO all_defense_averages (
        position_id, avg_rushing_attempts, avg_rushing_yards, avg_yards_per_carry,
        avg_rushing_tds, avg_targets, avg_receptions, avg_receiving_yards, avg_yards_per_catch, avg_receiving_tds
    ) VALUES %s
    ON CONFLICT (position_id) DO UPDATE SET
        avg_rushing_attempts = EXCLUDED.avg_rushing_attempts,
        avg_rushing_yards = EXCLUDED.avg_rushing_yards,
        avg_yards_per_carry = EXCLUDED.avg_yards_per_carry,
        avg_rushing_tds = EXCLUDED.avg_rushing_tds,
        avg_targets = EXCLUDED.avg_targets,
        avg_receptions = EXCLUDED.avg_receptions,
        avg_receiving_yards = EXCLUDED.avg_receiving_yards,
        avg_yards_per_catch = EXCLUDED.avg_yards_per_catch,
        avg_receiving_tds = EXCLUDED.avg_receiving_tds;
    """
    execute_values(cursor, general_query, general_averages)

    # Insert QB Averages
    qb_query = """
    INSERT INTO all_defense_averages_qb (
        avg_passing_attempts, avg_completions, avg_passing_yards, avg_passing_tds,
        avg_interceptions, avg_rate, avg_qb_rushing_attempts, avg_qb_rushing_yards,
        avg_qb_avg_rushing_yards, avg_qb_rushing_tds
    ) VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        avg_passing_attempts = EXCLUDED.avg_passing_attempts,
        avg_completions = EXCLUDED.avg_completions,
        avg_passing_yards = EXCLUDED.avg_passing_yards,
        avg_passing_tds = EXCLUDED.avg_passing_tds,
        avg_interceptions = EXCLUDED.avg_interceptions,
        avg_rate = EXCLUDED.avg_rate,
        avg_qb_rushing_attempts = EXCLUDED.avg_qb_rushing_attempts,
        avg_qb_rushing_yards = EXCLUDED.avg_qb_rushing_yards,
        avg_qb_avg_rushing_yards = EXCLUDED.avg_qb_avg_rushing_yards,
        avg_qb_rushing_tds = EXCLUDED.avg_qb_rushing_tds;
    """
    execute_values(cursor, qb_query, [qb_averages])

    conn.commit()
    cursor.close()
    conn.close()

# Main function
if __name__ == "__main__":
    general_averages, qb_averages = calculate_all_defense_averages()
    insert_all_defense_averages(general_averages, qb_averages)
    print("All-defense averages successfully calculated and uploaded.")