def contrast_table(con):
    con.execute(
        """
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_heuristic FLOAT;
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_heuristic FLOAT;
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS contrast_heuristic VARCHAR(500);
        """
    )

    con.execute(
        """
        UPDATE crosswalk_centers_classified_lights as c
        SET from_side_heuristic = (
            SELECT SUM(1.0 / (d.value * d.value))
            FROM UNNEST(c.from_side_streetlight_dist) AS d(value)
        ),
        to_side_heuristic = (
            SELECT SUM(1.0 / (d.value * d.value))
            FROM UNNEST(c.to_side_streetlight_dist) AS d(value)
        )
        """
    )

    con.execute(
        """
        UPDATE crosswalk_centers_classified_lights as c
        SET contrast_heuristic = (
            CASE
                WHEN c.from_side_heuristic > c.to_side_heuristic THEN 'positive contrast'
                WHEN c.from_side_heuristic < c.to_side_heuristic THEN 'negative contrast'
            END
        )
        """
    )


def get_coords(point):
    point = point[point.index("(") + 1 : point.index(")")]
    x = Decimal(point[: point.index(" ")])
    y = Decimal(point[point.index(" ") + 1 :])
    return x, y


def classify_lights_table(con):
    """
    Goes through each row and creates 2 lists (from_side and to_side)
    """
    con.execute(
        """
                CREATE TABLE IF NOT EXISTS crosswalk_centers_classified_lights AS
                SELECT crosswalk_id, geometry, center_id FROM crosswalk_centers_lights
                """
    )

    # Create the columns as arrays from the beginning
    con.execute(
        """
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_id INTEGER[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_dist FLOAT[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_geom VARCHAR(1000)[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_id INTEGER[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_dist FLOAT[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_geom VARCHAR(1000)[];
        """
    )

    crosswalks = con.execute(
        """SELECT crosswalk_id, center_id, from_coord, geometry, streetlight_id, streetlight_dist, streetlight_geom FROM crosswalk_centers_lights"""
    ).fetchall()

    for crosswalk in crosswalks:
        crosswalk_id = crosswalk[0]
        center_id = crosswalk[1]
        from_coord = crosswalk[2]
        center = crosswalk[3]
        light_ids = crosswalk[4]
        light_dists = crosswalk[5]
        light_geoms = crosswalk[6]

        crosswalk_A = con.execute("""
                                  SELECT geometry 
                                  FROM crosswalk_centers_lights
                                  WHERE crosswalk_id = ? AND center_id = ?
                                  """,
            (crosswalk_id, "A"),
        ).fetchall()

        crosswalk_B = con.execute("""
                                  SELECT geometry
                                  FROM crosswalk_centers_lights
                                  WHERE crosswalk_id = ? AND center_id = ?
                                  """,
            (crosswalk_id, "B"),
        ).fetchall()

        if light_geoms is None:
            continue

        light_geoms = light_geoms.split(",")
        light_coords = [get_coords(coord) for coord in light_geoms]
        from_x, from_y = get_coords(from_coord)

        if crosswalk_A != [] and crosswalk_B != []:
            centerA = crosswalk_A[0][0]
            centerB = crosswalk_B[0][0]

            center_xA, center_yA = get_coords(centerA)
            center_xB, center_yB = get_coords(centerB)
    
        from_side_streetlight_id = []
        from_side_streetlight_dist = []
        from_side_streetlight_geom = []
        to_side_streetlight_id = []
        to_side_streetlight_dist = []
        to_side_streetlight_geom = []

        for i, _ in enumerate(light_geoms):
            light_x, light_y = light_coords[i]

            direction_light = ((light_x - center_xA) * (center_yB - center_yA)) - (
                (light_y - center_yA) * (center_xB - center_xA)
            )

            direction_from = ((from_x - center_xA) * (center_yB - center_yA)) - (
                (from_y - center_yA) * (center_xB - center_xA)
            )

            if (direction_light > 0) == (direction_from > 0):
                from_side_streetlight_id.append(light_ids[i])
                from_side_streetlight_dist.append(light_dists[i])
                from_side_streetlight_geom.append(light_geoms[i])
            else:
                to_side_streetlight_id.append(light_ids[i])
                to_side_streetlight_dist.append(light_dists[i])
                to_side_streetlight_geom.append(light_geoms[i])

        con.execute(
            """
                    UPDATE crosswalk_centers_classified_lights
                    SET 
                        from_side_streetlight_id = ?,
                        from_side_streetlight_dist = ?,
                        from_side_streetlight_geom = ?,
                        to_side_streetlight_id = ?,
                        to_side_streetlight_dist = ?,
                        to_side_streetlight_geom = ?
                    WHERE geometry = ?
                    """,
            (
                from_side_streetlight_id,
                from_side_streetlight_dist,
                from_side_streetlight_geom,
                to_side_streetlight_id,
                to_side_streetlight_dist,
                to_side_streetlight_geom,
                center,
            ),
        )


def lights_geom(con):
    """ """
    con.execute(
        "ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom VARCHAR(1000)"
    )

    con.execute(
        """
                UPDATE crosswalk_centers_lights as c
                SET streetlight_geom = (
                    SELECT STRING_AGG(s.geometry, ',') 
                    FROM streetlights as s
                    JOIN UNNEST(c.streetlight_id) AS split_ids(id)
                        ON s.OBJECTID = split_ids.id
                    )
                """
    )
