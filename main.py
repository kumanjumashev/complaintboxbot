import telebot
from datetime import datetime, timedelta
import csv

botapi = "YOURTELEGRAMBOTAPIKEY"

bot = telebot.TeleBot(botapi, parse_mode=None)

user_states = {}
complaints_file = "complaints.txt"
timestamps_file = "user_timestamps.txt"
filter_words_file = 'English.csv'

with open(filter_words_file, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    filter_words = [word.strip().lower() for row in reader for word in row]

def can_submit_complaint(user_id):
    try:
        with open(timestamps_file, "r", encoding='utf-8') as timestamp_file:
            timestamps = timestamp_file.readlines()
            timestamps = [line.strip().split(",") for line in timestamps]
            user_timestamp = next((ts[1] for ts in timestamps if ts[0] == str(user_id)), None)
            if user_timestamp:
                last_complaint_time = datetime.strptime(user_timestamp, "%Y-%m-%d %H:%M:%S")
                return datetime.now() - last_complaint_time >= timedelta(weeks=1)
    except FileNotFoundError:
        pass

    return True

def update_timestamp(user_id):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(timestamps_file, "a", encoding='utf-8') as timestamp_file:
        timestamp_file.write(f"{user_id},{current_time}\n")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_complaint'
    
    terms_of_use = (
        "Welcome to the Chyngyz Aytmatov Lyceum's Complaint Box Bot!\n\n"
        "This bot allows you to submit complaints. Please read the following terms of use:\n\n"
        "1. Don't use inappropriate language: Ensure your messages are respectful.\n"
        "2. Only 1 message per week: Limit your submissions to one per week.\n"
        "3. No unreasonable complaints: Ensure your complaints are valid and reasonable.\n\n"
        "To submit a complaint, use the /complaint command."
    )
    
    bot.reply_to(message, terms_of_use)

@bot.message_handler(commands=['complaint'])
def command(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_complaint'
    
    if can_submit_complaint(user_id):
        bot.reply_to(message, "Ready to receive your complaint!")
    else:
        bot.reply_to(message, "You can only submit one complaint per week.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_complaint')
def complaint(message):
    user_id = message.from_user.id
    text = message.text.lower()

    if any(word in text for word in filter_words):
        bot.reply_to(message, "Please refrain from using inappropriate language.")
    elif can_submit_complaint(user_id):
        bot.reply_to(message, "Complaint received!")
        with open(complaints_file, "a", encoding='utf-8') as file:
            file.write(text + "\n")
        update_timestamp(user_id)
    else:
        bot.reply_to(message, "You can only submit one complaint per week.")

    user_states[user_id] = None

bot.polling()
