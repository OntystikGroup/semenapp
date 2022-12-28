import torch
from telebot import TeleBot
from telebot.types import Message
from config import token
import logging
from packed_image_editor import make_baw
import datetime
from tools import predict

now_time = datetime.datetime.now().date()
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')

bot = TeleBot(token)
logger.info('Got bot token')
model = torch.hub.load('.', 'custom', path='model/best.pt', source='local')


@bot.message_handler(commands=['start'])
def start(message: Message):
    logger.info('Got start command')
    bot.send_message(message.chat.id,
                     text='This bot provides online calculator for determining Sperm DNA fragmentation '
                          'using images and videos obtained from Sperm Chromatin Dispersion (SCD) Test.'
                          ' You just have to upload the images/videous to obtain the results of the'
                          ' test. AI is configured to images/videos obtained from 400x microscope'
                          ' magnification. \n\n\n\nЭтот бот способен высчитывать индекс фрагментации ДНК'
                          ' сперматозоидов, используя фотографии или видеоматериалы, полученные с помощью'
                          ' теста на дисперсию хроматина сперматозоидов (SCD test). Для получения результата'
                          ' вам достаточно загрузить фотографии/видеоматериалы полученных препаратов. ИИ бота '
                          'предназначен только для анализа изображений/видеоматериалов, полученных с микроскопа '
                          'с увеличением х400.'
                          '\n\n\n\nКонтакты для связи:'
                          '\n\nMagauiya Alikhan - orda.ezhenid@gmail.com '
                          '\n\nZhumadil Kh.'
                          '\n\nSarsen Sherkhan - sherkhan.sarsen@gmail.com'
                          '\n\nDarbayev Nurdaulet - darbayevn@gmail.com'
                     )


@bot.message_handler(content_types=['photo'])
def download_photo(message):
    try:
        logger.info('Got photo from user')

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        logger.info('Photo downloaded')
        dtype = str(file_info).split('.')[-1][:-2]
        src = 'input_images/input.' + dtype
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        logger.info('Photo read')

        bot.reply_to(message, "Wait please, uploading ...")
        make_baw(input_path=src)
        output_text, percent = predict(input_model=model, img_path='baw_images/ready.jpeg')

        logger.info('Photo converted to BaW')

        with open('output_images/ready.jpg', 'rb') as output_img:
            bot.send_photo(message.chat.id, output_img)
            bot.send_message(message.chat.id, output_text)
            bot.send_message(message.chat.id, f'Percent fragmentation {round(percent * 100, 2)}%')

        logger.info('Prediction completed')
    except Exception as e:
        logger.error('Appeared error: %s', str(e))
        bot.reply_to(message, 'Appeared errors, try another photo, please')


bot.polling()
