"""
Authentication utilities for Pic2Kitchen
"""
import bcrypt
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def hash_pass(password):
    """Hash a password using bcrypt"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt())

def verify_pass(password, hashed):
    """Verify a password against its hash"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    return bcrypt.checkpw(password, hashed)

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_dietary_restrictions(user):
    """Get all dietary restrictions for a user"""
    restrictions = []
    
    if user.is_vegetarian:
        restrictions.append('vegetarian')
    if user.is_vegan:
        restrictions.append('vegan')
    if user.is_gluten_free:
        restrictions.append('gluten_free')
    if user.is_dairy_free:
        restrictions.append('dairy_free')
    if user.is_nut_free:
        restrictions.append('nut_free')
    if user.is_halal:
        restrictions.append('halal')
    if user.is_kosher:
        restrictions.append('kosher')
    
    return restrictions

def filter_recipes_by_dietary_restrictions(recipes, user):
    """Filter recipes based on user's dietary restrictions"""
    if not user.is_authenticated:
        return recipes
    
    restrictions = get_user_dietary_restrictions(user)
    allergies = user.get_allergies()
    
    # Map dietary restrictions to ingredients to avoid
    ingredient_restrictions = {
        'vegetarian': ['Beef', 'Pork', 'Chicken', 'Seafood', 'Shrimp', 'Lobster', 
                      'Crab', 'Squid', 'Oyster', 'Tuna', 'Salmon'],
        'vegan': ['Beef', 'Pork', 'Chicken', 'Seafood', 'Shrimp', 'Lobster', 
                  'Crab', 'Squid', 'Oyster', 'Tuna', 'Salmon', 'Egg'],
        'gluten_free': ['Bread'],
        'dairy_free': [],  # Would need dairy ingredients in CSV
        'nut_free': [],  # Would need nut ingredients in CSV
        'halal': ['Pork'],
        'kosher': ['Pork', 'Seafood', 'Shrimp', 'Lobster', 'Crab', 'Squid', 'Oyster']
    }
    
    # TODO: Implement actual filtering based on recipe ingredients
    # This would require loading recipe data and checking ingredients
    
    return recipes