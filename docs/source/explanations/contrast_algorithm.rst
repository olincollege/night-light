Crosswalk Contrast Heuristic
============================

Overview
--------
This document outlines the process and algorithms used to compute contrast heuristic values for crosswalks. The calculation involves multiple steps, including data loading, crosswalk edge classification, center detection, vehicle direction analysis, and contrast computation.

Process Flow
------------

.. graphviz::
    :name: sphinx.ext.graphviz
    :caption: Data pipeline for crosswalk contrast and brightness heuristic
    :alt: Data pipeline for Crosswalk Contrast and Brightness Heuristic
    :align: center
    :layout: neato

    digraph "sphinx-ext-graphviz" {
        rankdir="LR";
        graph [fontname="Verdana", fontsize="12"];
        node [fontname="Verdana", fontsize="12", shape=box, style=rounded];

        load_data [label="Load GeoJSON data\n(crosswalks, streetlights, road segments)"];
        simplify [label="Simplify crosswalk geometry\nand decompose edges"];
        classify_edges [label="Classify edges\n(vehicle vs pedestrian)"];
        compute_centers [label="Compute crosswalk centers"];
        detect_direction [label="Detect vehicle direction at each center"];
        find_streetlights [label="Find streetlights near each center"];
        classify_sides [label="Classify streetlights by vehicle side\nand append distance info"];
        compute_heuristics [label="Compute brightness & contrast heuristics"];
        aggregate_results [label="Aggregate and store as table"];

        load_data -> simplify -> classify_edges -> compute_centers;
        compute_centers -> detect_direction -> find_streetlights;
        find_streetlights -> classify_sides -> compute_heuristics -> aggregate_results;
    }


1. **Load Datasets to Database**:

- The entry script `main.py` starts by generating a DuckDB database which will be the basis for analysis.
- Following GeoJSON datasets are loaded into the database:
    - Crosswalks (`datasets/boston_crosswalks.geojson`)
    - Streetlights (`datasets/boston_streetlights.geojson`)
    - Street segments (`datasets/boston_street_segments.geojson`)

2. **Classify Crosswalk Edges**:

- Convert crosswalk polygons into simplified minimum rotated rectangle. This ensures that there are always exactly 4 edges to a crosswalk.
- Break down crosswalk rectangles into individual edges. Each edge is represented by a unique ID and its start and end points.
- Classify crosswalk edges based on intersections with street segments. If the edge intersects with a street segment, classify as `is_vehicle_edge = TRUE` and otherwise `FALSE`. Alongside, store the intersecting street segment ID.

3. **Find Crosswalk Centers**:

- Find the points of intersection of the crosswalks with the street segments.
- Compute the midpoint of the intersection points.
- Compute the midpoints of the two edges of the crosswalk that pedestrians use.
- Compute the two midpoints between the midpoints of the edges and the midpoint of the intersections.
- Save the two midpoints as individual points in the database as a new table and ID them either `A` or `B`.

4. **Identify Vehicle Direction**:

.. note::
    Direction of vehicles is critical in determining the contrast level of a pedestrian observed by the driver. Thus, we identify the direction assuming that the vehicle always drives on the right side of the road, except for one-way streets.

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

- Adds the `streetlights` table to the `boston_constrast.db` to prepare for distance calculations.
- Creates the `crosswalk_centers_lights` table by copying `crosswalk_centers` and adding two empty columns: `streetlight_id` and `streetlight_dist`.
    – `streetlight_id` will contain an array of streetlight IDs for each cell.
    – `streetlight_dist` will contain an array of distances (in meters) between each streetlight and the crosswalk centerpoint for each cell. Note that the index of the distance will correlate with the index of the ID.
- Flips the (longitude, latitude) so that it becomes (latitude, longitude) for both the streetlight and crosswalk center geometries. The flipped geometry will be stored in a column called `geometry_lat_long`.
    – GeoJSON stores coordinates as (longitude, latitude) in WKT format. DuckDB's distance functions expect the coordinates to be in (latitude, longitude), so they need to be flipped.
- For each crosswalk centerpoint, finds all streetlights that are roughly within 20 meters (this number can be adjusted).
    – Uses `ST_DWithin`,  which calculates the Cartesian distance between the two points. Therefore, the value used to find the distances must be in degrees. `meters_to_degrees` provides a rough conversion using a default Boston latitude value, which tends to give an overestimate.
    – After identifying the streetlights, a more precise distance calculation is performed using ST_Distance_Sphere, which uses the Haversine formula to calculate the distance in meters.
    – This information is used to populate the `streetlight_id` and `streetlight_dist` columns.
    – Note that calculating the distances per centerpoint is the most time-intensive step of this process. The function `find_streetlights_crosswalk_centers` takes about 10 minutes for the Boston dataset.

6. **Identify streetlight groups**:

- Prior to computing the contrast heuristics, we need to determine the effects of each streetlight on the contrast. Thus, we categorize streetlights based on their spatial relationship to the crosswalk and the vehicle's direction (i.e., the driver's perspective) as either `to_side` or `from_side`.
- Define the Crosswalk Center Line:
    - Identify two center points (`A` and `B`) of the crosswalk.
    - Draw a straight line (`a_to_b`) connecting them.
- Compute Reference Direction:
    - Create a directional vector from the start (`from_coord`) to the end (`to_coord`) of the crosswalk.
- Associate Streetlights with Crosswalk Centers:
    - Identify all streetlights near the crosswalk within the masking radius from the previous step (e.g. 20 meters).
    - Draw a line from the crosswalk center to each streetlight (`center_to_light`).
- Classify Streetlights:
    - Compare the directional relationships between the reference vector and streetlight vectors by comparing the sign of cross product with the crosswalk center line.
    - If the streetlight has a similar direction to the reference direction, it belongs to the **to-side**; otherwise, it belongs to the **from-side**.
- Associate Distance Values
    - Retrieve the distance between each classified streetlight and the crosswalk center.
    - Store this information for later contrast calculation.

7. **Compute Contrast Heuristics**:

- The contrast heuristic measures the difference in lighting between the two sides of a crosswalk (side of the approaching driver, and the opposite side).
- Calculate Light Influence for Each Side:
    - Compute heuristic values separately for **to-side** and **from-side** based on the sum of inverse squared distances: :math:`\sum \left( \frac{1}{{\text{distance}^2}} \right)`
- Compare Lighting Balance:
    - If the difference between the two sides is small, classify the crosswalk as having **no contrast**.
    - If the from-side has more light influence, label it **positive contrast**.
    - If the to-side has more light influence, label it **negative contrast**.

- Store Results for Each Crosswalk Center:
    - `to_heuristic`: Light intensity sum for the to-side.
    - `from_heuristic`: Light intensity sum for the from-side.
    - `contrast_heuristic`: The final contrast classification.
    
.. image:: ../_static/images/crosswalk_diagram.png
  :width: 600
  :align: center
  :alt: Diagram of a two-way street