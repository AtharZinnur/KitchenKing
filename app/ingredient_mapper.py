"""
Comprehensive ingredient mapping system for robust food detection
"""
import re
from typing import List, Dict, Optional

class IngredientMapper:
    """Maps detected objects to standardized ingredient names"""
    
    def __init__(self):
        # All ingredients from File_name.csv
        self.valid_ingredients = [
            'Seafood', 'Oyster', 'Crab', 'Salad', 'Squid', 'Shrimp', 'Lobster',
            'Carrot', 'Cabbage', 'Pumpkin', 'Squash', 'Tomato', 'Potato', 'Radish',
            'Cucumber', 'Mushroom', 'Bread', 'Egg', 'Pork', 'Beef', 'Chicken',
            'Tuna', 'Salmon'
        ]
        
        # Comprehensive mapping from COCO classes and variations to our ingredients
        self.coco_mappings = {
            # Direct food items in COCO
            'banana': 'Banana',
            'apple': 'Apple',
            'sandwich': 'Bread',
            'orange': 'Orange',
            'broccoli': 'Cabbage',  # Close vegetable
            'carrot': 'Carrot',
            'hot dog': 'Pork',
            'pizza': 'Bread',
            'donut': 'Bread',
            'cake': 'Bread',
            
            # Kitchen items that might indicate food
            'bottle': 'Beverage',
            'wine glass': 'Wine',
            'cup': 'Beverage',
            'fork': None,
            'knife': None,
            'spoon': None,
            'bowl': None,
            'dining table': None,
            'chair': None,
            
            # Animals that map to meat
            'cow': 'Beef',
            'sheep': 'Lamb',
            'bird': 'Chicken',
            
            # Person detection - ignore
            'person': None,
            
            # Vehicles and other objects - ignore
            'car': None,
            'truck': None,
            'bicycle': None,
            'motorcycle': None,
            'bus': None,
            'train': None,
            'traffic light': None,
            'stop sign': None,
            'bench': None,
            
            # Other potential food-related items
            'potted plant': 'Herbs',
            'oven': None,
            'toaster': None,
            'microwave': None,
            'refrigerator': None,
            'sink': None
        }
        
        # Additional keyword mappings for better detection
        self.keyword_mappings = {
            # Vegetables
            'vegetable': ['Carrot', 'Cabbage', 'Tomato'],
            'green': ['Cabbage', 'Cucumber'],
            'root': ['Carrot', 'Potato', 'Radish'],
            'leafy': ['Cabbage', 'Salad'],
            
            # Meats
            'meat': ['Beef', 'Pork', 'Chicken'],
            'poultry': ['Chicken'],
            'red meat': ['Beef', 'Pork'],
            'fish': ['Salmon', 'Tuna'],
            'seafood': ['Seafood', 'Shrimp', 'Crab', 'Lobster', 'Squid', 'Oyster'],
            
            # Other categories
            'grain': ['Bread'],
            'dairy': ['Egg'],  # Eggs are often in dairy section
            'protein': ['Egg', 'Chicken', 'Beef', 'Pork'],
            
            # Color-based mappings
            'orange': ['Carrot', 'Pumpkin', 'Squash'],
            'red': ['Tomato', 'Beef'],
            'yellow': ['Squash', 'Egg'],
            'green': ['Cucumber', 'Cabbage'],
            'brown': ['Mushroom', 'Potato', 'Bread'],
            'white': ['Egg', 'Mushroom', 'Bread', 'Chicken'],
            
            # Shape-based mappings
            'round': ['Tomato', 'Potato', 'Egg'],
            'long': ['Carrot', 'Cucumber'],
            
            # Common misdetections
            'ball': ['Tomato', 'Potato'],  # Round objects
            'stick': ['Carrot'],  # Long thin objects
            'plant': ['Cabbage', 'Salad'],  # Green plants
        }
        
        # Fuzzy matching patterns
        self.fuzzy_patterns = {
            r'chick.*': 'Chicken',
            r'beef.*': 'Beef',
            r'pork.*': 'Pork',
            r'egg.*': 'Egg',
            r'bread.*': 'Bread',
            r'tomat.*': 'Tomato',
            r'potat.*': 'Potato',
            r'carrot.*': 'Carrot',
            r'mushroom.*': 'Mushroom',
            r'shrimp.*': 'Shrimp',
            r'crab.*': 'Crab',
            r'fish.*': 'Seafood',
            r'salm.*': 'Salmon',
            r'tuna.*': 'Tuna',
            r'squid.*': 'Squid',
            r'lobst.*': 'Lobster',
            r'oyster.*': 'Oyster',
            r'cabba.*': 'Cabbage',
            r'cucumb.*': 'Cucumber',
            r'pump.*': 'Pumpkin',
            r'squa.*': 'Squash',
            r'radi.*': 'Radish',
            r'sala.*': 'Salad'
        }
    
    def map_to_ingredient(self, detected_object: str) -> Optional[str]:
        """Map a detected object to a valid ingredient"""
        detected_lower = detected_object.lower().strip()
        
        # 1. Check direct COCO mappings
        if detected_lower in self.coco_mappings:
            mapped = self.coco_mappings[detected_lower]
            if mapped and mapped in self.valid_ingredients:
                return mapped
        
        # 2. Check if it's already a valid ingredient (case-insensitive)
        for valid_ing in self.valid_ingredients:
            if detected_lower == valid_ing.lower():
                return valid_ing
        
        # 3. Check fuzzy patterns
        for pattern, ingredient in self.fuzzy_patterns.items():
            if re.match(pattern, detected_lower):
                if ingredient in self.valid_ingredients:
                    return ingredient
        
        # 4. Check keyword mappings
        for keyword, ingredients in self.keyword_mappings.items():
            if keyword in detected_lower:
                # Return the first valid ingredient from the list
                for ing in ingredients:
                    if ing in self.valid_ingredients:
                        return ing
        
        # 5. Partial matching
        for valid_ing in self.valid_ingredients:
            if valid_ing.lower() in detected_lower or detected_lower in valid_ing.lower():
                return valid_ing
        
        return None
    
    def map_multiple(self, detected_objects: List[str]) -> List[str]:
        """Map multiple detected objects to ingredients"""
        ingredients = []
        for obj in detected_objects:
            mapped = self.map_to_ingredient(obj)
            if mapped and mapped not in ingredients:
                ingredients.append(mapped)
        
        # If no valid ingredients found, suggest common ones
        if not ingredients:
            # Return some common ingredients based on what's frequently used
            common_ingredients = ['Chicken', 'Tomato', 'Egg']
            return [ing for ing in common_ingredients if ing in self.valid_ingredients][:2]
        
        return ingredients
    
    def enhance_detection(self, detected_objects: List[str], image_features: Dict = None) -> List[str]:
        """Enhance detection using additional image features"""
        mapped_ingredients = self.map_multiple(detected_objects)
        
        if image_features:
            # Add color-based detection
            if 'dominant_colors' in image_features:
                for color in image_features['dominant_colors']:
                    if color in self.keyword_mappings:
                        for ing in self.keyword_mappings[color]:
                            if ing in self.valid_ingredients and ing not in mapped_ingredients:
                                mapped_ingredients.append(ing)
                                break
            
            # Add shape-based detection
            if 'shapes' in image_features:
                for shape in image_features['shapes']:
                    if shape in self.keyword_mappings:
                        for ing in self.keyword_mappings[shape]:
                            if ing in self.valid_ingredients and ing not in mapped_ingredients:
                                mapped_ingredients.append(ing)
                                break
        
        return mapped_ingredients