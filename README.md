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