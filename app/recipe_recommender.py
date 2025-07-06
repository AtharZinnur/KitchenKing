import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import json
import os

class RecipeRecommender:
    """
    A simple recipe recommendation system based on ingredient matching.
    This replaces the Doc2Vec model with a more straightforward approach.
    """
    
    def __init__(self, recipe_csv_path: str):
        """Initialize the recommender with the recipe database."""
        self.df_recipe = pd.read_csv(recipe_csv_path, sep='\t')
        self.ingredient_columns = [col for col in self.df_recipe.columns 
                                  if col not in ['Unnamed: 0', 'FileName', 'IndexFile']]
        
    def find_recipes_by_ingredients(self, ingredients: List[str], top_n: int = 7) -> List[int]:
        """
        Find recipes that match the given ingredients.
        
        Args:
            ingredients: List of ingredient names detected from the image
            top_n: Number of top recipes to return
            
        Returns:
            List of recipe indices
        """
        # Convert ingredient names to match column names in the CSV
        ingredients = [ing.capitalize() for ing in ingredients]
        
        # Calculate match scores for each recipe
        scores = []
        for idx, row in self.df_recipe.iterrows():
            score = 0
            matched_ingredients = 0
            
            # Count how many of the detected ingredients are in this recipe
            for ingredient in ingredients:
                if ingredient in self.ingredient_columns and row[ingredient] == True:
                    matched_ingredients += 1
                    score += 10  # Base score for matching ingredient
            
            # Bonus for matching multiple ingredients
            if matched_ingredients > 1:
                score += matched_ingredients * 5
            
            # Penalty for having too many extra ingredients
            total_ingredients = sum(row[col] == True for col in self.ingredient_columns)
            if total_ingredients > 0:
                score -= (total_ingredients - matched_ingredients) * 0.5
            
            scores.append((idx, score, matched_ingredients))
        
        # Sort by score (descending) and then by number of matched ingredients
        scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Get the top recipes
        result = []
        for idx, score, matched in scores[:top_n]:
            if matched > 0:  # Only include recipes with at least one matching ingredient
                index_file = self.df_recipe.iloc[idx]['IndexFile']
                result.append(int(index_file))
        
        # If we don't have enough results, add some popular recipes
        if len(result) < top_n:
            # Add recipes with common ingredients
            common_ingredients = ['Chicken', 'Beef', 'Egg', 'Tomato', 'Bread']
            for idx, row in self.df_recipe.iterrows():
                if len(result) >= top_n:
                    break
                index_file = int(row['IndexFile'])
                if index_file not in result:
                    for ing in common_ingredients:
                        if row[ing] == True:
                            result.append(index_file)
                            break
        
        return result[:top_n]
    
    def find_similar_recipes(self, recipe_index: int, top_n: int = 5) -> List[int]:
        """
        Find recipes similar to a given recipe based on ingredient overlap.
        
        Args:
            recipe_index: Index of the reference recipe
            top_n: Number of similar recipes to return
            
        Returns:
            List of similar recipe indices
        """
        # Find the row for the given recipe
        ref_row = self.df_recipe[self.df_recipe['IndexFile'] == recipe_index].iloc[0]
        ref_ingredients = set(col for col in self.ingredient_columns if ref_row[col] == True)
        
        similarities = []
        for idx, row in self.df_recipe.iterrows():
            if int(row['IndexFile']) == recipe_index:
                continue
                
            # Calculate Jaccard similarity
            recipe_ingredients = set(col for col in self.ingredient_columns if row[col] == True)
            intersection = len(ref_ingredients.intersection(recipe_ingredients))
            union = len(ref_ingredients.union(recipe_ingredients))
            
            if union > 0:
                similarity = intersection / union
                similarities.append((int(row['IndexFile']), similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [idx for idx, _ in similarities[:top_n]]