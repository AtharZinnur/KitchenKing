"""
Database configuration and models for Pic2Kitchen
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model with dietary preferences and allergies"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dietary preferences
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_dairy_free = db.Column(db.Boolean, default=False)
    is_nut_free = db.Column(db.Boolean, default=False)
    is_halal = db.Column(db.Boolean, default=False)
    is_kosher = db.Column(db.Boolean, default=False)
    
    # Allergies stored as JSON
    allergies = db.Column(db.Text, default='[]')  # JSON array of allergies
    
    # Relationships
    favorites = db.relationship('RecipeFavorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('RecipeHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('RecipeRating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_allergies(self):
        """Get list of allergies"""
        try:
            return json.loads(self.allergies) if self.allergies else []
        except:
            return []
    
    def set_allergies(self, allergies_list):
        """Set allergies from list"""
        self.allergies = json.dumps(allergies_list)
    
    def __repr__(self):
        return f'<User {self.username}>'

class RecipeFavorite(db.Model):
    """Track user's favorite recipes"""
    __tablename__ = 'recipe_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.String(10), nullable=False)  # IndexFile from CSV
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)

class RecipeHistory(db.Model):
    """Track recipes viewed/cooked by users"""
    __tablename__ = 'recipe_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.String(10), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    cooked = db.Column(db.Boolean, default=False)
    cooked_at = db.Column(db.DateTime, nullable=True)
    detected_ingredients = db.Column(db.Text)  # JSON array of detected ingredients
    
class RecipeRating(db.Model):
    """User ratings for recipes"""
    __tablename__ = 'recipe_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.String(10), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id'),
        db.CheckConstraint('rating >= 1 AND rating <= 5'),
    )

class UserPreference(db.Model):
    """Track user preferences based on behavior"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient = db.Column(db.String(50), nullable=False)
    preference_score = db.Column(db.Float, default=0.5)  # 0-1, where 1 is highly preferred
    interaction_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'ingredient'),)

class IngredientInventory(db.Model):
    """Track user's ingredient inventory for leftover management"""
    __tablename__ = 'ingredient_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))  # kg, g, pieces, etc.
    expiry_date = db.Column(db.Date, nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='inventory')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'ingredient'),)