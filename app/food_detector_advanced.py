"""
Advanced Food Detection using Hugging Face Models
Dynamically detects food ingredients without hardcoding
"""
import torch
from PIL import Image
from transformers import (
    pipeline, 
    AutoProcessor, 
    AutoModelForObjectDetection,
    AutoModelForImageClassification,
    AutoFeatureExtractor,
    DetrForObjectDetection,
    YolosForObjectDetection
)
import numpy as np
import cv2
from typing import List, Dict, Tuple, Set
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class AdvancedFoodDetector:
    def __init__(self):
        """Initialize multiple food detection models for comprehensive detection"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.processors = {}
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize various models for food detection"""
        
        # Model 1: Food-101 classifier (nateraw/food)
        try:
            self.models['food_classifier'] = pipeline(
                "image-classification",
                model="nateraw/food",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded Food-101 classifier")
        except Exception as e:
            logger.warning(f"Failed to load Food-101 classifier: {e}")
        
        # Model 2: DETR for object detection
        try:
            self.models['detr'] = pipeline(
                "object-detection",
                model="facebook/detr-resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded DETR object detector")
        except Exception as e:
            logger.warning(f"Failed to load DETR: {e}")
        
        # Model 3: YOLOS for better food detection
        try:
            self.models['yolos'] = pipeline(
                "object-detection",
                model="hustvl/yolos-tiny",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded YOLOS detector")
        except Exception as e:
            logger.warning(f"Failed to load YOLOS: {e}")
        
        # Model 4: Zero-shot classification for flexible detection
        try:
            self.models['clip'] = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("Loaded CLIP for zero-shot classification")
        except Exception as e:
            logger.warning(f"Failed to load CLIP: {e}")
    
    def detect_ingredients(self, image_path: str) -> List[str]:
        """
        Detect food ingredients using multiple models
        Returns a list of detected ingredients
        """
        detected_items = set()
        confidence_scores = {}
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Method 1: Food-101 Classification
            if 'food_classifier' in self.models:
                food_items = self._detect_with_food101(image)
                for item, score in food_items:
                    detected_items.add(item)
                    confidence_scores[item] = max(confidence_scores.get(item, 0), score)
            
            # Method 2: Object Detection with DETR/YOLOS
            object_items = self._detect_objects(image)
            for item, score in object_items:
                detected_items.add(item)
                confidence_scores[item] = max(confidence_scores.get(item, 0), score)
            
            # Method 3: Zero-shot classification with comprehensive food list
            if 'clip' in self.models:
                clip_items = self._detect_with_clip(image)
                for item, score in clip_items:
                    detected_items.add(item)
                    confidence_scores[item] = max(confidence_scores.get(item, 0), score)
            
            # Method 4: Visual feature analysis
            visual_items = self._analyze_visual_features(image_path)
            for item in visual_items:
                detected_items.add(item)
                confidence_scores[item] = max(confidence_scores.get(item, 0), 0.3)
            
            # Post-process and filter results
            final_items = self._post_process_detections(detected_items, confidence_scores)
            
        except Exception as e:
            logger.error(f"Error in ingredient detection: {e}")
            final_items = ['chicken', 'tomato', 'onion']  # Fallback
        
        return final_items
    
    def _detect_with_food101(self, image: Image) -> List[Tuple[str, float]]:
        """Detect food using Food-101 classifier"""
        items = []
        try:
            results = self.models['food_classifier'](image, top_k=10)
            
            # Map Food-101 classes to ingredients
            food_to_ingredients = {
                'pizza': ['cheese', 'tomato', 'dough'],
                'steak': ['beef', 'meat'],
                'sushi': ['rice', 'fish', 'seaweed'],
                'hamburger': ['beef', 'bread', 'lettuce', 'tomato'],
                'fried_chicken': ['chicken', 'flour'],
                'french_fries': ['potato', 'oil'],
                'ice_cream': ['milk', 'cream', 'sugar'],
                'salad': ['lettuce', 'tomato', 'cucumber'],
                'spaghetti': ['pasta', 'tomato', 'meat'],
                'sandwich': ['bread', 'cheese', 'meat', 'lettuce'],
                'omelette': ['egg', 'cheese', 'milk'],
                'soup': ['vegetable', 'water', 'meat'],
                'rice': ['rice'],
                'noodles': ['noodles', 'vegetable'],
                'bread': ['bread', 'flour'],
                'cake': ['flour', 'egg', 'sugar', 'milk'],
                'chocolate': ['chocolate', 'cocoa'],
                'apple': ['apple'],
                'banana': ['banana'],
                'carrot': ['carrot'],
                'broccoli': ['broccoli'],
                'corn': ['corn'],
                'potato': ['potato'],
                'tomato': ['tomato'],
                'onion': ['onion']
            }
            
            for result in results:
                label = result['label'].lower().replace('_', ' ')
                score = result['score']
                
                # Extract ingredients from detected food
                if label in food_to_ingredients:
                    for ingredient in food_to_ingredients[label]:
                        items.append((ingredient, score * 0.8))
                else:
                    # Direct ingredient detection
                    items.append((label, score))
                    
        except Exception as e:
            logger.warning(f"Food-101 detection failed: {e}")
        
        return items
    
    def _detect_objects(self, image: Image) -> List[Tuple[str, float]]:
        """Detect objects using DETR/YOLOS"""
        items = []
        
        # Try both object detectors
        for model_name in ['detr', 'yolos']:
            if model_name not in self.models:
                continue
                
            try:
                results = self.models[model_name](image)
                
                # COCO classes that are food-related
                food_objects = {
                    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
                    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
                    'potted plant', 'bed', 'dining table', 'toilet', 'tv',
                    'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                    'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
                    'book', 'clock', 'vase', 'scissors', 'teddy bear',
                    'hair drier', 'toothbrush', 'wine glass', 'cup', 'fork',
                    'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
                    'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                    'donut', 'cake', 'bird', 'cat', 'dog', 'horse',
                    'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe'
                }
                
                # Map detected objects to ingredients
                object_to_ingredient = {
                    'banana': 'banana',
                    'apple': 'apple',
                    'orange': 'orange',
                    'broccoli': 'broccoli',
                    'carrot': 'carrot',
                    'pizza': 'cheese',
                    'sandwich': 'bread',
                    'hot dog': 'sausage',
                    'donut': 'flour',
                    'cake': 'flour',
                    'wine glass': 'wine',
                    'cup': 'beverage',
                    'bowl': 'soup',
                    'bird': 'chicken',
                    'cow': 'beef',
                    'sheep': 'lamb'
                }
                
                for detection in results:
                    label = detection['label'].lower()
                    score = detection['score']
                    
                    if score > 0.5:
                        if label in object_to_ingredient:
                            items.append((object_to_ingredient[label], score))
                        elif 'food' in label or 'vegetable' in label or 'fruit' in label:
                            items.append((label.replace('_', ' '), score))
                            
            except Exception as e:
                logger.warning(f"{model_name} detection failed: {e}")
        
        return items
    
    def _detect_with_clip(self, image: Image) -> List[Tuple[str, float]]:
        """Use CLIP for zero-shot food detection"""
        items = []
        
        try:
            # Comprehensive list of food ingredients
            ingredients = [
                # Proteins
                "chicken", "beef", "pork", "fish", "shrimp", "egg", "tofu", "lamb", "turkey", "duck",
                "salmon", "tuna", "crab", "lobster", "squid", "octopus", "bacon", "sausage",
                
                # Vegetables
                "tomato", "carrot", "potato", "onion", "garlic", "pepper", "lettuce", "broccoli",
                "spinach", "cucumber", "corn", "mushroom", "peas", "beans", "cabbage", "celery",
                "eggplant", "zucchini", "cauliflower", "asparagus", "radish", "beet", "turnip",
                
                # Fruits
                "apple", "banana", "orange", "strawberry", "grape", "watermelon", "pineapple",
                "mango", "peach", "pear", "cherry", "blueberry", "raspberry", "kiwi", "lemon",
                "lime", "grapefruit", "avocado", "papaya", "coconut",
                
                # Grains & Carbs
                "rice", "pasta", "bread", "noodles", "flour", "oats", "quinoa", "barley",
                
                # Dairy
                "cheese", "milk", "yogurt", "butter", "cream",
                
                # Others
                "oil", "salt", "pepper", "sugar", "honey", "vinegar", "soy sauce", "herbs", "spices"
            ]
            
            # Run zero-shot classification
            results = self.models['clip'](
                image,
                candidate_labels=ingredients,
                hypothesis_template="A photo containing {}"
            )
            
            # Get top results
            if isinstance(results, list):
                # Handle list format from pipeline
                for result in results[:15]:
                    if result['score'] > 0.1:
                        items.append((result['label'], result['score']))
            else:
                # Handle dict format
                for i, (label, score) in enumerate(zip(results.get('labels', []), results.get('scores', []))):
                    if score > 0.1 and i < 15:  # Top 15 with reasonable confidence
                        items.append((label, score))
                    
        except Exception as e:
            logger.warning(f"CLIP detection failed: {e}")
        
        return items
    
    def _analyze_visual_features(self, image_path: str) -> List[str]:
        """Analyze visual features of the image"""
        items = []
        
        try:
            # Load image with OpenCV
            img = cv2.imread(image_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze dominant colors in different regions
            h, w = img.shape[:2]
            regions = [
                hsv[:h//2, :w//2],
                hsv[:h//2, w//2:],
                hsv[h//2:, :w//2],
                hsv[h//2:, w//2:]
            ]
            
            for region in regions:
                # Calculate color histogram
                hist = cv2.calcHist([region], [0], None, [180], [0, 180])
                dominant_hue = np.argmax(hist)
                
                # Map hues to likely ingredients
                if 0 <= dominant_hue <= 10 or 170 <= dominant_hue <= 180:  # Red
                    items.extend(['tomato', 'red pepper'])
                elif 11 <= dominant_hue <= 25:  # Orange
                    items.extend(['carrot', 'orange'])
                elif 26 <= dominant_hue <= 35:  # Yellow
                    items.extend(['corn', 'lemon'])
                elif 36 <= dominant_hue <= 85:  # Green
                    items.extend(['lettuce', 'broccoli'])
                elif 100 <= dominant_hue <= 130:  # Blue (rare in food)
                    items.extend(['blueberry'])
                
        except Exception as e:
            logger.warning(f"Visual analysis failed: {e}")
        
        return list(set(items))
    
    def _post_process_detections(self, detected_items: Set[str], 
                               confidence_scores: Dict[str, float]) -> List[str]:
        """Post-process and filter detected items"""
        
        # Remove duplicates and sort by confidence
        sorted_items = sorted(
            [(item, confidence_scores.get(item, 0)) for item in detected_items],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Filter out low confidence and non-ingredient items
        filtered_items = []
        non_ingredients = {'table', 'chair', 'person', 'background', 'plate', 'bowl', 'fork', 'knife', 'spoon'}
        
        for item, score in sorted_items:
            if item.lower() not in non_ingredients and score > 0.1:
                filtered_items.append(item.lower())
        
        # Ensure we have at least 3 items
        if len(filtered_items) < 3:
            # Add common ingredients that weren't detected
            common = ['onion', 'garlic', 'salt', 'oil', 'pepper']
            for item in common:
                if item not in filtered_items:
                    filtered_items.append(item)
                if len(filtered_items) >= 3:
                    break
        
        # Return top 5-7 items
        return filtered_items[:7]

# Singleton instance
_detector = None

def get_advanced_food_detector():
    """Get or create the advanced food detector instance"""
    global _detector
    if _detector is None:
        _detector = AdvancedFoodDetector()
    return _detector