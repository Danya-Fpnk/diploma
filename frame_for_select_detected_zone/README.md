# Frame Extraction for Traffic Analysis

This script extracts the first frame from a set of video files to create still images that can be used for object detection training.
The images are intended for use with polygon drawing tools such as Roboflow Polygon Zone,
allowing users to manually annotate areas where traffic objects need to be detected.

## Description

The `save_first_frame.py` script automates the extraction of the first frame from multiple traffic video files.
These images serve as a basis for creating training datasets for computer vision models, specifically for traffic management
systems where accurate object detection is crucial.

## Usage

Run the script with the following command:

```bash
python save_first_frame.py
```

This will generate JPG images from the first frames of the specified video files, which are stored in the video directory.

## Annotating Images

After running the script, you will have a set of images named according to their respective video sources. To annotate these images:

1. Visit [Roboflow Polygon Zone](https://roboflow.github.io/polygonzone/?ref=blog.roboflow.com).
2. Upload the generated images.
3. Use the polygon drawing tools to mark areas of interest (e.g., lanes, traffic lights, vehicles).
4. Save and download the annotated data for use in training your object detection models.
