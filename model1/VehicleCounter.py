import torch

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
      return res
    except FileNotFoundError as e:
      print(f"Error: File not found. Please check the path. Details: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
  def countMultiple(self,image_paths):
    result = []
    for img_path in image_paths:
      result.append(self.count(img_path))
    return result