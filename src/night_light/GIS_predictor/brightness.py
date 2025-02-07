import night_light.bronze_db.util as util


def brightness_table():
    """
    Find an estimate for the overall brightness of the area near each crosswalk
    by using a heuristic for illuminance.

    Add column to table 'crosswalk_centers_lights' called 
    'illuminance_heuristic' which sums the inverse square distance of each
    streetlight identified to be located near each crosswalk center.
    """
    # Go through each light that is close to the crosswalk
    con = util.connect_to_duckdb("src/night_light/GIS_predictor/edge_classifier/edge_classifier_lights.db")
    crosswalks = con.execute("SELECT geometry, streetlight_dist FROM crosswalk_centers_lights").fetchall()

    con.execute("ALTER TABLE crosswalk_centers_lights ADD COLUMN IF NOT EXISTS illuminance_heuristic FLOAT")

    for crosswalk in crosswalks:
        center = crosswalk[0]
        distances = crosswalk[1]
        illuminance_heuristic = sum([1 / (x**2) for x in distances])

        con.execute("""
                    UPDATE crosswalk_centers_lights
                    SET illuminance_heuristic = ?
                    WHERE geometry = ?
                    """, (illuminance_heuristic, center))
    con.commit()

if __name__ == "__main__":
    brightness_table()

