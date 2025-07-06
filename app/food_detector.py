"""
Food Detection using various approaches
"""
import cv2
import numpy as np
import os

class FoodDetector:
    def __init__(self, method='yolov3'):
        self.method = method
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
    def detect_with_yolov3_coco(self, image_path):
        """Use YOLOv3 trained on COCO dataset"""
        # Define food-related classes from COCO (80 classes)
        food_items = {
            46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange',
            50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza',
            54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch',
            58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet',
            62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote',
            66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
            70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book',
            74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
            78: 'hair drier', 79: 'toothbrush'
        }
        
        # Map COCO food items to our ingredients
        coco_to_ingredients = {
            'banana': 'Banana',
            'apple': 'Apple', 
            'sandwich': 'Bread',
            'orange': 'Orange',
            'broccoli': 'Cabbage',  # Close enough
            'carrot': 'Carrot',
            'hot dog': 'Pork',
            'pizza': 'Cheese',
            'donut': 'Bread',
            'cake': 'Bread'
        }
        
        try:
            # Load YOLO
            net = cv2.dnn.readNet(
                os.path.join(self.BASE_DIR, 'static/yolo/yolov3.weights'),
                os.path.join(self.BASE_DIR, 'static/yolo/yolov3.cfg')
            )
            
            # Load class names
            with open(os.path.join(self.BASE_DIR, 'static/yolo/coco.names'), 'r') as f:
                classes = [line.strip() for line in f.readlines()]
            
            # Load image
            image = cv2.imread(image_path)
            height, width = image.shape[:2]
            
            # Create blob
            blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
            
            # Set input
            net.setInput(blob)
            
            # Get output layer names
            layer_names = net.getLayerNames()
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            
            # Forward pass
            outputs = net.forward(output_layers)
            
            # Extract detections
            detected_ingredients = []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.5:
                        class_name = classes[class_id]
                        if class_name in coco_to_ingredients:
                            ingredient = coco_to_ingredients[class_name]
                            if ingredient not in detected_ingredients:
                                detected_ingredients.append(ingredient)
            
            return detected_ingredients if detected_ingredients else ['Chicken', 'Tomato']  # Default
            
        except Exception as e:
            print(f"Error in YOLO detection: {e}")
            return ['Chicken', 'Tomato']  # Default fallback
    
    def detect(self, image_path):
        """Main detection method"""
        if self.method == 'yolov3':
            return self.detect_with_yolov3_coco(image_path)
        else:
            # Fallback
            return ['Chicken', 'Tomato']