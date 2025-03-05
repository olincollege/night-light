from pyproj import Transformer, CRS

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
    """
    """
    point = point[point.index("(") + 1 : point.index(")")]
    x = float(point[: point.index(" ")])
    y = float(point[point.index(" ") + 1 :])

    return x, y


def classify_lights_table(con):
    """
    Goes through each row and creates 2 lists (from_side and to_side)
    """
    con.execute(
        """
                CREATE TABLE IF NOT EXISTS crosswalk_centers_classified_lights AS
                SELECT crosswalk_id, geometry, center_id, geometry_xy from_coord, to_coord FROM crosswalk_centers_lights
                """
    )

    con.execute(
        """        
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_id INTEGER[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_dist FLOAT[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_geom VARCHAR(1000)[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS from_side_streetlight_geom_xy VARCHAR(1000)[];
        
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_id INTEGER[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_dist FLOAT[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_geom VARCHAR(1000)[];
        ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS to_side_streetlight_geom_xy VARCHAR(1000)[];
        """
    )

    crosswalks = con.execute(
        """SELECT crosswalk_id, 
                  from_coord_xy, 
                  geometry, 
                  streetlight_id, 
                  streetlight_dist, 
                  streetlight_geom,
                  streetlight_geom_xy FROM crosswalk_centers_lights"""
    ).fetchall()

    for crosswalk in crosswalks:
        crosswalk_id = crosswalk[0]
        from_coord_xy = crosswalk[1]
        center = crosswalk[2]
        light_ids = crosswalk[3]
        light_dists = crosswalk[4]
        light_geoms = crosswalk[5]
        light_geoms_xy = crosswalk[6]

        crosswalk_A = con.execute("""
                                  SELECT geometry_xy 
                                  FROM crosswalk_centers_lights
                                  WHERE crosswalk_id = ? AND center_id = ?
                                  """,
            (crosswalk_id, "A"),
        ).fetchall()

        crosswalk_B = con.execute("""
                                  SELECT geometry_xy, 
                                  FROM crosswalk_centers_lights
                                  WHERE crosswalk_id = ? AND center_id = ?
                                  """,
            (crosswalk_id, "B"),
        ).fetchall()


        if light_geoms_xy is None:
            continue

        light_geoms = light_geoms.split(",")
        light_geoms_xy = light_geoms_xy.split(",")
        light_coords_xy = [get_coords(coord) for coord in light_geoms_xy]
        from_x, from_y = get_coords(from_coord_xy)

        if crosswalk_A != [] and crosswalk_B != []:
            center_xyA = crosswalk_A[0][0]
            center_xyB = crosswalk_B[0][0]

            center_xA, center_yA = get_coords(center_xyA)
            center_xB, center_yB = get_coords(center_xyB)
    
        from_side_streetlight_id = []
        from_side_streetlight_dist = []
        from_side_streetlight_geom = []
        from_side_streetlight_geom_xy = []
        to_side_streetlight_id = []
        to_side_streetlight_dist = []
        to_side_streetlight_geom = []
        to_side_streetlight_geom_xy = []

        for i, _ in enumerate(light_geoms_xy):
            light_x, light_y = light_coords_xy[i]

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
                from_side_streetlight_geom_xy.append(light_geoms_xy[i])
            else:
                to_side_streetlight_id.append(light_ids[i])
                to_side_streetlight_dist.append(light_dists[i])
                to_side_streetlight_geom.append(light_geoms[i])
                to_side_streetlight_geom_xy.append(light_geoms_xy[i])

        con.execute(
            """
                    UPDATE crosswalk_centers_classified_lights
                    SET 
                        from_side_streetlight_id = ?,
                        from_side_streetlight_dist = ?,
                        from_side_streetlight_geom = ?,
                        from_side_streetlight_geom_xy = ?,
                        to_side_streetlight_id = ?,
                        to_side_streetlight_dist = ?,
                        to_side_streetlight_geom = ?,
                        to_side_streetlight_geom_xy = ?
                    WHERE geometry = ?
                    """,
            (
                from_side_streetlight_id,
                from_side_streetlight_dist,
                from_side_streetlight_geom,
                from_side_streetlight_geom_xy,
                to_side_streetlight_id,
                to_side_streetlight_dist,
                to_side_streetlight_geom,
                to_side_streetlight_geom_xy,
                center,
            ),
        )


def lights_geom(con):
    """ 
    """
    con.execute(
        """
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS geometry_xy VARCHAR(1000);

        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS from_coord_lat_long VARCHAR(1000);
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS from_coord_xy VARCHAR(1000);

        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom VARCHAR(1000);
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom_lat_long VARCHAR(1000);
        ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom_xy VARCHAR(1000);
        """
    )

    con.execute(
        """
        UPDATE crosswalk_centers_lights as c
        SET geometry_xy = (
            ST_AsText(
                ST_Transform(
                    ST_GeomFromText(geometry_lat_long), 
                    CAST('EPSG:4326' AS VARCHAR),
                    CAST('EPSG:3857' AS VARCHAR)
                )
            )
        )
        """
    )

    con.execute(
        """
        UPDATE crosswalk_centers_lights as c
        SET from_coord_lat_long = (
            ST_AsText(
                ST_Point(ST_Y(ST_GeomFromText(from_coord)), ST_X(ST_GeomFromText(from_coord)))
            )
        ),
        from_coord_xy = (
            ST_AsText(
                ST_Transform(
                    ST_GeomFromText(from_coord_lat_long), 
                    CAST('EPSG:4326' AS VARCHAR),
                    CAST('EPSG:3857' AS VARCHAR)
                )
            )
        )
        """
    )

    con.execute(
        """
                UPDATE crosswalk_centers_lights as c
                SET streetlight_geom = (
                    SELECT STRING_AGG(s.geometry, ',') 
                    FROM streetlights as s
                    JOIN UNNEST(c.streetlight_id) AS split_ids(id)
                        ON s.OBJECTID = split_ids.id
                    ),
                streetlight_geom_lat_long = (
                    SELECT STRING_AGG(s.geometry_lat_long, ',') 
                    FROM streetlights as s
                    JOIN UNNEST(c.streetlight_id) AS split_ids(id)
                        ON s.OBJECTID = split_ids.id
                    ),
                streetlight_geom_xy = (
                    SELECT STRING_AGG(
                        ST_AsText(
                            ST_Transform(
                                ST_GeomFromText(s.geometry_lat_long), 
                                CAST('EPSG:4326' AS VARCHAR),
                                CAST('EPSG:3857' AS VARCHAR)
                            )
                        ) , ','
                    )
                    FROM streetlights as s
                    JOIN UNNEST(c.streetlight_id) AS split_ids(id)
                        ON s.OBJECTID = split_ids.id
                    )
                """
    )
