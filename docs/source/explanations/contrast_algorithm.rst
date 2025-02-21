Crosswalk Contrast Heuristic
============================

Overview
--------
This document outlines the process and algorithms used to compute contrast heuristic values for crosswalks. The calculation involves multiple steps, including data loading, crosswalk edge classification, center detection, vehicle direction analysis, and contrast computation.

Process Flow
------------

1. **Load Datasets to Database**:

- The entry script `main.py` starts by generating a mini version of a bronze-level database which will be used later for manipulation.
- Following GeoJSON datasets are loaded into the database:
    - Crosswalks (`tests/test_boston_crosswalk.geojson`)
    - Streetlights (`tests/test_boston_streetlights.geojson`)
    - Traffic lights (`tests/test_boston_traffic_lights.geojson`)

2. **Classify Crosswalk Edges**:

- Initialize `edge_classifier.db` with Boston's street segments and crosswalk datasets to process the edges of crosswalks.
- Convert crosswalk polygons into simplified minimum rotated rectangle. This ensures that there are always exactly 4 edges to a crosswalk.
- Break down crosswalk rectangles into individual edges. Each edge is represented by a unique ID and its start and end points.
- Classify crosswalk edges based on intersections with street segments. If the edge intersects with a street segment, classify as `is_vehicle_edge = TRUE` and otherwise `FALSE`. Alongside, store the intersecting street segment ID.

3. **Find Crosswalk Centers**:

.. note::
    Assume that there are always 2 centers for each crosswalk that mark each vehicle sides of the road. This means that we're assuming 2-way traffic.

- Find the points of intersection of the crosswalks with the street segments.
- Compute the midpoint of the intersection points.
- Compute the midpoints of the two edges of the crosswalk that pedestrians use.
- Compute the two midpoints between the midpoints of the edges and the midpoint of the intersections.
- Save the two midpoints as individual points in the database as a new table and ID them either `A` or `B`.

4. **Identify Vehicle Direction**:

.. note::
    Direction of vehicles is critical in determining the contrast level of a pedestrian observed by the driver. Thus, we identify the direction assuming that the vehicle always drives on the right side of the road.

- Case 1: If the crosswalk center’s X value is greater than the street center point’s X value, we assume the vehicle is moving from `y_smaller` to `y_larger`.
    – For the `from_coord`, choose the vertex of the pedestrian edge with the smaller Y value.
    – For the `to_coord`, choose the vertex with the larger Y value.
- Case 2: If the crosswalk center’s X is less than the street center point’s X value, we assume the reverse:
    – For `from_coord`, choose the vertex with the larger Y.
    – For `to_coord`, choose the vertex with the smaller Y.
- Case 3: If the crosswalk center’s Y is greater than the street center point’s Y value, we assume the vehicle is moving from `x_larger` to `x_smaller`.
    – For `from_coord`, choose the vertex with the larger X value.
    – For `to_coord`, choose the vertex with the smaller X value.
- Case 4: If the crosswalk center’s Y is less than the street center point’s Y value, then:
    – For `from_coord`, choose the vertex with the smaller X value.
    – For `to_coord`, choose the vertex with the larger X value.

5. **Compute Distances from Crosswalk to Streetlights**:

TODO

6. **Compute Contrast Heuristics**:

TODO
