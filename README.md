# KitchenKing (formerly Pic2Kitchen)
AI-powered food app with advanced photo recognition and recipe recommendation system

KitchenKing will make your life way easy: It recognizes a photo of a ingredient and suggests possible recipes with step-by-step instructions for your culinary adventures!


# Target audience:
**KITCHENKING** will be a life-changer that makes your life way easier but healthier by suggesting the perfect and easiest recipes for you.

1.	Let be the money-saver: KitchenKing will help you consume all the leftover ingredients in fridge 
2.	Let be smart buyer: you found super discounted products at supermarket but don't know what to do with it – KitchenKing will help you out. 
3.	If you are a cooking lover , This app is perfect for you, you can cook different foods with unique recipes  
4.	If you are a hungry learner, You can be a masterChef by following step-by-step video. 


# How to use? 
By using advanced photo recognition and complex machine learning, KitchenKing gives you tailored suggestions on what to cook next. All you need to do is to take a photo of the ingredients. The rest of work, KitchenKing will do it for you. It instantly sends you tailored recipe suggestions! If you take two or more ingredients, then the app will show more recipes recommendations using those ingredients.

Add allergies and diet preferences, to get even more tailored results. It starts to learn what you personally like, by connecting patterns and taking into consideration different behaviors. The more you use the app, the better suggestions you get!

![](https://i.imgur.com/GaMHvRr.jpg)

# Architecture & Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface (Web)                         │
│                    ┌─────────────────────────┐                      │
│                    │   Upload Image Form     │                      │
│                    │   Recipe Display Page   │                      │
│                    └───────────┬─────────────┘                      │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Flask Application                             │
│  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   Routes/Views  │───▶│  Controllers │───▶│    Templates    │   │
│  │   (/send, /)    │    │              │    │  (HTML/Jinja2)  │   │
│  └─────────────────┘    └──────────────┘    └─────────────────┘   │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AI/ML Processing Pipeline                        │
│                                                                      │
│  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │  Image Upload   │───▶│ YOLO v3      │───▶│   Ingredient    │   │
│  │  & Validation   │    │ Object       │    │   Extraction    │   │
│  │                 │    │ Detection    │    │                 │   │
│  └─────────────────┘    └──────────────┘    └────────┬────────┘   │
│                                                       │             │
│                                                       ▼             │
│  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │  Recipe Match   │◀───│   Doc2Vec    │◀───│  Ingredient     │   │
│  │   Results       │    │  Similarity  │    │  Processing     │   │
│  │                 │    │  Matching    │    │                 │   │
│  └─────────────────┘    └──────────────┘    └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Storage                                 │
│  ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   Recipe JSON   │    │  YOLO Model  │    │  Doc2Vec Model  │   │
│  │     Files       │    │   Weights    │    │    (d2v_v4)     │   │
│  └─────────────────┘    └──────────────┘    └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Workflow

### 1. Image Upload Phase
- User uploads food ingredient photo through web interface
- Flask validates file type (png, jpg, jpeg, gif)
- Image saved to `static/images/upload/`

### 2. Object Detection Phase
- YOLO v3 model loads with custom food-trained weights
- Processes uploaded image to detect food items
- Draws bounding boxes around detected ingredients
- Saves annotated image as `predict.jpg`

### 3. Ingredient Processing Phase
- Extracts detected ingredient labels from YOLO output
- Maps detected objects to standardized ingredient names
- Creates ingredient list for recipe matching

### 4. Recipe Matching Phase
- Doc2Vec model computes ingredient embeddings
- Calculates similarity scores against recipe database
- Returns top N most similar recipes

### 5. Results Display Phase
- Renders recipe recommendations with:
  - Recipe names and images
  - Cooking instructions
  - Instructional videos (via video API)
  - Ingredient lists

**Use 'KITCHEN KING' BE HEALTHIER, SAVE MONEY, SAVE EARTH, SPEND LESS TIME, SPEND LESS EFFORT and have happy life.** 

## Setup Instructions

### Prerequisites
- Python 3.7+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AtharZinnur/KitchenKing.git
cd KitchenKing
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Required Files (Not Included)

Due to file size limitations, you need to download these files separately:

1. **YOLO Model Files** (required for ingredient detection):
   - `yolov3.cfg` - YOLO configuration file
   - `yolov3_last.weights` - YOLO trained weights (~236MB)
   - `yolo.names` - Class names for detected objects
   
   Place these files in: `app/static/yolo/`

2. **Doc2Vec Model** (required for recipe matching):
   - `d2v_v4.model` - Pre-trained Doc2Vec model
   
   Place this file in: `app/static/data/`

### Running the Application

1. Development mode:
```bash
python -m app.app
```

2. Production mode with gunicorn:
```bash
gunicorn app.app:app --bind 127.0.0.1:8000
```

The application will be available at http://127.0.0.1:8000

## Technologies Used
- Flask (Web Framework)
- YOLO v3 (Object Detection)
- Doc2Vec (Recipe Recommendation)
- OpenCV (Image Processing)
- Bootstrap (Frontend)

## Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.