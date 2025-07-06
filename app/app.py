import os
from pathlib import Path
from flask import Flask, render_template, flash, jsonify, redirect, request, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import numpy as np
import pandas as pd
import json
from sqlalchemy import func

from . import yolo
from .database import db, User, RecipeFavorite, RecipeHistory, RecipeRating, UserPreference, IngredientInventory
from .config import config
from .recommendation_engine import PersonalizedRecommender
from .youtube_service import get_youtube_service
from .auth_utils import hash_pass, verify_pass
from .forms import LoginForm, RegistrationForm, PreferencesForm, RecipeRatingForm, InventoryForm
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(ROOT_DIR, 'static', 'images', 'upload')

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize services
youtube_service = get_youtube_service()
recommender = None

# Initialize recommender
try:
    recommender = PersonalizedRecommender('./app/static/data/File_name.csv')
    print("Personalized recipe recommender initialized successfully")
except Exception as e:
    print(f"Warning: Failed to initialize personalized recommender: {e}")
    from .recipe_recommender import RecipeRecommender
    try:
        recommender = RecipeRecommender('./app/static/data/File_name.csv')
        print("Basic recipe recommender initialized")
    except:
        recommender = None

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database tables on startup
with app.app_context():
    db.create_all()
    print("Database tables created")
# Load recipe CSV
try:
    df_recipe = pd.read_csv('./app/static/data/File_name.csv', sep='\t')
except Exception as e:
    print(f"Warning: Failed to load recipe file: {e}")
    df_recipe = None
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Login & Registration

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and verify_pass(form.password.data, user.password):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Welcome back!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)
        
        # Check if email exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hash_pass(form.password.data),
            is_vegetarian=form.is_vegetarian.data,
            is_vegan=form.is_vegan.data,
            is_gluten_free=form.is_gluten_free.data,
            is_dairy_free=form.is_dairy_free.data,
            is_nut_free=form.is_nut_free.data,
            is_halal=form.is_halal.data,
            is_kosher=form.is_kosher.data
        )
        
        # Set allergies
        allergies = form.allergies.data[:]
        if form.other_allergies.data:
            allergies.append(form.other_allergies.data)
        user.set_allergies(allergies)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


def get_current_index():
    try:
        image_path = Path(UPLOAD_DIR)
        image_files = image_path.glob('*.jpg')
        image_names = []
        for path in image_files:
            try:
                # Try to get the numeric part of the filename
                name = path.stem  # filename without extension
                if name.isdigit():
                    image_names.append(int(name))
            except:
                pass
        if image_names:
            current_index = max(image_names)
        else:
            current_index = 0
    except: 
        current_index = 0
    return current_index

current_index = get_current_index()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle multiple file uploads
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            flash('No files uploaded', 'warning')
            return redirect(request.url)
        
        uploaded_files = []
        all_detected_ingredients = set()
        
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                global current_index 
                current_index += 1 
                filename = f"{current_index}.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filename)
                
                # Detect ingredients from each image
                try:
                    ingredients = yolo.image_detect(filepath)
                    all_detected_ingredients.update(ingredients)
                except Exception as e:
                    print(f"Error detecting ingredients in {filename}: {e}")
        
        if not uploaded_files:
            flash('No valid files uploaded', 'danger')
            return redirect(request.url)
        
        # Store detected ingredients in session for use in kitchen route
        session['detected_ingredients'] = list(all_detected_ingredients)
        session['uploaded_files'] = uploaded_files
        
        # Redirect to kitchen with the first uploaded file
        return redirect(url_for('kitchen', filename=uploaded_files[0]))
    
    return render_template('index.html')

#
def make_query_string(ingredients):
    query_str =''
    if(len(ingredients)==0):
        return query_str
    elif(len(ingredients)==1):
        query_str = ingredients[0] +' == True'
        return query_str
    else:
        for ingredient in ingredients[:-1]:
            query_str = query_str + ingredient +' == True & '
        query_str = query_str + ingredients[-1] + ' == True'
        return query_str

def Query_index(ingredients,dframe):
    str_query = make_query_string(ingredients)
    result = dframe.query(str_query)['IndexFile']
    print('QUERY', result)
    if(len(result) !=0):
        return result.tolist()
    a =  ingredients[:-1]
    return Query_index(a ,dframe)

def GetFoodRecipe(index):
    # Convert index to int if it's a string
    if isinstance(index, str):
        index = int(index)
    name_file = f'./app/static/data/Food_recipe/food{index:05d}.json'
    try:
        with open(name_file) as json_data:
            data = json.load(json_data)
        return data
    except Exception as e:
        print(f"Error loading recipe {index}: {e}")
        return None

# These functions are now replaced by the RecipeRecommender class
def GetVideo(name):
    # assign some var get response from API below
    video_api.query(name)
    #return output as link video

@app.route('/kitchen/<filename>')
def kitchen(filename):
    PICTURE_DIR = os.path.join(UPLOAD_DIR, filename)
    
    # Check if we have ingredients from multiple uploads in session
    if 'detected_ingredients' in session:
        detected_ingredients = session.get('detected_ingredients', [])
        uploaded_files = session.get('uploaded_files', [filename])
        # Clear session after use
        session.pop('detected_ingredients', None)
        session.pop('uploaded_files', None)
    else:
        # Single file upload (backwards compatibility)
        detected_ingredients = yolo.image_detect(PICTURE_DIR)
        uploaded_files = [filename]
    
    if len(detected_ingredients) == 0:
        return render_template('Error.html')
    
    # Get recipes
    if recommender is not None:
        if isinstance(recommender, PersonalizedRecommender) and current_user.is_authenticated:
            # Get personalized recommendations
            recipes = recommender.get_personalized_recipes(
                current_user, detected_ingredients, top_n=15  # Get more to filter duplicates
            )
            # Track view
            for recipe in recipes:
                recommender.track_recipe_view(
                    current_user.id, recipe['recipe_id'], detected_ingredients
                )
        else:
            # Get basic recommendations using the base recommender
            result = recommender.base_recommender.find_recipes_by_ingredients(detected_ingredients, top_n=15)
            recipes = []
            seen_recipe_ids = set()
            for recipe_id in result:
                if recipe_id not in seen_recipe_ids:
                    recipe_data = GetFoodRecipe(recipe_id)
                    if recipe_data:
                        recipe_data['recipe_id'] = recipe_id
                        recipes.append(recipe_data)
                        seen_recipe_ids.add(recipe_id)
    else:
        # Fallback
        result = Query_index(detected_ingredients, df_recipe)
        recipes = []
        seen_recipe_ids = set()
        for recipe_id in result[:15]:  # Get more to filter duplicates
            if recipe_id not in seen_recipe_ids:
                recipe_data = GetFoodRecipe(recipe_id)
                if recipe_data:
                    recipe_data['recipe_id'] = recipe_id
                    recipes.append(recipe_data)
                    seen_recipe_ids.add(recipe_id)
    
    # Remove duplicate recipes by name and limit to 7 unique recipes
    unique_recipes = []
    seen_names = set()
    for recipe in recipes:
        recipe_name = recipe.get('name', '').lower().strip()
        if recipe_name and recipe_name not in seen_names:
            unique_recipes.append(recipe)
            seen_names.add(recipe_name)
            if len(unique_recipes) >= 7:
                break
    recipes = unique_recipes
    
    # Add video links with variation to avoid duplicates
    used_video_ids = set()
    for i, recipe in enumerate(recipes):
        # Add variation to search query to get different videos
        search_query = recipe.get('name', '')
        if i > 0:
            # Add ingredients to search for variety
            ingredients = recipe.get('ingredients', [])
            if ingredients:
                search_query += f" {ingredients[0]}"
        
        videos = youtube_service.search_recipe_videos(search_query, max_results=3)
        
        # Find a video that hasn't been used yet
        for video in videos:
            video_id = video.get('video_id', '')
            if video_id and video_id not in used_video_ids:
                recipe['video_url'] = video['embed_url']
                recipe['video_thumbnail'] = video['thumbnail_url']
                used_video_ids.add(video_id)
                break
        
        # If no unique video found, use the first one
        if 'video_url' not in recipe and videos:
            recipe['video_url'] = videos[0]['embed_url']
            recipe['video_thumbnail'] = videos[0]['thumbnail_url']
    
    return render_template('kitchen.html', 
                         img_name=filename,
                         uploaded_files=uploaded_files,
                         recipes=recipes,
                         detected_ingredients=detected_ingredients)

@app.route('/recipe')
def recipe():
    return render_template('list.html')

# Recipe detail page
@app.route('/recipe/<recipe_id>')
def recipe_detail(recipe_id):
    recipe_data = GetFoodRecipe(recipe_id)
    if not recipe_data:
        flash('Recipe not found', 'danger')
        return redirect(url_for('index'))
    
    # Get videos
    videos = youtube_service.search_recipe_videos(recipe_data.get('name', ''), max_results=3)
    
    # Get step-by-step videos if available
    step_videos = {}
    if 'instructions' in recipe_data:
        step_videos = youtube_service.get_step_by_step_videos(
            recipe_data['name'], recipe_data['instructions']
        )
    
    # Get user rating if logged in
    user_rating = None
    if current_user.is_authenticated:
        rating = RecipeRating.query.filter_by(
            user_id=current_user.id, recipe_id=recipe_id
        ).first()
        user_rating = rating.rating if rating else None
        
        # Check if favorite
        is_favorite = RecipeFavorite.query.filter_by(
            user_id=current_user.id, recipe_id=recipe_id
        ).first() is not None
    else:
        is_favorite = False
    
    # Get average rating
    avg_rating = db.session.query(func.avg(RecipeRating.rating)).filter_by(
        recipe_id=recipe_id
    ).scalar() or 0
    
    return render_template('recipe_detail.html',
                         recipe=recipe_data,
                         recipe_id=recipe_id,
                         videos=videos,
                         step_videos=step_videos,
                         user_rating=user_rating,
                         avg_rating=avg_rating,
                         is_favorite=is_favorite)

# User preference routes
@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    form = PreferencesForm()
    
    if request.method == 'GET':
        # Populate form with current preferences
        form.is_vegetarian.data = current_user.is_vegetarian
        form.is_vegan.data = current_user.is_vegan
        form.is_gluten_free.data = current_user.is_gluten_free
        form.is_dairy_free.data = current_user.is_dairy_free
        form.is_nut_free.data = current_user.is_nut_free
        form.is_halal.data = current_user.is_halal
        form.is_kosher.data = current_user.is_kosher
        form.allergies.data = current_user.get_allergies()
    
    if form.validate_on_submit():
        # Update preferences
        current_user.is_vegetarian = form.is_vegetarian.data
        current_user.is_vegan = form.is_vegan.data
        current_user.is_gluten_free = form.is_gluten_free.data
        current_user.is_dairy_free = form.is_dairy_free.data
        current_user.is_nut_free = form.is_nut_free.data
        current_user.is_halal = form.is_halal.data
        current_user.is_kosher = form.is_kosher.data
        
        # Update allergies
        allergies = form.allergies.data[:]
        if form.other_allergies.data:
            allergies.append(form.other_allergies.data)
        current_user.set_allergies(allergies)
        
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('preferences'))
    
    return render_template('preferences.html', form=form)

# API routes
@app.route('/api/favorite/<recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id):
    favorite = RecipeFavorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    
    if favorite:
        db.session.delete(favorite)
        is_favorite = False
    else:
        favorite = RecipeFavorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        is_favorite = True
    
    db.session.commit()
    return jsonify({'is_favorite': is_favorite})

@app.route('/api/rate/<recipe_id>', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    data = request.get_json()
    rating_value = data.get('rating')
    review = data.get('review', '')
    
    if not rating_value or not (1 <= rating_value <= 5):
        return jsonify({'error': 'Invalid rating'}), 400
    
    rating = RecipeRating.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id
    ).first()
    
    if rating:
        rating.rating = rating_value
        rating.review = review
        rating.updated_at = datetime.utcnow()
    else:
        rating = RecipeRating(
            user_id=current_user.id,
            recipe_id=recipe_id,
            rating=rating_value,
            review=review
        )
        db.session.add(rating)
    
    db.session.commit()
    
    # Update preferences based on rating
    if isinstance(recommender, PersonalizedRecommender) and rating_value >= 4:
        recipe_data = GetFoodRecipe(recipe_id)
        if recipe_data and 'ingredients' in recipe_data:
            recommender._update_user_preferences(current_user.id, recipe_data['ingredients'])
    
    return jsonify({'success': True})

@app.route('/api/cooked/<recipe_id>', methods=['POST'])
@login_required
def mark_cooked(recipe_id):
    if isinstance(recommender, PersonalizedRecommender):
        recommender.track_recipe_cooked(current_user.id, recipe_id)
    return jsonify({'success': True})

# Inventory management
@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    form = InventoryForm()
    
    if form.validate_on_submit():
        item = IngredientInventory.query.filter_by(
            user_id=current_user.id,
            ingredient=form.ingredient.data
        ).first()
        
        if item:
            item.quantity = float(form.quantity.data)
            item.unit = form.unit.data
            item.updated_at = datetime.utcnow()
        else:
            item = IngredientInventory(
                user_id=current_user.id,
                ingredient=form.ingredient.data,
                quantity=float(form.quantity.data),
                unit=form.unit.data
            )
            db.session.add(item)
        
        db.session.commit()
        flash('Inventory updated!', 'success')
        return redirect(url_for('inventory'))
    
    inventory_items = IngredientInventory.query.filter_by(user_id=current_user.id).all()
    return render_template('inventory.html', form=form, items=inventory_items)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 