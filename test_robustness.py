#!/usr/bin/env python3
"""
Test script to verify the robustness of the Pic2Kitchen application
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.recipe_recommender import RecipeRecommender
from app.ingredient_mapper import IngredientMapper
import pandas as pd

def test_recipe_recommender():
    """Test the recipe recommender functionality"""
    print("=" * 60)
    print("Testing Recipe Recommender")
    print("=" * 60)
    
    try:
        recommender = RecipeRecommender('./app/static/data/File_name.csv')
        print("✓ Recipe recommender loaded successfully")
        
        # Test with various ingredient combinations
        test_cases = [
            ['Chicken', 'Mushroom'],
            ['Beef', 'Potato', 'Carrot'],
            ['Shrimp', 'Tomato'],
            ['Egg', 'Bread'],
            ['Salmon', 'Salad']
        ]
        
        for ingredients in test_cases:
            print(f"\nTesting with ingredients: {ingredients}")
            recipes = recommender.find_recipes_by_ingredients(ingredients, top_n=5)
            print(f"  Found {len(recipes)} recipes: {recipes[:3]}...")
            
    except Exception as e:
        print(f"✗ Error testing recipe recommender: {e}")

def test_ingredient_mapper():
    """Test the ingredient mapper functionality"""
    print("\n" + "=" * 60)
    print("Testing Ingredient Mapper")
    print("=" * 60)
    
    try:
        mapper = IngredientMapper()
        print("✓ Ingredient mapper loaded successfully")
        
        # Test various COCO class mappings
        test_mappings = [
            'banana', 'apple', 'carrot', 'hot dog', 'pizza',
            'broccoli', 'chicken', 'cow', 'person', 'bottle'
        ]
        
        print("\nTesting COCO class mappings:")
        for item in test_mappings:
            mapped = mapper.map_to_ingredient(item)
            if mapped:
                print(f"  '{item}' -> '{mapped}'")
            else:
                print(f"  '{item}' -> No mapping")
                
        # Test fuzzy matching
        print("\nTesting fuzzy matching:")
        fuzzy_tests = ['chickn', 'beeff', 'tomatoo', 'potatoe', 'shrmp']
        for item in fuzzy_tests:
            mapped = mapper.map_to_ingredient(item)
            if mapped:
                print(f"  '{item}' -> '{mapped}'")
                
    except Exception as e:
        print(f"✗ Error testing ingredient mapper: {e}")

def test_recipe_json_files():
    """Test that recipe JSON files exist and are valid"""
    print("\n" + "=" * 60)
    print("Testing Recipe JSON Files")
    print("=" * 60)
    
    recipe_dir = './app/static/data/Food_recipe'
    
    try:
        # Count recipe files
        recipe_files = list(os.listdir(recipe_dir))
        json_files = [f for f in recipe_files if f.endswith('.json')]
        print(f"✓ Found {len(json_files)} recipe JSON files")
        
        # Test loading a few recipes
        import json
        for i in [1, 10, 50, 100]:
            filename = f"food{i:05d}.json"
            filepath = os.path.join(recipe_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    recipe = json.load(f)
                print(f"✓ Recipe {i}: {recipe['name']} - {', '.join(recipe['ingredients'])}")
            else:
                print(f"✗ Recipe {i} not found")
                
    except Exception as e:
        print(f"✗ Error testing recipe JSON files: {e}")

def test_csv_data_integrity():
    """Test the integrity of the CSV data"""
    print("\n" + "=" * 60)
    print("Testing CSV Data Integrity")
    print("=" * 60)
    
    try:
        # Load CSV
        df = pd.read_csv('./app/static/data/File_name.csv', sep='\t')
        print(f"✓ CSV loaded successfully with {len(df)} recipes")
        
        # Check columns
        ingredient_columns = [col for col in df.columns 
                            if col not in ['Unnamed: 0', 'FileName', 'IndexFile']]
        print(f"✓ Found {len(ingredient_columns)} ingredient columns:")
        print(f"  {', '.join(ingredient_columns[:5])}...")
        
        # Check data types
        for col in ingredient_columns:
            if df[col].dtype == bool:
                true_count = df[col].sum()
                print(f"✓ {col}: {true_count} recipes use this ingredient")
        
        # Find most common ingredient combinations
        print("\nMost common ingredient combinations:")
        for idx, row in df.head(5).iterrows():
            ingredients = [col for col in ingredient_columns if row[col] == True]
            if ingredients:
                print(f"  Recipe {row['IndexFile']}: {', '.join(ingredients)}")
                
    except Exception as e:
        print(f"✗ Error testing CSV data: {e}")

if __name__ == "__main__":
    print("Testing Pic2Kitchen Robustness")
    print("=" * 60)
    
    test_recipe_recommender()
    test_ingredient_mapper()
    test_recipe_json_files()
    test_csv_data_integrity()
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)