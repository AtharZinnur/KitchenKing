"""
Forms for Pic2Kitchen application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    """Multiple checkbox field"""
    widget = ListWidget(html_tag='ul', prefix_label=False)
    option_widget = CheckboxInput()

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """Registration form with dietary preferences"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    
    # Dietary preferences
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    is_gluten_free = BooleanField('Gluten Free')
    is_dairy_free = BooleanField('Dairy Free')
    is_nut_free = BooleanField('Nut Free')
    is_halal = BooleanField('Halal')
    is_kosher = BooleanField('Kosher')
    
    # Common allergies
    allergies = MultiCheckboxField('Allergies', choices=[
        ('eggs', 'Eggs'),
        ('milk', 'Milk/Dairy'),
        ('peanuts', 'Peanuts'),
        ('tree_nuts', 'Tree Nuts'),
        ('fish', 'Fish'),
        ('shellfish', 'Shellfish'),
        ('wheat', 'Wheat'),
        ('soy', 'Soy'),
        ('sesame', 'Sesame'),
        ('other', 'Other')
    ])
    
    other_allergies = TextAreaField('Other Allergies', validators=[Length(max=500)])

class PreferencesForm(FlaskForm):
    """Form to update user preferences"""
    is_vegetarian = BooleanField('Vegetarian')
    is_vegan = BooleanField('Vegan')
    is_gluten_free = BooleanField('Gluten Free')
    is_dairy_free = BooleanField('Dairy Free')
    is_nut_free = BooleanField('Nut Free')
    is_halal = BooleanField('Halal')
    is_kosher = BooleanField('Kosher')
    
    allergies = MultiCheckboxField('Allergies', choices=[
        ('eggs', 'Eggs'),
        ('milk', 'Milk/Dairy'),
        ('peanuts', 'Peanuts'),
        ('tree_nuts', 'Tree Nuts'),
        ('fish', 'Fish'),
        ('shellfish', 'Shellfish'),
        ('wheat', 'Wheat'),
        ('soy', 'Soy'),
        ('sesame', 'Sesame'),
        ('other', 'Other')
    ])
    
    other_allergies = TextAreaField('Other Allergies', validators=[Length(max=500)])

class RecipeRatingForm(FlaskForm):
    """Form for rating recipes"""
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    review = TextAreaField('Review', validators=[Length(max=1000)])

class InventoryForm(FlaskForm):
    """Form for managing ingredient inventory"""
    ingredient = StringField('Ingredient', validators=[DataRequired(), Length(max=50)])
    quantity = StringField('Quantity', validators=[DataRequired()])
    unit = StringField('Unit', validators=[DataRequired(), Length(max=20)])