import duckdb

## Determines the direction of vehicle flow relative to pedestrian crosswalks and stores
## this direction using from_coord and to_coord in the crosswalk_centers table.


def identify_vehicle_direction(con: duckdb.DuckDBPyConnection):
    """
    Identify the direction of the vehicle for each side of the road segment.

    One-way streets:

    1. Find the intersecting street segment to the crosswalk.
    2. Compute relative distance between the first point of the street segment and the
       two points of the pedestrian edge. The closer of the two points to the street
       segment's first point is the "from_coord" and the other is the "to_coord." This
       is predefined by the street segments dataset since all the one ways were marked
       as ``FT``.

    Two-way streets:

    * **Case 1**:
      If the crosswalk center's X value is greater than the street center point's X
      value, we assume the vehicle is moving from "y_smaller" to "y_larger."

      * For the from_coord, choose the vertex of the pedestrian edge with the smaller Y.
      * For the to_coord, choose the vertex with the larger Y.

    * **Case 2**:
      If the crosswalk center's X is less than the street center point's X value, we
      assume the reverse.

      * For from_coord, choose the vertex with the larger Y.
      * For to_coord, choose the vertex with the smaller Y.

    * **Case 3**:
      If the crosswalk center's Y is greater than the street center point's Y value, we
      assume the vehicle is moving from "x_larger" to "x_smaller."

      * For from_coord, choose the vertex with the larger X.
      * For to_coord, choose the vertex with the smaller X.

    * **Case 4**:
      If the crosswalk center's Y is less than the street center point's Y value, then
      we assume the reverse.

      * For from_coord, choose the vertex with the smaller X.
      * For to_coord, choose the vertex with the larger X.
    """
    con.execute(
        """
        -- Add columns to store the from/to direction
        ALTER TABLE crosswalk_centers DROP COLUMN IF EXISTS from_coord;
        ALTER TABLE crosswalk_centers DROP COLUMN IF EXISTS to_coord;
        
        ALTER TABLE crosswalk_centers ADD COLUMN from_coord VARCHAR;
        ALTER TABLE crosswalk_centers ADD COLUMN to_coord VARCHAR;
        """
    )
    _identify_vehicle_direction_oneway(con)
    _identify_vehicle_direction_twoway(con)


def _identify_vehicle_direction_oneway(con: duckdb.DuckDBPyConnection):
    """Identify the direction of the vehicle for one-way streets."""
    con.execute(
        """
        -- One-way streets
        UPDATE crosswalk_centers cc
        SET 
            from_coord = CASE
                -- Compare the distance from the street's first point to the two endpoints of ped_edge_geom
                WHEN ST_Distance(
                        ST_PointN(ST_GeomFromText(s.geometry), 1),
                        ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 1)
                    )
                    <
                    ST_Distance(
                        ST_PointN(ST_GeomFromText(s.geometry), 1),
                        ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 2)
                    )
                THEN ST_AsText(ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 1))
                ELSE ST_AsText(ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 2))
            END,
            to_coord = CASE
                WHEN ST_Distance(
                        ST_PointN(ST_GeomFromText(s.geometry), 1),
                        ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 1)
                    )
                    <
                    ST_Distance(
                        ST_PointN(ST_GeomFromText(s.geometry), 1),
                        ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 2)
                    )
                THEN ST_AsText(ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 2))
                ELSE ST_AsText(ST_PointN(ST_GeomFromText(cc.ped_edge_geom), 1))
            END
        FROM street_segments s
        WHERE cc.street_segment_id = s.OBJECTID
        AND cc.is_oneway = TRUE;
        """
    )


def _identify_vehicle_direction_twoway(con: duckdb.DuckDBPyConnection):
    """Identify the direction of the vehicle for two-way streets."""
    con.execute(
        """
        -- Two-way streets
        UPDATE crosswalk_centers
        SET
            from_coord = CASE
                WHEN is_oneway = FALSE THEN
                    CASE
                        WHEN ST_X(ST_GeomFromText(geometry)) > ST_X(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     < ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_X(ST_GeomFromText(geometry)) < ST_X(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     > ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_Y(ST_GeomFromText(geometry)) > ST_Y(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     > ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_Y(ST_GeomFromText(geometry)) < ST_Y(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     < ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        ELSE 'undefined'
                    END
                ELSE from_coord
            END,
            
            to_coord = CASE
                WHEN is_oneway = FALSE THEN
                    CASE
                        WHEN ST_X(ST_GeomFromText(geometry)) > ST_X(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     > ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_X(ST_GeomFromText(geometry)) < ST_X(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     < ST_Y(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_Y(ST_GeomFromText(geometry)) > ST_Y(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     < ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        WHEN ST_Y(ST_GeomFromText(geometry)) < ST_Y(ST_GeomFromText(street_center_point))
                        THEN (
                            CASE 
                                WHEN ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 1)) 
                                     > ST_X(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                                THEN ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 1))
                                ELSE ST_AsText(ST_PointN(ST_GeomFromText(ped_edge_geom), 2))
                            END
                        )
                        ELSE 'undefined'
                    END
                ELSE to_coord
            END;
        """
    )
