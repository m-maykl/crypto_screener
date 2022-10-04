import telebot
import time
import pandas as pd
bot = telebot.TeleBot('')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "Working..")
    while True:
        with open('info.csv') as f:
            info_csv = {k: v.strip() for k, v in (line.split(':') for line in f)}
            change = info_csv.get('change')
            key = info_csv.get('key')
        if key == 'read':
            bot.send_message(message.from_user.id, change)
            info_csv.update({'key': 'write'})
            pd.Series(info_csv).to_csv('info.csv', index=True, header=False, sep=':')


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)
