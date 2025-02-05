import night_light.bronze_db.util as util

"""

"""
def contrast_table():
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    gdf = util.query_table_to_gdf(con, "crosswalk_centers_lights", "SELECT * FROM crosswalk_centers_lights")
    return gdf

def crosswalk_centers_contrast_gdf():
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")

    con.execute("ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS streetlight_geom VARCHAR(1000)")
    
    crosswalks = con.execute("SELECT geometry, streetlight_id FROM crosswalk_centers_lights").fetchall()

    for crosswalk in crosswalks:
        center = crosswalk[0]
        lights = crosswalk[1]

        con.execute("""
                    UPDATE crosswalk_centers_lights
                    SET streetlight_geom = (
                        SELECT GROUP_CONCAT(streetlights.geometry) 
                        FROM streetlights
                        WHERE streetlights.OBJECTID IN ?
                    ) 
                    WHERE geometry = ?""", (lights, center))
    con.commit()


if __name__ == "__main__":
    # crosswalk_centers_contrast_gdf()
    print(contrast_table())
