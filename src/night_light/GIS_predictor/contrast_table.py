import night_light.bronze_db.util as util
from shapely.wkt import loads

"""

"""
def contrast_table():
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    gdf = util.query_table_to_gdf(con, "crosswalk_centers_classified_lights", "SELECT * FROM crosswalk_classified_lights")
    return gdf

def get_coords(point):
    point = point[point.index('(') + 1:point.index(')')]
    x = float(point[:point.index(" ")])
    y = float(point[point.index(" ") + 1:])
    return x, y

def classify_lights_table():
    """
    Goes through each row and creates 2 lists (left and right)
    """
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    con.execute("""
                CREATE TABLE IF NOT EXISTS crosswalk_centers_classified_lights AS
                SELECT crosswalk_id, geometry FROM crosswalk_centers_lights
                """)
    
    con.execute("""
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS left_streetlight_id INTEGER[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS left_streetlight_dist FLOAT[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS left_streetlight_geom VARCHAR(1000);
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS right_streetlight_id INTEGER[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS right_streetlight_dist FLOAT[];
                ALTER TABLE crosswalk_centers_classified_lights ADD COLUMN IF NOT EXISTS right_streetlight_geom VARCHAR(1000);
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

        l_streetlight_id = []
        l_streetlight_dist = []
        l_streetlight_geom = []
        r_streetlight_id = []
        r_streetlight_dist = []
        r_streetlight_geom = []

        if light_geoms is not None:
            for i, _ in enumerate(light_geoms):
                light_x, light_y = light_coords[i]

                direction = (light_x - center_x1)*(center_y2 - center_y1) - (light_y - center_y1)*(center_x2-center_x1)
                if direction < 0:
                    l_streetlight_id.append(light_ids[i])
                    l_streetlight_dist.append(light_dists[i])
                    l_streetlight_geom.append(light_geoms[i])
                else:
                    r_streetlight_id.append(light_ids[i])
                    r_streetlight_dist.append(light_dists[i])
                    r_streetlight_geom.append(light_geoms[i])

        con.execute("""
                    UPDATE crosswalk_centers_classified_lights
                    SET 
                        left_streetlight_id = ?,
                        left_streetlight_dist = ?,
                        left_streetlight_geom = ?,
                        right_streetlight_id = ?,
                        right_streetlight_dist = ?,
                        right_streetlight_geom = ?
                    WHERE geometry = ?
                    """, (l_streetlight_id, l_streetlight_dist, l_streetlight_geom, r_streetlight_id, r_streetlight_dist, r_streetlight_geom, center))
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
    lights_geom()
    classify_lights_table()
    
