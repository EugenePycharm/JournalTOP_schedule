import requests
import json
import telebot
from telebot import types
import datetime
from get_token import get_token
from schedule_image import generate_schedule_image
import threading

bot = telebot.TeleBot('YOUR_BOT_TOKEN')

# Укажите ID вашего чата
CHAT_ID = YOUR_CHAT_ID  # Замените на нужный chat_id
last_pinned_message_id = None  # Переменная для хранения ID последнего закрепленного сообщения


@bot.message_handler(commands=['start'])
def start(message):
    print(
        f"[{datetime.datetime.now()}] Бот запущен. Пользователь {message.from_user.first_name} отправил команду /start.")
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Написать", url='https://t.me/berdigin')
    markup.add(button1)
    bot.send_message(message.chat.id,
                     "Привет, {0.first_name}, напиши в чат 'Расписание'. Бот находится в разработке, пиши свои предложения мне в телеграм".format(
                         message.from_user), reply_markup=markup)


# @bot.message_handler(func=lambda message: message.text == "Расписание")
# def lessons(message):
#     print(f"[{datetime.datetime.now()}] Пользователь {message.from_user.first_name} запросил расписание.")
#     send_schedule(message.chat.id)


def send_schedule(chat_id):
    """
        Эта функция отправляет расписание на указанный chat_id. Она извлекает расписание на следующий день,
        создает изображение расписания, отправляет его как фотографию в чат, закрепляет сообщение и открепляет предыдущее закрепленное сообщение.

        Параметры:
        chat_id (int): Идентификатор чата, в который будет отправлено расписание.

        Возвращает:
        None
        """
    global last_pinned_message_id  # Чтобы можно было модифицировать переменную внутри функции

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)  # Получаем расписание на следующий день
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # button1 = types.KeyboardButton("Расписание")
    # markup.add(button1)

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Отправка запроса на получение расписания на дату: {tomorrow_str}")

    url = "https://msapi.top-academy.ru/api/v2/schedule/operations/get-by-date"
    headers = {"authorization": "Bearer {}".format(get_token()),
               "referer": "https://journal.top-academy.ru/"}
    params = {"date_filter": tomorrow_str}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        try:
            if data:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Получено расписание: {data}")
                # Генерация и отправка изображения
                image_path = generate_schedule_image(data)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Изображение расписания сгенерировано: {image_path}")
                sent_message = bot.send_photo(chat_id, open(image_path, 'rb'), reply_markup=markup)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Изображение отправлено. ID сообщения: {sent_message.message_id}")

                # Открепляем предыдущее закрепленное сообщение, если оно было
                if last_pinned_message_id:
                    try:
                        bot.unpin_chat_message(chat_id, last_pinned_message_id)
                        print(
                            f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Предыдущее сообщение откреплено. ID: {last_pinned_message_id}")
                    except Exception as e:
                        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка при откреплении предыдущего сообщения: {str(e)}")
                        bot.send_message(chat_id, f"Ошибка при откреплении предыдущего сообщения: {str(e)}")

                # Закрепляем новое сообщение
                try:
                    bot.pin_chat_message(chat_id, sent_message.message_id)
                    last_pinned_message_id = sent_message.message_id  # Сохраняем ID нового закрепленного сообщения
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Новое сообщение закреплено. ID: {last_pinned_message_id}")
                except Exception as e:
                    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка при закреплении сообщения: {str(e)}")
                    bot.send_message(chat_id, f"Ошибка при закреплении сообщения: {str(e)}")
            else:
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Расписания нет.")
                bot.send_message(chat_id, text="Расписания пока что нет :(", reply_markup=markup)
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка при создании расписания: {str(e)}")
            bot.send_message(chat_id, text=f"Произошла ошибка при создании расписания: {str(e)}", reply_markup=markup)
    elif response.status_code == 401:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: истёк токен. Код 401.")
        bot.send_message(chat_id, text="Обнови токен :(", reply_markup=markup)
    else:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка при запросе расписания. Код: {response.status_code}")
        bot.send_message(chat_id, text=f"Ошибка: {response.status_code}", reply_markup=markup)


def schedule_daily_message():
    now = datetime.datetime.now()
    next_run = now.replace(hour=18, minute=58, second=0, microsecond=0)
    if now >= next_run:
        next_run += datetime.timedelta(days=1)
    delay = (next_run - now).total_seconds()

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Следующее расписание будет отправлено в {next_run}. Ожидание {round(delay)} секунд.")
    threading.Timer(delay, send_daily_message).start()


def send_daily_message():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Автоматическая отправка расписания.")
    send_schedule(chat_id=CHAT_ID)
    schedule_daily_message()


if __name__ == '__main__':
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск бота...")
    schedule_daily_message()
    bot.polling(none_stop=True)
