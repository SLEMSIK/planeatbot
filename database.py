import logging
import sqlite3

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        chat_id INTEGER,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        day TEXT,
        meal TEXT,
        dish TEXT,
        calories INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_type TEXT,
        name TEXT,
        instructions TEXT,
        calories TEXT,
        image_url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        ingredient TEXT,
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        calories REAL,
        protein REAL,
        fats REAL,
        carbs REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tip TEXT
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM meal_plans")
    if cursor.fetchone()[0] == 0:
        insert_initial_meal_plans(cursor)
    
    cursor.execute("SELECT COUNT(*) FROM recipes")
    if cursor.fetchone()[0] == 0:
        insert_initial_recipes(cursor)
    
    cursor.execute("SELECT COUNT(*) FROM food_data")
    if cursor.fetchone()[0] == 0:
        insert_initial_food_data(cursor)
    
    cursor.execute("SELECT COUNT(*) FROM health_tips")
    if cursor.fetchone()[0] == 0:
        initial_tips = [
            ("Питайся разнообразно и сбалансированно."),
            ("Уделяй достаточно времени на приготовление пищи."),
            ("Не переедай и не пропускай приемы пищи."),
            ("Пей достаточно воды и других жидкостей."),
            ("Делай физические упражнения регулярно."),
            ("Следи за своим сном и стрессом.")
        ]
        cursor.executemany("INSERT INTO health_tips (tip) VALUES (?)", [(tip,) for tip in initial_tips])
        logging.info("Initial health tips data inserted")
    
    conn.commit()
    conn.close()
    logging.info("Database initialized with all tables and data")

def insert_initial_meal_plans(cursor):
    meal_plans = [
        ('Похудение', 'Понедельник', 'Завтрак', 'Овсянка с ягодами', 250),
        ('Похудение', 'Понедельник', 'Обед', 'Греческий салат с курицей', 400),
        ('Похудение', 'Понедельник', 'Ужин', 'Запеченная рыба с овощами', 350),
        ('Похудение', 'Вторник', 'Завтрак', 'Омлет из белков с овощами', 200),
        ('Похудение', 'Вторник', 'Обед', 'Суп из чечевицы', 300),
        ('Похудение', 'Вторник', 'Ужин', 'Индейка на гриле с брокколи', 350),
        ('Набор массы', 'Понедельник', 'Завтрак', 'Омлет из 4 яиц с сыром и авокадо', 600),
        ('Набор массы', 'Понедельник', 'Перекус 1', 'Протеиновый коктейль с бананом', 350),
        ('Набор массы', 'Понедельник', 'Обед', 'Куриная грудка с рисом и овощами', 700),
        ('Набор массы', 'Понедельник', 'Перекус 2', 'Творог с орехами и медом', 400),
        ('Набор массы', 'Понедельник', 'Ужин', 'Стейк с картофелем', 800),
        ('Набор массы', 'Вторник', 'Завтрак', 'Овсянка с арахисовым маслом и бананом', 550),
        ('Набор массы', 'Вторник', 'Перекус 1', 'Бутерброд с индейкой и сыром', 300),
        ('Набор массы', 'Вторник', 'Обед', 'Паста с фрикадельками', 750),
        ('Набор массы', 'Вторник', 'Перекус 2', 'Йогурт с гранолой', 300),
        ('Набор массы', 'Вторник', 'Ужин', 'Лосось с киноа', 650),
        ('Поддержание веса', 'Понедельник', 'Завтрак', 'Гранола с йогуртом и фруктами', 400),
        ('Поддержание веса', 'Понедельник', 'Обед', 'Сэндвич с индейкой и овощами', 450),
        ('Поддержание веса', 'Понедельник', 'Ужин', 'Киноа с запеченными овощами', 500),
        ('Поддержание веса', 'Вторник', 'Завтрак', 'Тосты с авокадо и яйцом', 450),
        ('Поддержание веса', 'Вторник', 'Обед', 'Куриный салат с орехами', 500),
        ('Поддержание веса', 'Вторник', 'Ужин', 'Запеченная рыба с бататом', 400)
    ]
    
    cursor.executemany(
        "INSERT INTO meal_plans (goal, day, meal, dish, calories) VALUES (?, ?, ?, ?, ?)",
        meal_plans
    )
    logging.info("Initial meal plans data inserted")

def insert_initial_recipes(cursor):
    recipes = [
        ('Завтрак', 'Омлет с овощами и сыром', 
         '1. Взбейте яйца в миске.\n2. Нарежьте овощи и добавьте к яйцам.\n3. Посыпьте тертым сыром, добавьте специи.\n4. Жарьте на среднем огне до готовности.', 
         'Около 350 ккал',
         'https://img1.russianfood.com/dycontent/images_upl/390/big_389184.jpg'),
        ('Обед', 'Греческий салат с курицей', 
         '1. Нарежьте овощи, сыр и оливки.\n2. Приготовьте курицу на гриле и нарежьте.\n3. Смешайте все ингредиенты.\n4. Заправьте оливковым маслом и лимонным соком, посыпьте орегано.', 
         'Около 400 ккал',
         'https://static.1000.menu/img/content-v2/eb/79/22217/grecheskii-salat-s-kuricei_1589111068_12_max.jpg'),
        ('Ужин', 'Запеченный лосось с овощами', 
         '1. Нарежьте овощи и выложите на противень.\n2. Полейте оливковым маслом, посолите и поперчите.\n3. Сверху положите филе лосося.\n4. Сбрызните лимонным соком и посыпьте зеленью.\n5. Запекайте при 180°C в течение 20 минут.', 
         'Около 380 ккал',
         'https://img.povar.ru/main/43/7f/e9/fc/zapechennii_losos_s_ovoshami-404089.jpg'),
        ('Десерт', 'Протеиновые панкейки с ягодами', 
         '1. Смешайте банан, яйца и протеин в блендере.\n2. Жарьте на антипригарной сковороде небольшими порциями.\n3. Подавайте с ягодами и корицей.', 
         'Около 250 ккал',
         'https://fitbreak.ru/wp-content/uploads/2021/05/belkovye-pankejki.jpg'),
        ('Напиток', 'Протеиновый смузи', 
         '1. Смешайте все ингредиенты в блендере до однородной массы.\n2. При необходимости добавьте лед.', 
         'Около 300 ккал',
         'https://edaplus.info/food_pictures/protein-smoothie.jpg')
    ]
    
    for recipe in recipes:
        cursor.execute(
            "INSERT INTO recipes (meal_type, name, instructions, calories, image_url) VALUES (?, ?, ?, ?, ?)",
            recipe
        )
        recipe_id = cursor.lastrowid
        
        # Add ingredients based on recipe
        if recipe[1] == 'Омлет с овощами и сыром':
            ingredients = ['3 яйца', '50г сыра', '1 помидор', '1/2 болгарского перца', 'зелень', 'соль, перец']
        elif recipe[1] == 'Греческий салат с курицей':
            ingredients = ['150г куриной грудки', '1 огурец', '1 помидор', '50г феты', '10 оливок', 'оливковое масло', 'лимонный сок', 'орегано']
        elif recipe[1] == 'Запеченный лосось с овощами':
            ingredients = ['150г филе лосося', 'цукини', 'болгарский перец', 'морковь', 'лук', 'оливковое масло', 'лимон', 'зелень', 'соль, перец']
        elif recipe[1] == 'Протеиновые панкейки с ягодами':
            ingredients = ['1 банан', '2 яйца', '30г протеинового порошка', '100г ягод', 'корица']
        elif recipe[1] == 'Протеиновый смузи':
            ingredients = ['1 банан', '200мл молока', '150г ягод', '30г протеинового порошка', '1 ст.л. меда']
            
        for ingredient in ingredients:
            cursor.execute(
                "INSERT INTO recipe_ingredients (recipe_id, ingredient) VALUES (?, ?)",
                (recipe_id, ingredient)
            )
    
    logging.info("Initial recipes and ingredients data inserted")

def insert_initial_food_data(cursor):
    foods = [
        ('курица', 165, 31, 3.6, 0),
        ('рис', 130, 2.7, 0.3, 28),
        ('гречка', 143, 5.7, 1.1, 25),
        ('овсянка', 68, 2.4, 1.4, 12),
        ('яйцо', 72, 6.3, 5, 0.4),
        ('молоко', 42, 2.8, 1, 4.7),
        ('творог', 103, 18, 1.8, 3.3),
        ('говядина', 187, 26, 9.9, 0),
        ('свинина', 242, 22, 16.5, 0),
        ('картофель', 77, 2, 0.1, 16.3),
        ('морковь', 41, 0.9, 0.2, 8.7),
        ('яблоко', 52, 0.3, 0.4, 11.8),
        ('банан', 96, 1.1, 0.2, 21.8),
        ('хлеб', 265, 7.5, 1, 53.4),
        ('сыр', 363, 24, 29.5, 0.3),
        ('макароны', 344, 10.4, 1.1, 69.7),
        ('масло', 748, 0.5, 82.5, 0.9),
        ('рыба', 144, 19.8, 7.6, 0),
        ('греческий йогурт', 59, 10, 0.4, 3.6)
    ]
    
    cursor.executemany(
        "INSERT INTO food_data (name, calories, protein, fats, carbs) VALUES (?, ?, ?, ?, ?)",
        foods
    )
    logging.info("Initial food data inserted")

def user_exists(user_id):
    """Check if a user with the given user_id exists in the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def add_user(user_id, username, first_name, last_name, chat_id):
    """Add a new user to the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, username, first_name, last_name, chat_id) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, first_name, last_name, chat_id)
    )
    conn.commit()
    conn.close()
    logging.info(f"Added new user: {user_id} - {username} - {first_name} {last_name}")

def get_meal_plan(goal):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT day, meal, dish, calories FROM meal_plans WHERE goal = ? ORDER BY day, CASE meal "
        "WHEN 'Завтрак' THEN 1 "
        "WHEN 'Перекус 1' THEN 2 "
        "WHEN 'Обед' THEN 3 "
        "WHEN 'Перекус 2' THEN 4 "
        "WHEN 'Ужин' THEN 5 "
        "ELSE 6 END",
        (goal,)
    )
    meals = cursor.fetchall()
    conn.close()
    return meals

def get_recipe(meal_type):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, instructions, calories, image_url FROM recipes WHERE meal_type = ?",
        (meal_type,)
    )
    recipe = cursor.fetchone()
    
    if recipe:
        recipe_id, name, instructions, calories, image_url = recipe
        
        # Get ingredients for this recipe
        cursor.execute(
            "SELECT ingredient FROM recipe_ingredients WHERE recipe_id = ?",
            (recipe_id,)
        )
        ingredients = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return {
            'name': name,
            'ingredients': ingredients,
            'instructions': instructions,
            'calories': calories,
            'image_url': image_url
        }
    
    conn.close()
    return None

def get_food_data():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, calories, protein, fats, carbs FROM food_data")
    foods = cursor.fetchall()
    
    food_data = {}
    for food in foods:
        name, calories, protein, fats, carbs = food
        food_data[name] = {
            'calories': calories,
            'protein': protein,
            'fats': fats,
            'carbs': carbs
        }
    
    conn.close()
    return food_data

def get_all_recipes():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, meal_type, name, calories FROM recipes ORDER BY meal_type")
    recipes = cursor.fetchall()
    
    conn.close()
    return recipes

def get_recipe_by_id(recipe_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, meal_type, name, instructions, calories, image_url FROM recipes WHERE id = ?",
        (recipe_id,)
    )
    recipe_data = cursor.fetchone()
    
    if recipe_data:
        recipe_id, meal_type, name, instructions, calories, image_url = recipe_data
        
        cursor.execute(
            "SELECT ingredient FROM recipe_ingredients WHERE recipe_id = ?",
            (recipe_id,)
        )
        ingredients = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return {
            'id': recipe_id,
            'meal_type': meal_type,
            'name': name,
            'instructions': instructions,
            'calories': calories,
            'image_url': image_url,
            'ingredients': ingredients
        }
    
    conn.close()
    return None


def get_all_meal_plans():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, goal, day, meal, dish, calories FROM meal_plans ORDER BY goal, day, meal")
    plans = cursor.fetchall()
    
    conn.close()
    return plans

def get_meal_plan_by_id(plan_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, goal, day, meal, dish, calories FROM meal_plans WHERE id = ?",
        (plan_id,)
    )
    plan = cursor.fetchone()
    
    conn.close()
    if plan:
        plan_id, goal, day, meal, dish, calories = plan
        return {
            'id': plan_id,
            'goal': goal,
            'day': day,
            'meal': meal,
            'dish': dish,
            'calories': calories
        }
    return None

def get_all_foods():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, calories, protein, fats, carbs FROM food_data ORDER BY name")
    foods = cursor.fetchall()
    
    conn.close()
    return foods

def get_food_by_id(food_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, calories, protein, fats, carbs FROM food_data WHERE id = ?",
        (food_id,)
    )
    food = cursor.fetchone()
    
    conn.close()
    if food:
        food_id, name, calories, protein, fats, carbs = food
        return {
            'id': food_id,
            'name': name,
            'calories': calories,
            'protein': protein,
            'fats': fats,
            'carbs': carbs
        }
    return None

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, username, first_name, last_name, registration_date FROM users ORDER BY registration_date DESC")
    users = cursor.fetchall()
    
    conn.close()
    return users

def get_health_tips():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tip FROM health_tips")
    tips = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tips 