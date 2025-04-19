import sqlite3
import json
import hashlib
import requests
from datetime import datetime

DB_NAME = "bank.db"
conn = sqlite3.connect(DB_NAME)

# === Хелперы ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_new_schet(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT number_of_schet FROM users
                      WHERE number_of_schet LIKE 'BY00UNBS%'
                      ORDER BY number_of_schet DESC LIMIT 1""")
    result = cursor.fetchone()
    if result:
        last_schet = result[0]
        number = int(last_schet[-12:])
        new_schet = number + 1
    else:
        new_schet = 1
    return f"BY00UNBS{new_schet:012d}"

def generate_user_id():
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id FROM users
                      WHERE user_id LIKE 'BY00UNBS%'
                      ORDER BY user_id DESC LIMIT 1""")
    result = cursor.fetchone()
    if result:
        last_id = result[0]
        number = int(last_id[-12:]) + 1
    else:
        number = 1
    return f"BY00UNBS{number:012d}"

def get_exchange_rates():
    url = "https://www.nbrb.by/api/exrates/rates?periodicity=0"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Ошибка при получении курсов валют")
            return
        rates = response.json()
        print("Курсы валют (по данным НБРБ):")
        for rate in rates:
            if rate['Cur_Abbreviation'] in ['USD', 'RUB', 'EUR']:
                print(f"{rate['Cur_Abbreviation']}: {rate['Cur_OfficialRate']} BYN")
    except Exception as e:
        print("Ошибка при обращении к API:", e)

# === Класс клиента ===
class Client:
    def __init__(self, name, surname, telephone_number, date_birthday, date_s_client, number_of_schet, user_id,
                 history_of_operations=None, applications=None, have_byn=0.0, have_usd=0.0, have_rub=0.0, messages=None):
        self.name = name
        self.surname = surname
        self.telephone_number = telephone_number
        self.date_birthday = date_birthday
        self.date_s_client = date_s_client
        self.number_of_schet = number_of_schet
        self.user_id = user_id
        self.have_byn = have_byn
        self.have_rub = have_rub
        self.have_usd = have_usd
        self.history_of_operations = history_of_operations if history_of_operations else []
        self.applications = applications if applications else []
        self.messages = messages if messages else []

    def check_balance(self):
        want_currency = input('Выберите валюту (BYN, RUB, USD): ').lower()
        if want_currency == "byn":
            print(self.have_byn)
        elif want_currency == "rub":
            print(self.have_rub)
        elif want_currency == "usd":
            print(self.have_usd)
        else:
            print("Неверная валюта")

    def is_manager(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT is_manager FROM users WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        return result and result[0] == 1

    def send_money(self, conn):
        cursor = conn.cursor()
        send_user_id = input("Введите ID получателя: ")
        currency = input("Выберите валюту перевода (BYN / RUB / USD): ").lower()
        try:
            amount = float(input("Введите сумму перевода: "))
        except ValueError:
            print("Неверное число")
            return

        commission = {"byn": 1.0, "rub": 25.0, "usd": 1.5}
        if currency not in commission:
            print("Неверная валюта.")
            return

        total_amount = amount + commission[currency]

        if currency == "byn" and self.have_byn < total_amount:
            print("Недостаточно средств.")
            return
        if currency == "rub" and self.have_rub < total_amount:
            print("Недостаточно средств.")
            return
        if currency == "usd" and self.have_usd < total_amount:
            print("Недостаточно средств.")
            return

        cursor.execute("SELECT have_byn, have_usd, have_rub FROM users WHERE user_id = ?", (send_user_id,))
        result = cursor.fetchone()
        if not result:
            print("Получатель не найден.")
            return

        if currency == "byn":
            self.have_byn -= total_amount
            cursor.execute("UPDATE users SET have_byn = ? WHERE user_id = ?", (self.have_byn, self.user_id))
            new_value = result[0] + amount
            cursor.execute("UPDATE users SET have_byn = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "rub":
            self.have_rub -= total_amount
            cursor.execute("UPDATE users SET have_rub = ? WHERE user_id = ?", (self.have_rub, self.user_id))
            new_value = result[2] + amount
            cursor.execute("UPDATE users SET have_rub = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "usd":
            self.have_usd -= total_amount
            cursor.execute("UPDATE users SET have_usd = ? WHERE user_id = ?", (self.have_usd, self.user_id))
            new_value = result[1] + amount
            cursor.execute("UPDATE users SET have_usd = ? WHERE user_id = ?", (new_value, send_user_id))

        conn.commit()
        operation = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Отправлено {amount} {currency.upper()} пользователю {send_user_id} (комиссия {commission[currency]})"
        self.history_of_operations.append(operation)
        print("Перевод выполнен успешно.")
    def get_user_id(self):
        print(f"Ваш ID пользователя: {self.user_id}")

    def get_numer_of_schet(self):
        print(f"Ваш номер счета: {self.number_of_schet}")

    def get_history_of_operations(self):
        print("Ваш список операций:")
        for op in self.history_of_operations:
            print(f"- {op}")

# === Регистрация и вход ===
def register_client(conn):
    name = input("Введите имя: ")
    surname = input("Введите фамилию: ")
    phone = input("Введите номер телефона: ")
    birthday = input("Введите дату рождения (ГГГГ-ММ-ДД): ")
    password = input("Придумайте пароль: ")
    is_manager = input("Вы регистрируетесь как менеджер? (да/нет): ").strip().lower() == "да"

    date_now = datetime.now().strftime("%Y-%m-%d")
    number_of_schet = generate_new_schet(conn)
    user_id = generate_user_id()
    hashed_password = hash_password(password)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (
            user_id, name, surname, telephone_number, date_birthday,
            date_s_client, number_of_schet, have_byn, have_usd, have_rub,
            password, is_manager
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, name, surname, phone, birthday,
        date_now, number_of_schet, 0.0, 0.0, 0.0,
        hashed_password, int(is_manager)
    ))
    conn.commit()
    print(f"\nРегистрация завершена!\nВаш user_id: {user_id}\nВаш счёт: {number_of_schet}")

def login_client(conn):
    user_id = input("Введите user_id: ")
    password = input("Введите пароль: ")
    hashed_password = hash_password(password)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ? AND password = ?", (user_id, hashed_password))
    user_data = cursor.fetchone()
    if not user_data:
        print("Неверный логин или пароль.")
        return None
    print("Успешный вход. \n")
    return user_data

