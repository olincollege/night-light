def calculate_percieved_brightness(conn):
    """
    Calculate percieved brightness by adding A + B hueristic together.
    """
    conn.execute("""
    ALTER TABLE crosswalk_centers_classified_lights 
    ADD COLUMN IF NOT EXISTS light_heuristic FLOAT;
    """)

    conn.execute("""
    UPDATE crosswalk_centers_classified_lights
    SET light_heuristic = (a_heuristic + b_heuristic);
    """)

    print("Light heuristic calculated")
