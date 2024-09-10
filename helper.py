import webbrowser
import string
import datetime
import random
import speech_recognition as sr
import pyttsx3
import requests
import json
import tkinter as tk
from threading import Thread, Event


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Я слушаю")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, language="ru-RU")
            return command.lower()
        except sr.UnknownValueError:
            speak("Извините, я не понял.")
            return ""
        except sr.RequestError:
            speak("Ошибка сервиса распознавания.")
            return ""


def get_external_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        ip_data = response.json()
        return ip_data["ip"]
    except requests.RequestException as e:
        print(f"Ошибка получения IP: {e}")
        return "Не удалось определить IP"


def send_request_data(query, ip_address):
    server_url = "http://10.10.0.253:5000/receive_request"
    data = {
        "query": query,
        "ip_address": ip_address
    }
    try:
        response = requests.post(server_url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)


def search_internet(query):
    ip_address = get_external_ip()
    send_request_data(query, ip_address)
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)


def get_current_time():
    return datetime.datetime.now().strftime("%H:%M")


def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def tell_joke():
    try:
        url = "https://api.chucknorris.io/jokes/random"
        response = requests.get(url)
        response.raise_for_status()
        joke_data = response.json()
        return joke_data["value"]
    except requests.RequestException as e:
        return f"Ошибка соединения: {e}"
    except json.JSONDecodeError:
        return "Ошибка при обработке данных."


def tell_fact():
    try:
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        response = requests.get(url)
        response.raise_for_status()
        fact_data = response.json()
        return fact_data["text"]
    except requests.RequestException as e:
        return f"Ошибка соединения: {e}"
    except json.JSONDecodeError:
        return "Ошибка при обработке данных."


def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def process_command(command):
    if "привет" in command:
        speak("Привет! Как я могу помочь?")
    elif "поиск" in command:
        speak("Что вы хотите найти?")
        query = listen()
        search_internet(query)
    elif "время" in command:
        current_time = get_current_time()
        speak(f"Сейчас {current_time}")
    elif "дата" in command:
        current_date = get_current_date()
        speak(f"Сегодня {current_date}")
    elif "анекдот" in command:
        joke = tell_joke()
        speak(joke)
    elif "факт" in command:
        fact = tell_fact()
        speak(fact)
    elif "генерация пароля" in command:
        speak("Какой длины должен быть пароль?")
        length = listen()
        try:
            length = int(length)
            password = generate_password(length)
            speak(f"Ваш пароль: {password}")
        except ValueError:
            speak("Пожалуйста, введите число.")
    elif "стоп" in command:
        speak("Останавливаю программу.")
        stop_event.set()  # Устанавливаем событие остановки
        root.quit()  # Закрываем окно


def on_close():
    stop_event.set()  # Устанавливаем событие остановки при закрытии окна
    root.quit()  # Закрываем окно


def show_commands(stop_event):
    commands = {
        "привет": "Запустите приветствие.",
        "поиск": "Начните поиск в интернете.",
        "время": "Получите текущее время.",
        "дата": "Получите текущую дату.",
        "анекдот": "Узнайте случайный анекдот.",
        "факт": "Узнайте случайный интересный факт.",
        "генерация пароля": "Сгенерируйте случайный пароль.",
        "стоп": "Остановите программу."
    }

    global root
    root = tk.Tk()
    root.title("Доступные команды")
    root.protocol("WM_DELETE_WINDOW", on_close)  # Обработка закрытия окна

    text = tk.Text(root, height=15, width=50)
    for command, description in commands.items():
        text.insert(tk.END, f"{command}: {description}\n")
    text.pack()

    button = tk.Button(root, text="Закрыть", command=on_close)
    button.pack()

    while not stop_event.is_set():
        root.update_idletasks()
        root.update()


def main():
    global stop_event
    stop_event = Event()

    # Запускаем окно команд в отдельном потоке
    commands_thread = Thread(target=show_commands, args=(stop_event,))
    commands_thread.start()

    while not stop_event.is_set():
        command = listen()
        if command:
            process_command(command)

    commands_thread.join()  # Ожидаем завершения потока с GUI


if __name__ == "__main__":
    main()
