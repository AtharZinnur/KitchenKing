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

# Workflow

![](https://i.imgur.com/LFhnmsR.png)


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