import torch
import cv2
import sys,os
sys.path.append(os.path.abspath(os.path.join('..')))
from model1.my_utility import get_two_lines
import numpy as np

class VehicleCounter:
  def __init__(self,conf_thres=0.15,cnt_ratio=[1,2,3]):
    self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    self.model.conf = conf_thres
    self.model.classes = [2,3,5,7]
    self.cnt_ratio = cnt_ratio
    print(f"conf_thres : {conf_thres}")
    print(f"Weights ratio {cnt_ratio} for bike:car:truck")
    
  def count(self,image_path):
    try:
      results = self.model(image_path)
      # results.show()
      detections = results.pred[0]
      class_counts = {2: 0, 3: 0, 5: 0, 7: 0}
      for det in detections:
        cls_id = int(det[5].item())
        if cls_id in class_counts:
            class_counts[cls_id] += 1
      print(f"\n{image_path}")
      print(f"Cars: {class_counts[2]}")
      print(f"Motorcycles: {class_counts[3]}")
      print(f"Buses: {class_counts[5]}")
      print(f"Trucks: {class_counts[7]}")
      res = (
        class_counts[2] * self.cnt_ratio[1] + 
        class_counts[3] * self.cnt_ratio[0] +
        class_counts[5] * self.cnt_ratio[2] +
        class_counts[7] * self.cnt_ratio[1] 
      )
      print(f"Final weighted count : {res}")
      return res,(class_counts[2],class_counts[3],class_counts[5],class_counts[7])
    except FileNotFoundError as e:
      print(f"Error: File not found. Please check the path. Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
  def countMultiple(self,image_paths):
    result = []
    for img_path in image_paths:
      result.append(self.count(img_path)[0])
    return result
  
  def count_lanewise(self,image_path):
    try:
      line_points = get_two_lines(image_path)
      line1 = (line_points[0][0],line_points[0][1],line_points[1][0],line_points[1][1])
      line2 = (line_points[2][0],line_points[2][1],line_points[3][0],line_points[3][1])        
      # Load image
      img = cv2.imread(image_path)
      height, width, _ = img.shape

      # Define lines (points should be provided in (x1, y1, x2, y2) format)
      lines = [line1, line2]
      lines = [(line[0], line[1], line[2], line[3]) for line in lines]

      # Perform detection
      results = self.model(image_path)
      detections = results.pred[0]

      # Initialize lane counts
      lane_counts = {"left": {2: 0, 3: 0, 5: 0, 7: 0},
                      "middle": {2: 0, 3: 0, 5: 0, 7: 0},
                      "right": {2: 0, 3: 0, 5: 0, 7: 0}}

      for det in detections:
        x1, y1, x2, y2 = map(int, det[:4])
        cls_id = int(det[5].item())
        if cls_id not in lane_counts["left"]:
          continue

        # Determine lane based on bounding box center
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        if cx < lines[0][0]:
          lane = "left"
        elif cx < lines[1][0]:
          lane = "middle"
        else:
          lane = "right"

        lane_counts[lane][cls_id] += 1

      # Print results
      final_res = []
      for lane, counts in lane_counts.items():
        print(f"{lane.capitalize()} lane:")
        print(f"Cars: {counts[2]}")
        print(f"Motorcycles: {counts[3]}")
        print(f"Buses: {counts[5]}")
        print(f"Trucks: {counts[7]}")
        res = (
            counts[2] * self.cnt_ratio[1] + 
            counts[3] * self.cnt_ratio[0] +
            counts[5] * self.cnt_ratio[2] +
            counts[7] * self.cnt_ratio[1]
        )
        final_res.append(res)
        print(f"Final weighted count for {lane} lane: {res}")
      print(final_res)
      return tuple(final_res)
    except FileNotFoundError as e:
      print(f"Error: File not found. Please check the path. Details: {e}")
    except Exception as e:
      print(f"An error occurred: {e}") 

if __name__ == "__main__":
  vc = VehicleCounter()
  image_path = '../assets/examples/images/north.jpg'
  left_count, middle_count, right_count = vc.count_lanewise(image_path)
  print(f"Left lane count: {left_count}")
  print(f"Middle lane count: {middle_count}")
  print(f"Right lane count: {right_count}")