import duckdb

## Determines the direction of vehicle flow relative to pedestrian crosswalks and stores 
## this direction using from_coord and to_coord in the crosswalk_centers table.


def identify_vehicle_direction(con: duckdb.DuckDBPyConnection):
    """
    Identify the direction of the vehicle for each side of the road segment.

    One-way streets:
    1.	Crop Street Segment:
        Intersect the crosswalk boundary with its street segment to isolate the crossing
        portion.
    2.	Compute Relative Orientation:
        Use the 2D cross product of vectors from the cropped street segment and
        pedestrian edge to determine direction.
    3.	Assign Endpoints:
        If the cross product ≥ 0:
            from_coord = first point of ped_edge_geom
            to_coord = second point
        Else:
            Reverse the order.

    Two-way streets:
    - Case 1: If the crosswalk center’s X value is greater than the street center
        point’s X value, we assume the vehicle is moving from “y_smaller” to “y_larger.”
        – For the from_coord, choose the vertex of the pedestrian edge with the smaller
            Y value.
        – For the to_coord, choose the vertex with the larger Y value.
    - Case 2: If the crosswalk center’s X is less than the street center point’s X
        value, we assume the reverse:
        – For from_coord, choose the vertex with the larger Y.
        – For to_coord, choose the vertex with the smaller Y.
    - Case 3: If the crosswalk center’s Y is greater than the street center point’s Y
        value, we assume the vehicle is moving from “x_larger” to “x_smaller.”
        – For from_coord, choose the vertex with the larger X value.
        – For to_coord, choose the vertex with the smaller X value.
    - Case 4: If the crosswalk center’s Y is less than the street center point’s Y
        value, then:
        – For from_coord, choose the vertex with the smaller X value.
        – For to_coord, choose the vertex with the larger X value.
    """
    con.execute(
        """
        -- Add columns to store the from/to direction
        ALTER TABLE crosswalk_centers DROP COLUMN IF EXISTS from_coord;
        ALTER TABLE crosswalk_centers DROP COLUMN IF EXISTS to_coord;
        
        ALTER TABLE crosswalk_centers ADD COLUMN from_coord VARCHAR;
        ALTER TABLE crosswalk_centers ADD COLUMN to_coord VARCHAR;
        
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
