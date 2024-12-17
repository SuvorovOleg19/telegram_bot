import telebot
import wikipedia
import re
import requests

# Создаем экземпляр бота
bot = telebot.TeleBot('7858339848:AAGUExcRJSBvhVcOB8MQkrOEaN3BVyXt9ag')

# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")

# Функция для очистки текста статьи в Wikipedia и ограничения его 1000 символами
def getwiki(s):
    try:
        ny = wikipedia.page(s)  # Получаем страницу по запросу
        # Получаем первую тысячу символов
        wikitext = ny.content[:1000]
        # Разделяем по точкам
        wikimas = wikitext.split('.')
        # Отбрасываем все после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, исключая заголовки
        for x in wikimas:
            if not ('==' in x):
                if len((x.strip())) > 3:
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        # Убираем разметку при помощи регулярных выражений
        wikitext2 = re.sub(r'\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub(r'\{[^\{\}]*\}', '', wikitext2)
        return wikitext2, ny.images  # Возвращаем текст и список изображений
    except Exception as e:
        return 'В энциклопедии нет информации об этом', []

# Функция для получения подписи к изображению
def get_image_caption(image_url):
    try:
        # Википедия возвращает URL с расширением (например .jpg). Получим подпись через API
        params = {
            'action': 'query',
            'prop': 'imageinfo',
            'iiprop': 'extmetadata',
            'format': 'json',
            'titles': 'File:' + image_url.split('/')[-1]
        }
        response = requests.get('https://ru.wikipedia.org/w/api.php', params=params)
        data = response.json()

        # Получаем подпись из метаданных
        pages = data['query']['pages']
        for page in pages.values():
            if 'imageinfo' in page:
                extmetadata = page['imageinfo'][0]['extmetadata']
                if 'ImageDescription' in extmetadata:
                    return extmetadata['ImageDescription']['value']
        return None  # Если подписи нет
    except Exception as e:
        return None

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Отправьте мне любое слово, и я найду его значение на Wikipedia')

# Получение сообщений от пользователя
@bot.message_handler(content_types=["text"])
def handle_text(message):
    result, images = getwiki(message.text)  # Получаем текст и изображения
    bot.send_message(message.chat.id, result)  # Отправляем текст
    
    # Проверяем наличие изображений и отправляем первое фото с подписью
    if images:
        first_image = images[0]  # Берем первое изображение
        try:
            caption = get_image_caption(first_image)  # Получаем подпись
            if caption:
                bot.send_photo(message.chat.id, first_image, caption=caption)  # Отправляем фото с подписью
            else:
                bot.send_photo(message.chat.id, first_image, caption="Изображение с Wikipedia")  # Без подписи
        except Exception as e:
            print("Ошибка при отправке изображения:", e)
            bot.send_message(message.chat.id, "Не удалось загрузить изображение.")
    else:
        print("Изображений нет для данного запроса.")  # Лог для отладки

# Запускаем бота
bot.polling(none_stop=True, interval=0)
