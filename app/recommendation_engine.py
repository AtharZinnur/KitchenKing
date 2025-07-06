"""
Personalized Recipe Recommendation Engine
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func
from .database import db, RecipeHistory, RecipeRating, UserPreference, RecipeFavorite
from .recipe_recommender import RecipeRecommender
from .auth_utils import filter_recipes_by_dietary_restrictions

class PersonalizedRecommender:
    """
    Enhanced recipe recommender that learns from user behavior
    """
    
    def __init__(self, csv_path: str):
        """Initialize with base recommender"""
        self.base_recommender = RecipeRecommender(csv_path)
        self.learning_rate = 0.1
        self.min_interactions = 3
        
    def get_personalized_recipes(self, user, detected_ingredients: List[str], 
                               top_n: int = 7) -> List[Dict]:
        """
        Get personalized recipe recommendations based on:
        1. Detected ingredients
        2. User preferences
        3. Dietary restrictions
        4. Past behavior
        """
        
        # Get base recommendations
        base_recipes = self.base_recommender.find_recipes_by_ingredients(
            detected_ingredients, top_n=top_n * 3  # Get more for filtering
        )
        
        if not user or not user.is_authenticated:
            # Return base recommendations for non-authenticated users
            return self._format_recipes(base_recipes[:top_n])
        
        # Get user preferences
        user_prefs = self._get_user_preferences(user.id)
        
        # Get user history
        user_history = self._get_user_history(user.id)
        
        # Score recipes based on personalization
        scored_recipes = []
        for recipe_id in base_recipes:
            score = self._calculate_recipe_score(
                recipe_id, user, user_prefs, user_history, detected_ingredients
            )
            scored_recipes.append((recipe_id, score))
        
        # Sort by score (descending)
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by dietary restrictions
        filtered_recipes = []
        for recipe_id, score in scored_recipes:
            if self._check_dietary_compatibility(recipe_id, user):
                filtered_recipes.append(recipe_id)
                if len(filtered_recipes) >= top_n:
                    break
        
        # Track this interaction
        self._update_user_preferences(user.id, detected_ingredients)
        
        return self._format_recipes(filtered_recipes)
    
    def _calculate_recipe_score(self, recipe_id: str, user, user_prefs: Dict,
                              user_history: Dict, detected_ingredients: List[str]) -> float:
        """Calculate personalized score for a recipe"""
        score = 0.0
        
        # Base score from ingredient matching (already handled by base recommender)
        score += 1.0
        
        # User preference score
        recipe_data = self._get_recipe_data(recipe_id)
        if recipe_data:
            ingredients = recipe_data.get('ingredients', [])
            for ingredient in ingredients:
                if ingredient in user_prefs:
                    # Add preference score (0-1)
                    score += user_prefs[ingredient] * 0.5
        
        # History score (penalize recently viewed recipes)
        if recipe_id in user_history:
            days_ago = user_history[recipe_id]
            if days_ago < 7:
                score -= 0.5  # Reduce score for recipes viewed in last week
            elif days_ago < 14:
                score -= 0.2
        
        # Favorite bonus
        is_favorite = RecipeFavorite.query.filter_by(
            user_id=user.id, recipe_id=recipe_id
        ).first()
        if is_favorite:
            score += 0.8
        
        # Rating bonus
        rating = RecipeRating.query.filter_by(
            user_id=user.id, recipe_id=recipe_id
        ).first()
        if rating:
            score += (rating.rating - 3) * 0.2  # -0.4 to +0.4 based on rating
        
        # Diversity bonus (prefer recipes with different ingredients)
        unique_ingredients = set(ingredients) - set(detected_ingredients)
        score += len(unique_ingredients) * 0.05
        
        return score
    
    def _get_user_preferences(self, user_id: int) -> Dict[str, float]:
        """Get user ingredient preferences"""
        prefs = UserPreference.query.filter_by(user_id=user_id).all()
        return {pref.ingredient: pref.preference_score for pref in prefs}
    
    def _get_user_history(self, user_id: int) -> Dict[str, int]:
        """Get user recipe history with days since viewed"""
        history = RecipeHistory.query.filter_by(user_id=user_id).all()
        result = {}
        now = datetime.utcnow()
        
        for item in history:
            days_ago = (now - item.viewed_at).days
            result[item.recipe_id] = days_ago
            
        return result
    
    def _update_user_preferences(self, user_id: int, ingredients: List[str]):
        """Update user preferences based on interaction"""
        for ingredient in ingredients:
            pref = UserPreference.query.filter_by(
                user_id=user_id, ingredient=ingredient
            ).first()
            
            if not pref:
                # Create new preference
                pref = UserPreference(
                    user_id=user_id,
                    ingredient=ingredient,
                    preference_score=0.6,  # Start slightly positive
                    interaction_count=1
                )
                db.session.add(pref)
            else:
                # Update existing preference
                pref.interaction_count += 1
                
                # Increase preference score (with diminishing returns)
                if pref.interaction_count >= self.min_interactions:
                    pref.preference_score = min(1.0, 
                        pref.preference_score + self.learning_rate * (1 - pref.preference_score)
                    )
                
                pref.last_updated = datetime.utcnow()
        
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _check_dietary_compatibility(self, recipe_id: str, user) -> bool:
        """Check if recipe is compatible with user's dietary restrictions"""
        recipe_data = self._get_recipe_data(recipe_id)
        if not recipe_data:
            return True  # Allow if we can't check
        
        ingredients = recipe_data.get('ingredients', [])
        
        # Check dietary restrictions
        if user.is_vegetarian and any(ing in ['Beef', 'Pork', 'Chicken', 'Seafood', 
                                              'Shrimp', 'Lobster', 'Crab', 'Squid', 
                                              'Oyster', 'Tuna', 'Salmon'] for ing in ingredients):
            return False
            
        if user.is_vegan and any(ing in ['Beef', 'Pork', 'Chicken', 'Seafood', 
                                        'Shrimp', 'Lobster', 'Crab', 'Squid', 
                                        'Oyster', 'Tuna', 'Salmon', 'Egg'] for ing in ingredients):
            return False
            
        if user.is_halal and 'Pork' in ingredients:
            return False
            
        if user.is_kosher and any(ing in ['Pork', 'Seafood', 'Shrimp', 'Lobster', 
                                         'Crab', 'Squid', 'Oyster'] for ing in ingredients):
            return False
            
        if user.is_gluten_free and 'Bread' in ingredients:
            return False
        
        # Check allergies
        allergies = user.get_allergies()
        allergy_mapping = {
            'eggs': ['Egg'],
            'fish': ['Tuna', 'Salmon'],
            'shellfish': ['Shrimp', 'Lobster', 'Crab', 'Oyster'],
            'seafood': ['Seafood', 'Shrimp', 'Lobster', 'Crab', 'Squid', 'Oyster', 'Tuna', 'Salmon']
        }
        
        for allergy in allergies:
            if allergy in allergy_mapping:
                if any(ing in allergy_mapping[allergy] for ing in ingredients):
                    return False
        
        return True
    
    def _get_recipe_data(self, recipe_id: str) -> Dict:
        """Get recipe data from CSV"""
        try:
            # Get ingredients from CSV
            df = self.base_recommender.df_recipe
            if recipe_id in df.index:
                row = df.loc[recipe_id]
                ingredients = []
                for col in self.base_recommender.ingredient_columns:
                    if row[col] == True:
                        ingredients.append(col)
                return {'ingredients': ingredients}
        except:
            pass
        return None
    
    def _format_recipes(self, recipe_ids: List[str]) -> List[Dict]:
        """Format recipe IDs into full recipe data"""
        recipes = []
        for recipe_id in recipe_ids:
            try:
                # Load recipe JSON
                import json
                with open(f'./app/static/data/Food_recipe/food{recipe_id}.json', 'r') as f:
                    recipe_data = json.load(f)
                    recipe_data['recipe_id'] = recipe_id
                    recipes.append(recipe_data)
            except:
                # Fallback if JSON not found
                recipe_data = self._get_recipe_data(recipe_id)
                if recipe_data:
                    recipes.append({
                        'id': recipe_id,
                        'name': f'Recipe {recipe_id}',
                        'ingredients': recipe_data['ingredients'],
                        'recipe_id': recipe_id
                    })
        
        return recipes
    
    def track_recipe_view(self, user_id: int, recipe_id: str, detected_ingredients: List[str]):
        """Track when a user views a recipe"""
        history = RecipeHistory(
            user_id=user_id,
            recipe_id=recipe_id,
            detected_ingredients=json.dumps(detected_ingredients)
        )
        db.session.add(history)
        
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def track_recipe_cooked(self, user_id: int, recipe_id: str):
        """Track when a user cooks a recipe"""
        history = RecipeHistory.query.filter_by(
            user_id=user_id, recipe_id=recipe_id
        ).order_by(RecipeHistory.viewed_at.desc()).first()
        
        if history:
            history.cooked = True
            history.cooked_at = datetime.utcnow()
            
            # Boost preference for ingredients in this recipe
            recipe_data = self._get_recipe_data(recipe_id)
            if recipe_data:
                for ingredient in recipe_data['ingredients']:
                    pref = UserPreference.query.filter_by(
                        user_id=user_id, ingredient=ingredient
                    ).first()
                    if pref:
                        # Cooking a recipe is a strong positive signal
                        pref.preference_score = min(1.0, pref.preference_score + 0.2)
                        pref.interaction_count += 2
        
        try:
            db.session.commit()
        except:
            db.session.rollback()