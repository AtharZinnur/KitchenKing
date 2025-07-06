import torch
import cv2
import numpy as np
import os

class YOLOv5Detector:
    def __init__(self):
        """Initialize YOLOv5 model for food detection"""
        # This will download the model on first use
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        
        # Define food-related classes from COCO dataset
        # YOLOv5 uses COCO dataset which includes some food items
        self.food_classes = {
            46: 'banana',
            47: 'apple',
            48: 'sandwich',
            49: 'orange',
            50: 'broccoli',
            51: 'carrot',
            52: 'hot dog',
            53: 'pizza',
            54: 'donut',
            55: 'cake',
        }
        
        # Map to ingredients in our system
        self.ingredient_mapping = {
            'banana': 'Banana',
            'apple': 'Apple',
            'sandwich': 'Bread',
            'orange': 'Orange',
            'broccoli': 'Broccoli',
            'carrot': 'Carrot',
            'hot dog': 'Sausage',
            'pizza': 'Cheese',
            'donut': 'Bread',
            'cake': 'Bread',
        }
    
    def detect(self, image_path):
        """Detect objects in image and return food items"""
        # Inference
        results = self.model(image_path)
        
        # Parse results
        detections = results.pandas().xyxy[0]  # Get detections as pandas DataFrame
        
        detected_foods = []
        for idx, detection in detections.iterrows():
            class_id = int(detection['class'])
            confidence = detection['confidence']
            
            # Check if it's a food item
            if class_id in self.food_classes and confidence > 0.5:
                food_name = self.food_classes[class_id]
                ingredient = self.ingredient_mapping.get(food_name, food_name.capitalize())
                if ingredient not in detected_foods:
                    detected_foods.append(ingredient)
        
        return detected_foods

# Usage example:
# detector = YOLOv5Detector()
# ingredients = detector.detect('path/to/image.jpg')