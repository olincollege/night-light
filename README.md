# night-light
SCOPE Santos-Volpe '24-25

## Overview

This repository explores the evaluation of lighting at crosswalks using GIS data for both crosswalks and streetlights. According to the U.S. Department of Transportation, 76% of pedestrian fatalities occur in dark conditions, even though only 25% of traffic occurs after dark. To reduce these fatalities, it is important to identify crosswalks at higher risk and those that do not meet recommended lighting guidelines. The process of evaluating the lighting of every crosswalk in any significant geographic area is time-consuming and currently impractical for governments. With the goal of saving time and money on these data collection and evaluative processes (and save lives!), this project works to provide a reliable, scalable method using GIS data to determine driver visibility of pedestrians in crosswalks at night. The project was done in collaboration with [Olin College of Engineering](https://www.olin.edu/research/data-illuminators-scalable-data-collection-nighttime-crosswalk-lighting), [Volpe National Transportation Systems Center](https://www.volpe.dot.gov/), and [The Santos Family Foundation](https://www.santosfamilyfoundation.org/).

Visit our documentation website for information about the code.

Check out our report for more information about the project, algorithms we used, and limitations.

## Quickstart 
This quickstart walks you through creating a duckdb database/parquet files for Boston.

### Prerequisites

- Python 3.12
- pip
- virtualenv

### Installation

1. Clone the repo
```sh
git clone git@github.com:olincollege/night-light.git
```
2. Create a virtual environment
```sh
python -m venv venv
```
4. Activate the virtual environment

`source venv/bin/activate` MacOS/Linux or `.\venv\Scripts\activate` for Windows

5. Install the required packages
```sh
pip install -r requirements.txt
```

### Run the script

```sh
python main.py
```

## Displaying Results
The main.py file outputs:
- DuckDB database
- crosswalk_centers_contrast.parquet
- crosswalk_centers_lights.parquet
- streetlights.parquet
- classified_streetlights.csv

The DuckDB database can easily be viewed using a tool such as [DBeaver](https://dbeaver.io/). For a more indepth look, we recommend using DBeaver to see what is happening at each step of the algorithm. DBeaver can be [downloaded here](https://dbeaver.io/download/) and [documentation on using it can be found here](https://duckdb.org/docs/stable/guides/sql_editors/dbeaver.html).

The parquet & CSV files can be uploaded to a tool like [kepler.gl](https://kepler.gl/), which is an open source geospatial analysis tool that has a mapping feature. Go here to see the Boston results in [kepler.gl](addlinkhereeeeeeee)

### How to use kepler.gl

#### Uploading files
- Click "Get started"
- Upload the parquet files from the output folder
- Click the “+ Add Data” button to add all the parquet files

#### Viewing data
- Click “+ Add Layer” to select a table from the parquet file to display
- Under the box labeled “Basic” click on “Select A Type”
- Select the Point option for displaying streetlights or crosswalk centerpoints
    - Depending on the type of data you may want to select line or polygon
- Then scroll down and under the box labeled “GeoJSON Feature” click on “Select a field” and pick the geometry field
- Scrolling down farther there are options to change the color, radius, and labels for the point

#### Other tips
- Hover over points on the map to see a pop-up with information about that point
- Use the funnel icon in the top left to filter and find specific crosswalks or streetlights
    - Click “+ Add Filter” and select the desired field 


## Datasets

The following spatial datasets are needed to run this code for any location:
- Crosswalks (spatial information: Polygon)
- Streetlights (spatial information: Point)
- Street_segments (spatial informations: LineString)

The code expects a GeoJSON file for each of these. It is fairly trivial to convert another file format to GeoJSON or make a few edits to the code to work with other file formats. The GeoJSONs get immediately dropped in duckdb table which is used to facilitate the calculations.

### Crosswalk Dataset
The crosswalk dataset should contain polygons that represent the boundaries of the crosswalks. The dataset ideally should accurately reflect the real world, but there is an implicit understanding that the dataset may not be perfect since most cities do not have a comprehensive dataset of crosswalks. 

We’ve chosen Boston for its relative ease of access to various datasets and physical proximity to the team at Olin College of Engineering. UMass Amherst has been developing a dataset of all crosswalks in Massachusetts using computer vision model (YOLOv8) and aerial imagery. The dataset is not perfect, but it is a good starting point for the project, and has the potential to be applicable for states that also do not have a thorough catalog of their crosswalk assets. The dataset can be viewed at the [UMass Crosswalk Dataset](https://www.arcgis.com/apps/mapviewer/index.html?url=https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0&source=sd).

### Streetlights Dataset
The dataset should represent the geometries of the streetlights represented as points. Additional information such as the type of bulb, last-replacement year, and wattage, etc. are useful to have as well. After talking to Michael Donaghy, Superintendent of Street Lighting at the City of Boston Public Works Department, we learned that Boston has recently completed a full catalog of their streetlight assets in 2023. We acknowledge that many cities might not have this data available, in which case, [OpenStreetMap features](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dstreet_lamp) could be used to roughly estimate the streetlight locations. The Boston streetlight dataset can be viewed at the [Boston Streetlight Dataset](https://sdmaps.maps.arcgis.com/apps/dashboards/84e1553e754b424f9c544ab5079ed99f).

### Street Segments Dataset
The street segments dataset is used to identify the road segments (linestrings) that intersect with the crosswalks. The dataset should contain information about the geometry of the road segments, as well as any relevant attributes such as speed limits, traffic volume, and one-way status. Currently, only the one-way status attribute is utilized. The dataset can be obtained from the [Analyze Boston](https://data.boston.gov/dataset/boston-street-segments-sam-system) and viewed online on [ArcGIS platform](https://www.arcgis.com/apps/mapviewer/index.html?url=https://gisportal.boston.gov/arcgis/rest/services/SAM/Live_SAM_Address/FeatureServer/3&source=sd).


## How to Run with Different Data Sets

Add here
