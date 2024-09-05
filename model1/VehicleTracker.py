import supervision as sv
from ultralytics import YOLO
from tqdm import tqdm
import argparse
import numpy as np
import torch
import os,sys
import cv2
sys.path.append(os.path.abspath(os.path.join('..')))
from model1.my_utility import get_line_points,select_video

def process_video(
        source_video_path: str,
        target_video_path: str,
        confidence_threshold: float = 0.15,
        iou_threshold: float = 0.6
) -> None:
    # Load YOLO model
    model = YOLO('yolov8s.pt')
    model.classes = [2,3,5,7]
    model.conf = confidence_threshold
    model.iou = iou_threshold
    classes = list(model.names.values())
    
    # Extract the first frame from the video
    cap = cv2.VideoCapture(source_video_path)
    ret, first_frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to read video")
        return

    # Save the first frame to a temporary file
    first_frame_path = "../assets/examples/videos/first_frame.jpg"
    cv2.imwrite(first_frame_path, first_frame)

    # Get the user-defined points
    points = get_line_points(first_frame_path)
    if len(points) != 2:
        print("Error: Two points not selected.")
        return

    LINE_STARTS = sv.Point(points[0][0], points[0][1])
    LINE_END = sv.Point(points[1][0], points[1][1])

    # Set up frame generator and video info
    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)
    video_info = sv.VideoInfo.from_video_path(video_path=source_video_path)

    # Initialize ByteTracker and annotators
    tracker = sv.ByteTrack()
    box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()


    # Initialize line counter and line annotator
    line_counter = sv.LineZone(start=LINE_STARTS, end=LINE_END)
    line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=2, text_scale=0.5)

    # Create a VideoSink object to save the output video
    with sv.VideoSink(target_path=target_video_path, video_info=video_info) as sink:
        for frame in tqdm(frame_generator, total=video_info.total_frames):

            # Perform detection
            results = model(frame,verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)

            # Filter detections for cars and trucks (class IDs: 2 and 7)
            detections = detections[np.where((detections.class_id == 2) | (detections.class_id == 7))]

            # Update ByteTracker with detections
            detections = tracker.update_with_detections(detections)

            # Annotate bounding boxes
            annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=detections)

            # Prepare labels for annotated frame
            labels = []
            for index in range(len(detections.class_id)):
                labels.append(f"#{detections.tracker_id[index]} {classes[detections.class_id[index]]} {round(detections.confidence[index], 2)}")

            # Trigger line counter
            line_counter.trigger(detections=detections)

            # Annotate labels and line
            annotated_label_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
            line_annotate_frame = line_annotator.annotate(frame=annotated_label_frame, line_counter=line_counter)

            # Write the annotated frame to the output video
            sink.write_frame(frame=annotated_label_frame)
    
    return line_counter.in_count, line_counter.out_count

video_path, output_path = select_video()
if video_path:
    print(f"Selected video path: {video_path}")
    print(f"Generated output path: {output_path}")
else:
    print("No video file selected.")

process_video(
        video_path,
        output_path,
        confidence_threshold=0.15,
        iou_threshold=0.45
    )