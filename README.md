# night-light
SCOPE Santos-Volpe '24-25

## Getting Started

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


## Usage

### Download the YOLOv8 model

Download the YOLOv8 model from the following link: [YOLOv8](https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt). Place the model in the root directory.

### Set the environment variables

Create a `.env` file in the root directory and add the following environment variables:

```sh
IMAGE_PATH="path/to/image"
```

### Run the script

```sh
python pedestrian_detection.py
```