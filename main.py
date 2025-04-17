import logging
import telebot
from telebot import types
import config
import database
import requests
from io import BytesIO
import schedule
import time
import random
import threading

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id
    
    if not database.user_exists(user_id):
        database.add_user(user_id, username, first_name, last_name, chat_id)
        welcome_message = f"👋 Привет, {first_name}!\n\n"
        welcome_message += "Добро пожаловать в PlanEat – твой персональный помощник для отслеживания калорий и планирования питания! 🥗\n\n С моей помощью ты сможешь:\n• Записывать и отслеживать калории 📊\n• Контролировать свой рацион 🍎\n• Достигать своих целей по питанию 🎯\n\n Начни свой путь к здоровому питанию прямо сейчас!\n\nДля начала моей работы, необходимо пройти небольшую регистрацию, отправь мне команду /reg"
        bot.reply_to(message, welcome_message)
    else:
        welcome_back_message = f"С возвращением, {first_name}! 🎉\n\n Рад видеть тебя снова в PlanEat. Продолжим отслеживать твои калории и поддерживать здоровое питание! 💪"
        bot.reply_to(message, welcome_back_message)

@bot.message_handler(commands=['reg'])
def reg(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    chat_id = message.chat.id

    if not database.user_exists(user_id):
        database.add_user(user_id, username, first_name, last_name, chat_id)
        bot.reply_to(message, "Спасибо! Ты успешно зарегистрирован!\nТеперь ты можешь воспользоваться командами: \n• /plan - для создания плана питания\n• /recipe - для получения рецепта\n• /track - для отслеживания калорий\n• /help - для просмотра доступных команд")
    else:
        bot.reply_to(message, "Ты уже зарегистрирован!")

@bot.message_handler(commands=['plan'])
def plan(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton('Похудение 🔽')
    btn2 = types.KeyboardButton('Набор массы 🔼')
    btn3 = types.KeyboardButton('Поддержание веса ⚖️')
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(message, "Выбери свою цель, чтобы получить подходящий план питания на неделю:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Похудение 🔽', 'Набор массы 🔼', 'Поддержание веса ⚖️'])
def create_plan(message):
    goal = message.text.split(' ')[0]  
    
    meal_plan = database.get_meal_plan(goal)
    
    if meal_plan:
        days = {}
        for day, meal, dish, calories in meal_plan:
            if day not in days:
                days[day] = []
            days[day].append((meal, dish, calories))
        
        plan_text = f"📋 План питания на неделю для {goal.lower()}:\n\n"
        
        for day in sorted(days.keys()):
            plan_text += f"🔸 {day}:\n"
            for meal, dish, calories in days[day]:
                plan_text += f"  • {meal}: {dish} ({calories} ккал)\n"
            plan_text += "\n"
            
        plan_text += "... и так далее на всю неделю"
    else:
        plan_text = "К сожалению, не удалось найти план питания для выбранной цели."
    
    markup = types.ReplyKeyboardRemove()
    bot.reply_to(message, plan_text, reply_markup=markup)
    bot.send_message(message.chat.id, "Хочешь получить детальные рецепты блюд из плана? Используй команду /recipe")

@bot.message_handler(commands=['recipe'])
def recipe(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Завтрак 🍳')
    btn2 = types.KeyboardButton('Обед 🍲')
    btn3 = types.KeyboardButton('Ужин 🍽️')
    btn4 = types.KeyboardButton('Десерт 🍰')
    btn5 = types.KeyboardButton('Напиток 🥤')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.reply_to(message, "Выбери тип блюда, для которого хочешь получить рецепт:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Завтрак 🍳', 'Обед 🍲', 'Ужин 🍽️', 'Десерт 🍰', 'Напиток 🥤'])
def get_recipe(message):
    meal_type = message.text.split(' ')[0]  
    
    recipe = database.get_recipe(meal_type)
    
    if recipe:
        image_sent = False
        if recipe['image_url']:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/jpeg,image/png,image/*;q=0.8,*/*;q=0.5',
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Referer': 'https://www.google.com/'
                }
                bot.send_photo(message.chat.id, recipe['image_url'])
                image_sent = True
                logging.info(f"Изображение успешно отправлено через прямой URL для: {recipe['name']}")
            except Exception as e1:
                logging.warning(f"Не удалось отправить изображение через прямой URL: {str(e1)}")
                
                try:
                    response = requests.get(recipe['image_url'], headers=headers, stream=True, timeout=10)
                    
                    if response.status_code == 200:
                        content = response.content
                        if content and len(content) > 100:  
                            photo = BytesIO(content)
                            photo.name = f"{recipe['name']}.jpg"
                            bot.send_photo(message.chat.id, photo)
                            image_sent = True
                            logging.info(f"Изображение успешно отправлено через BytesIO для: {recipe['name']}")
                        else:
                            logging.error(f"Получено пустое или слишком маленькое изображение для: {recipe['name']}")
                    else:
                        logging.error(f"Не удалось загрузить изображение для {recipe['name']}, код статуса: {response.status_code}")
                except Exception as e2:
                    logging.error(f"Вторая попытка отправки изображения также не удалась: {str(e2)}")
        
        response = f"🍽️ *{recipe['name']}*\n\n"
        if not image_sent:
            response += "*Изображение блюда недоступно*\n\n"
        
        response += "*Ингредиенты:*\n"
        for ingredient in recipe['ingredients']:
            response += f"• {ingredient}\n"
        response += f"\n*Приготовление:*\n{recipe['instructions']}\n\n"
        response += f"*Калорийность:* {recipe['calories']}"
        
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.reply_to(message, "К сожалению, у меня нет рецептов для этого типа блюда.")

@bot.message_handler(commands=['track'])
def track(message):
    markup = types.ForceReply(selective=True)
    bot.send_message(message.chat.id, "Введи название блюда и его приблизительный состав или вес, чтобы я подсчитал калории:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text.startswith("Введи название блюда"))
def calculate_calories(message):
    food_text = message.text.lower()
    
    calories = 0
    protein = 0
    fats = 0
    carbs = 0
    
    food_data = database.get_food_data()
    
    found_foods = []
    for food in food_data:
        if food in food_text:
            found_foods.append(food)
            calories += food_data[food]['calories']
            protein += food_data[food]['protein']
            fats += food_data[food]['fats']
            carbs += food_data[food]['carbs']
    
    if found_foods:
        response = f"📊 *Подсчет калорий для: {message.text}*\n\n"
        response += f"*Обнаруженные продукты:* {', '.join(found_foods)}\n\n"
        response += f"*Приблизительная пищевая ценность (на 100г каждого продукта):*\n"
        response += f"• Калории: {calories:.0f} ккал\n"
        response += f"• Белки: {protein:.1f} г\n"
        response += f"• Жиры: {fats:.1f} г\n"
        response += f"• Углеводы: {carbs:.1f} г\n\n"
        response += "⚠️ Это приблизительная оценка. Для более точного подсчета, укажите граммовку каждого продукта."
    else:
        response = "Извини, я не смог распознать продукты в твоем сообщении. Попробуй указать более распространенные продукты, например: курица, рис, яйца, молоко и т.д."
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "🍽️ *PlanEat - Калорийный помощник*\n\n"
    help_text += "*Доступные команды:*\n"
    help_text += "• /start - Начать работу с ботом\n"
    help_text += "• /reg - Зарегистрироваться в системе\n"
    help_text += "• /plan - Создать план питания на основе твоей цели\n"
    help_text += "• /recipe - Получить рецепты блюд\n"
    help_text += "• /track - Отслеживать калории в блюдах\n"
    help_text += "• /healthtip - Получить ежедневный совет по здоровью\n"
    help_text += "• /setreminder - Установить напоминания о приеме пищи\n"
    help_text += "• /help - Показать это сообщение\n\n"
    help_text += "Если у тебя есть вопросы или предложения, не стесняйся обращаться!"
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['healthtip'])
def send_health_tip(message):
    health_tips = database.get_health_tips()
    if health_tips:
        tip = random.choice(health_tips)
        bot.reply_to(message, f"💡 Совет по здоровью: {tip}")
    else:
        bot.reply_to(message, "Извините, в данный момент нет доступных советов по здоровью.")

@bot.message_handler(commands=['setreminder'])
def set_meal_reminder(message):
    bot.reply_to(message, "Напоминания о приеме пищи установлены на 8:00, 12:00 и 18:00.")
    schedule.every().day.at("08:00").do(lambda: bot.send_message(message.chat.id, "Время завтракать! 🍳"))
    schedule.every().day.at("12:00").do(lambda: bot.send_message(message.chat.id, "Время обедать! 🍲"))
    schedule.every().day.at("18:00").do(lambda: bot.send_message(message.chat.id, "Время ужинать! 🍽️"))

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler).start()

def main():
    database.init_db()
    test_image_urls()
    logging.info("Bot started")
    bot.infinity_polling()

def test_image_urls():
    logging.info("Проверка доступности URL с изображениями...")
    try:
        recipe = database.get_recipe("Завтрак")
        if recipe and recipe['image_url']:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(recipe['image_url'], headers=headers, timeout=5)
            if response.status_code == 200 and len(response.content) > 100:
                logging.info("Тестовый URL с изображением доступен и корректен")
            else:
                logging.warning(f"Проблема с тестовым URL: статус {response.status_code}, размер: {len(response.content)} байт")
    except Exception as e:
        logging.error(f"Ошибка при проверке URL с изображением: {str(e)}")

if __name__ == "__main__":
    main()
