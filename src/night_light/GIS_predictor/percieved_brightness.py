def calculate_percieved_brightness(conn):
    """
    Calculate percieved brightness by adding A + B hueristic together.
    """
    conn.execute(
        """
    ALTER TABLE crosswalk_centers_contrast 
    ADD COLUMN IF NOT EXISTS light_heuristic FLOAT;
    """
    )

    conn.execute(
        """
    UPDATE crosswalk_centers_contrast
    SET light_heuristic = from_heuristic + to_heuristic;
    """
    )

    print("Light heuristic calculated")
