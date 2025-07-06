"""
Recipe generator to create JSON recipe files based on ingredient combinations from CSV
"""
import json
import pandas as pd
from pathlib import Path

class RecipeGenerator:
    def __init__(self):
        # Recipe templates based on common ingredient combinations
        self.recipe_templates = {
            ('Chicken', 'Mushroom'): {
                'name': 'Creamy Chicken and Mushroom',
                'description': 'A delicious creamy chicken dish with sautéed mushrooms',
                'time': '30 minutes',
                'difficulty': 'Medium',
                'servings': 4,
                'instructions': [
                    'Season chicken breasts with salt and pepper',
                    'Heat oil in a large skillet over medium-high heat',
                    'Cook chicken until golden brown, about 6-7 minutes per side',
                    'Remove chicken and set aside',
                    'In the same pan, sauté sliced mushrooms until tender',
                    'Add garlic and cook for 1 minute',
                    'Pour in cream and chicken broth',
                    'Return chicken to pan and simmer for 10 minutes',
                    'Garnish with fresh parsley and serve'
                ]
            },
            ('Beef', 'Potato'): {
                'name': 'Classic Beef and Potato Stew',
                'description': 'Hearty beef stew with tender potatoes',
                'time': '2 hours',
                'difficulty': 'Easy',
                'servings': 6,
                'instructions': [
                    'Cut beef into 2-inch cubes and season with salt and pepper',
                    'Brown beef in a large pot with oil',
                    'Add onions and garlic, cook until softened',
                    'Add beef broth, tomato paste, and herbs',
                    'Simmer for 1 hour',
                    'Add cubed potatoes and carrots',
                    'Continue cooking for 30-40 minutes until vegetables are tender',
                    'Adjust seasoning and serve hot'
                ]
            },
            ('Shrimp', 'Tomato'): {
                'name': 'Garlic Shrimp with Tomatoes',
                'description': 'Quick and flavorful shrimp sautéed with fresh tomatoes',
                'time': '20 minutes',
                'difficulty': 'Easy',
                'servings': 4,
                'instructions': [
                    'Clean and devein shrimp',
                    'Heat olive oil in a large skillet',
                    'Add minced garlic and red pepper flakes',
                    'Add shrimp and cook until pink, about 2-3 minutes per side',
                    'Add diced tomatoes and white wine',
                    'Simmer for 5 minutes',
                    'Season with salt, pepper, and fresh basil',
                    'Serve over pasta or with crusty bread'
                ]
            },
            ('Egg', 'Bread'): {
                'name': 'Classic French Toast',
                'description': 'Golden brown French toast perfect for breakfast',
                'time': '15 minutes',
                'difficulty': 'Easy',
                'servings': 2,
                'instructions': [
                    'Whisk eggs with milk, cinnamon, and vanilla',
                    'Heat butter in a griddle or large skillet',
                    'Dip bread slices in egg mixture',
                    'Cook until golden brown on both sides',
                    'Serve with maple syrup and fresh berries'
                ]
            },
            ('Salmon', 'Salad'): {
                'name': 'Grilled Salmon Salad',
                'description': 'Healthy grilled salmon over mixed greens',
                'time': '25 minutes',
                'difficulty': 'Medium',
                'servings': 2,
                'instructions': [
                    'Season salmon fillets with salt, pepper, and lemon',
                    'Grill salmon for 4-5 minutes per side',
                    'Mix salad greens with cucumber, tomatoes, and red onion',
                    'Make vinaigrette with olive oil, lemon juice, and Dijon mustard',
                    'Place grilled salmon over salad',
                    'Drizzle with dressing and serve'
                ]
            },
            ('Pork', 'Cabbage'): {
                'name': 'Pork and Cabbage Stir Fry',
                'description': 'Asian-inspired pork and cabbage dish',
                'time': '25 minutes',
                'difficulty': 'Medium',
                'servings': 4,
                'instructions': [
                    'Slice pork into thin strips',
                    'Marinate pork in soy sauce, ginger, and garlic',
                    'Heat wok or large skillet over high heat',
                    'Stir-fry pork until cooked through',
                    'Add sliced cabbage and carrots',
                    'Stir-fry until vegetables are tender-crisp',
                    'Season with soy sauce and sesame oil',
                    'Serve over steamed rice'
                ]
            },
            ('Chicken', 'Potato', 'Carrot'): {
                'name': 'Roasted Chicken with Root Vegetables',
                'description': 'One-pan roasted chicken with potatoes and carrots',
                'time': '1 hour 15 minutes',
                'difficulty': 'Easy',
                'servings': 4,
                'instructions': [
                    'Preheat oven to 425°F (220°C)',
                    'Season chicken pieces with herbs and spices',
                    'Cut potatoes and carrots into chunks',
                    'Toss vegetables with olive oil, salt, and pepper',
                    'Arrange chicken and vegetables on a baking sheet',
                    'Roast for 45-60 minutes until chicken is golden',
                    'Let rest for 5 minutes before serving'
                ]
            },
            ('Squid', 'Tomato'): {
                'name': 'Calamari in Tomato Sauce',
                'description': 'Tender squid rings in rich tomato sauce',
                'time': '45 minutes',
                'difficulty': 'Medium',
                'servings': 4,
                'instructions': [
                    'Clean squid and cut into rings',
                    'Sauté onions and garlic in olive oil',
                    'Add crushed tomatoes and herbs',
                    'Simmer sauce for 15 minutes',
                    'Add squid rings to sauce',
                    'Cook for 20-25 minutes until tender',
                    'Season with salt and pepper',
                    'Serve with pasta or crusty bread'
                ]
            }
        }
        
        # Default recipe template for combinations not in templates
        self.default_template = {
            'name': 'Mixed Ingredient Dish',
            'description': 'A delicious combination of fresh ingredients',
            'time': '30 minutes',
            'difficulty': 'Medium',
            'servings': 4,
            'instructions': [
                'Prepare all ingredients by washing and cutting as needed',
                'Heat oil in a large pan over medium heat',
                'Cook protein ingredients first until done',
                'Add vegetables and sauté until tender',
                'Season with salt, pepper, and herbs',
                'Combine all ingredients and heat through',
                'Adjust seasoning to taste',
                'Serve hot with appropriate sides'
            ]
        }
    
    def get_recipe_name(self, ingredients):
        """Generate a recipe name based on ingredients"""
        if not ingredients:
            return "Simple Dish"
        
        # Check for exact matches in templates
        for combo, template in self.recipe_templates.items():
            if all(ing in ingredients for ing in combo):
                return template['name']
        
        # Generate name based on main ingredients
        proteins = ['Chicken', 'Beef', 'Pork', 'Seafood', 'Shrimp', 'Salmon', 'Tuna', 'Squid', 'Crab', 'Lobster', 'Oyster']
        main_protein = next((ing for ing in ingredients if ing in proteins), None)
        
        vegetables = ['Carrot', 'Cabbage', 'Tomato', 'Potato', 'Mushroom', 'Cucumber', 'Pumpkin', 'Squash', 'Radish']
        main_veg = next((ing for ing in ingredients if ing in vegetables), None)
        
        if main_protein and main_veg:
            return f"{main_protein} with {main_veg}"
        elif main_protein:
            return f"Savory {main_protein} Dish"
        elif main_veg:
            return f"Fresh {main_veg} Delight"
        else:
            return f"{ingredients[0]} Special"
    
    def generate_recipe(self, index, ingredients):
        """Generate a complete recipe based on ingredients"""
        # Find matching template
        recipe = None
        for combo, template in self.recipe_templates.items():
            if all(ing in ingredients for ing in combo):
                recipe = template.copy()
                break
        
        if not recipe:
            recipe = self.default_template.copy()
            recipe['name'] = self.get_recipe_name(ingredients)
        
        # Add metadata
        recipe['id'] = f"{index:05d}"
        recipe['ingredients'] = ingredients
        recipe['tags'] = self._generate_tags(ingredients)
        
        # Add nutritional info (simplified)
        recipe['nutrition'] = {
            'calories': 250 + len(ingredients) * 50,
            'protein': '25g' if any(ing in ['Chicken', 'Beef', 'Pork', 'Seafood', 'Egg'] for ing in ingredients) else '10g',
            'carbs': '30g' if any(ing in ['Potato', 'Bread', 'Squash'] for ing in ingredients) else '15g',
            'fat': '12g'
        }
        
        # Add chef tips
        recipe['tips'] = self._generate_tips(ingredients)
        
        return recipe
    
    def _generate_tags(self, ingredients):
        """Generate relevant tags for the recipe"""
        tags = []
        
        # Diet tags
        if 'Seafood' in ingredients or any(ing in ['Shrimp', 'Salmon', 'Tuna', 'Squid', 'Crab', 'Lobster', 'Oyster'] for ing in ingredients):
            tags.append('pescatarian')
        if not any(ing in ['Chicken', 'Beef', 'Pork', 'Seafood', 'Shrimp', 'Salmon', 'Tuna', 'Squid', 'Crab', 'Lobster', 'Oyster', 'Egg'] for ing in ingredients):
            tags.append('vegetarian')
        if 'Salad' in ingredients:
            tags.append('healthy')
            tags.append('light')
        
        # Meal type tags
        if 'Egg' in ingredients and 'Bread' in ingredients:
            tags.append('breakfast')
        elif any(ing in ['Beef', 'Chicken', 'Pork'] for ing in ingredients):
            tags.append('dinner')
            tags.append('main-course')
        
        # Cooking method tags
        if any(ing in ['Potato', 'Carrot', 'Squash'] for ing in ingredients):
            tags.append('roasted')
        if any(ing in ['Shrimp', 'Squid'] for ing in ingredients):
            tags.append('seafood')
            
        return tags
    
    def _generate_tips(self, ingredients):
        """Generate cooking tips based on ingredients"""
        tips = []
        
        if 'Chicken' in ingredients:
            tips.append("Use a meat thermometer to ensure chicken reaches 165°F (74°C)")
        if 'Beef' in ingredients:
            tips.append("Let beef rest for 5 minutes after cooking for juicier results")
        if 'Seafood' in ingredients or 'Shrimp' in ingredients:
            tips.append("Don't overcook seafood - it should be just opaque")
        if 'Mushroom' in ingredients:
            tips.append("Don't wash mushrooms - wipe them clean with a damp paper towel")
        if 'Egg' in ingredients:
            tips.append("Use room temperature eggs for better results")
        if 'Potato' in ingredients:
            tips.append("Soak cut potatoes in cold water to remove excess starch")
            
        return tips

def generate_all_recipes():
    """Generate recipe JSON files for all entries in the CSV"""
    # Read the CSV file (tab-separated)
    df = pd.read_csv('/home/athar/Pic2kitchen-master/app/static/data/File_name.csv', sep='\t')
    
    # Initialize recipe generator
    generator = RecipeGenerator()
    
    # Get all ingredient columns
    ingredient_columns = [
        'Seafood', 'Oyster', 'Crab', 'Salad', 'Squid', 'Shrimp', 'Lobster',
        'Carrot', 'Cabbage', 'Pumpkin', 'Squash', 'Tomato', 'Potato', 'Radish',
        'Cucumber', 'Mushroom', 'Bread', 'Egg', 'Pork', 'Beef', 'Chicken',
        'Tuna', 'Salmon'
    ]
    
    # Create output directory
    output_dir = Path('/home/athar/Pic2kitchen-master/app/static/data/Food_recipe')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate recipes for each row
    for idx, row in df.iterrows():
        # Get ingredients for this recipe
        ingredients = [col for col in ingredient_columns if row[col] == True]
        
        if ingredients:  # Only create recipe if there are ingredients
            index = int(row['IndexFile'])
            recipe = generator.generate_recipe(index, ingredients)
            
            # Write to JSON file
            filename = output_dir / f"food{index:05d}.json"
            with open(filename, 'w') as f:
                json.dump(recipe, f, indent=2)
            
            if idx < 5:  # Print first few for verification
                print(f"Generated recipe {index}: {recipe['name']} with {', '.join(ingredients)}")

if __name__ == "__main__":
    generate_all_recipes()
    print("Recipe generation complete!")