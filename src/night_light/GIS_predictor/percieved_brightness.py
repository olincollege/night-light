def calculate_percieved_brightness(conn):
    """
    Calculate percieved brightness by adding A + B hueristic together.
    Multiply by 50 to give values on the 1 to 5 scale.
    """
    conn.execute("""
    ALTER TABLE crosswalk_centers_classified_lights 
    ADD COLUMN IF NOT EXISTS light_heuristic FLOAT;
    """)

    conn.execute("""
    UPDATE crosswalk_centers_classified_lights
    SET light_heuristic = (a_heuristic + b_heuristic) * 50;
    """)

    print("Light heuristic calculated")