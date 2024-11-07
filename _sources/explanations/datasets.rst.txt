Dataset Choices
===============

Since creating a synthesized dataset based on multiple datasets is a critical part of the data processing pipeline, we have to make some choices regarding the datasets that we use. This document serves to explain the significant yet non-obvious logic and choices regarding different types of datasets.


Crosswalk Dataset
*****************

The crosswalk dataset should contain polygons that represent the boundaries of the crosswalks. The dataset ideally should accurately reflect the real world, but there is an implicit understanding that the dataset may not be perfect since most cities do not have a comprehensive dataset of crosswalks. The dataset should be in a format that can be easily read by the software, such as GeoJSON. In the testing module, you'll find the tests for fetching the crosswalk dataset and mapping it for the city of Boston. We've chosen Boston for its relative ease of access to various datasets and physical proximity to the team at Olin College of Engineering.

UMass Amherst has been developing a dataset of all crosswalks in Massachusetts using computer vision model (YOLOv8) and aerial imagery. The dataset is not perfect, but it is a good starting point for our project, and has the potential to be applicable for states that also do not have a thorough catalog of their crosswalk assets. The dataset can be viewed at the `following link <https://www.arcgis.com/apps/mapviewer/index.html?url=https://gis.massdot.state.ma.us/arcgis/rest/services/Assets/Crosswalk_Poly/FeatureServer/0&source=sd>`_.

Traffic Dataset
***************

Since our project is focused on pedestrian safety at nighttime on crosswalks, we need a dataset that contains information about the volume of traffic. MassDOT provides a convenient dataset that includes average annual daily traffic (AADT) counts for most roads in Massachusetts. The counts will be used to inform the risk of a pedestrian being hit by a car at a given crosswalk. The dataset can be viewed at the `following link <https://www.arcgis.com/apps/mapviewer/index.html?url=https://gis.massdot.state.ma.us/arcgis/rest/services/Roads/VMT/FeatureServer/10&source=sd>`_.