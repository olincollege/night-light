import night_light.bronze_db.util as util
from shapely.wkt import loads

"""

"""
def contrast_table():
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    con.execute("""
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS a_heuristic FLOAT;
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS b_heuristic FLOAT;
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS contrast_heuristic VARCHAR(500);
                """)
    
    con.execute("""
                UPDATE crosswalk_centers_classified_lights as c
                SET a_heuristic = (
                    SELECT SUM(1.0 / (d.value * d.value))
                    FROM UNNEST(c.a_streetlight_dist) AS d(value)
                ),
                b_heuristic = (
                    SELECT SUM(1.0 / (d.value * d.value))
                    FROM UNNEST(c.b_streetlight_dist) AS d(value)
                )
                """)
    
    con2 = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier.db")

    direction_vectors = con2.execute("""SELECT crosswalk_id, geometry, from_coord FROM crosswalk_centers""").fetchall()

    for row in direction_vectors:
        crosswalk_id = row[0]
        from_coord = row[2]

        from_x, from_y = get_coords(from_coord)

        matching_crosswalks = con.execute("""
                                          SELECT * 
                                          FROM crosswalk_centers_lights
                                          WHERE crosswalk_id = ?
                                          """, (crosswalk_id,)).fetchall()
        
        if len(matching_crosswalks) > 1:
            center1 = matching_crosswalks[0][1]
            center2 = matching_crosswalks[1][1]

            center_x1, center_y1 = get_coords(center1)
            center_x2, center_y2 = get_coords(center2)

        direction = (from_x - center_x1)*(center_y2 - center_y1) - (from_y - center_y1)*(center_x2-center_x1)
        con.execute(f"""
                    UPDATE crosswalk_centers_classified_lights as c
                    SET contrast_heuristic = (
                        CASE
                            WHEN {direction} < 0 AND c.a_heuristic > c.b_heuristic THEN 'positive contrast'
                            WHEN {direction} < 0 AND c.b_heuristic > c.a_heuristic THEN 'negative contrast'
                            WHEN {direction} > 0 AND c.a_heuristic > c.b_heuristic THEN 'negative contrast'
                            WHEN {direction} > 0 AND c.b_heuristic > c.a_heuristic THEN 'positive contrast'
                        END
                    )
                    """)

    con.commit()

def get_coords(point):
    point = point[point.index('(') + 1:point.index(')')]
    x = float(point[:point.index(" ")])
    y = float(point[point.index(" ") + 1:])
    return x, y

def classify_lights_table():
    """
    Goes through each row and creates 2 lists (a and b)
    """
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    con.execute("""
                CREATE TABLE IF NOT EXISTS crosswalk_centers_classified_lights AS
                SELECT crosswalk_id, geometry FROM crosswalk_centers_lights
                """)
    
    con.execute("""
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS a_streetlight_id INTEGER[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS a_streetlight_dist FLOAT[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS a_streetlight_geom VARCHAR(1000);
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS b_streetlight_id INTEGER[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS b_streetlight_dist FLOAT[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS b_streetlight_geom VARCHAR(1000);
                """)
    
    crosswalks = con.execute("""SELECT crosswalk_id, geometry, streetlight_id, streetlight_dist, streetlight_geom FROM crosswalk_centers_lights""").fetchall()

    for crosswalk in crosswalks:
        crosswalk_id = crosswalk[0]
        center = crosswalk[1]
        light_ids = crosswalk[2]
        light_dists = crosswalk[3]
        light_geoms = crosswalk[4]

        matching_crosswalks = con.execute("""
                                          SELECT * 
                                          FROM crosswalk_centers_lights
                                          WHERE crosswalk_id = ?
                                          """, (crosswalk_id,)).fetchall()
        
        if light_geoms is not None:
            light_geoms = light_geoms.split(',')
            light_coords = [get_coords(coord) for coord in light_geoms]

        if len(matching_crosswalks) > 1:
            center1 = matching_crosswalks[0][1]
            center2 = matching_crosswalks[1][1]

            center_x1, center_y1 = get_coords(center1)
            center_x2, center_y2 = get_coords(center2)

        a_streetlight_id = []
        a_streetlight_dist = []
        a_streetlight_geom = []
        b_streetlight_id = []
        b_streetlight_dist = []
        b_streetlight_geom = []

        if light_geoms is not None:
            for i, _ in enumerate(light_geoms):
                light_x, light_y = light_coords[i]

                direction = (light_x - center_x1)*(center_y2 - center_y1) - (light_y - center_y1)*(center_x2-center_x1)
                if direction < 0:
                    a_streetlight_id.append(light_ids[i])
                    a_streetlight_dist.append(light_dists[i])
                    a_streetlight_geom.append(light_geoms[i])
                else:
                    b_streetlight_id.append(light_ids[i])
                    b_streetlight_dist.append(light_dists[i])
                    b_streetlight_geom.append(light_geoms[i])

        con.execute("""
                    UPDATE crosswalk_centers_classified_lights
                    SET 
                        a_streetlight_id = ?,
                        a_streetlight_dist = ?,
                        a_streetlight_geom = ?,
                        b_streetlight_id = ?,
                        b_streetlight_dist = ?,
                        b_streetlight_geom = ?
                    WHERE geometry = ?
                    """, (a_streetlight_id, a_streetlight_dist, a_streetlight_geom, b_streetlight_id, b_streetlight_dist, b_streetlight_geom, center))
    con.commit()


def lights_geom():
    """
    """
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")

    con.execute("ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom VARCHAR(1000)")

    con.execute("""
                UPDATE crosswalk_centers_lights as c
                SET streetlight_geom = (
                    SELECT STRING_AGG(s.geometry, ',') 
                    FROM streetlights as s
                    JOIN UNNEST(c.streetlight_id) AS split_ids(id)
                        ON s.OBJECTID = split_ids.id
                    )
                """)
    con.commit()

if __name__ == "__main__":
    # lights_geom()
    # classify_lights_table()
    # contrast_table()
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    con2 = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier.db")
    gdf = util.query_table_to_gdf(con, "crosswalk_centers_classified_lights", "SELECT * FROM crosswalk_centers_classified_lights")
    print(gdf[gdf['crosswalk_id'] == 49617])

    
