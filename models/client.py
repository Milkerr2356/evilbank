
from client_database import ClientDatabase
import sqlite3
import json
from datetime import datetime


conn = sqlite3.connect("bank.db")

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
        next_number = 1
    return f"BY00UNBS{next_number:012d}"

def generate_user_id():
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id FROM users
                       WHERE user_id 'BY00UNBS%'
                       ORDER BY user_if DESC LIMIT 1""")
    result = cursor.fetchone()
    if result:
        last_schet = result[0]
        number = int(last_schet[-12:])
        new_schet = number + 1
    else:
        next_number = 1
    return f"BY00UNBS{next_number:012d}"


def registration():
    name = input("Введите имя:")
    surname = input('Введите фамилию')
    telephone_number = input("Введите телефон:")
    date_birthday = input("Ведите дату рождения (в формате ДД-ММ-ГГГГ):")


def register_client(conn):
    name = input("Введите имя: ")
    surname = input("Введите фамилию: ")
    phone = input("Введите номер телефона: ")
    birthday = input("Введите дату рождения (ГГГГ-ММ-ДД): ")

    date_now = datetime.now().strftime("%Y-%m-%d")
    number_of_schet = generate_new_schet(conn)
    user_id = generate_user_id(name, conn)

    client = Client(
        name=name,
        surname=surname,
        telephone_number=phone,
        date_birthday=birthday,
        date_s_client=date_now,
        number_of_schet=number_of_schet,
        user_id=user_id,
        have_byn=0.0,
        have_usd=0.0,
        have_rub=0.0
    )

    # Добавляем в БД
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (
            user_id, name, surname, telephone_number, date_birthday,
            date_s_client, number_of_schet, have_byn, have_usd, have_rub
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client.user_id,
        client.name,
        client.surname,
        client.telephone_number,
        client.date_birthday,
        client.date_s_client,
        client.number_of_schet,
        client.have_byn,
        client.have_usd,
        client.have_rub
    ))
    conn.commit()

    print(f"\nРегистрация завершена!\nВаш user_id: {client.user_id}\nВаш счёт: {client.number_of_schet}")
    return client


def login_client():
    cursor = conn.cursor()
    input_user_id = input("Введите юзер айди:")
    cursor.execute("SELECT input_user_id FROM users")




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
        self.applicatios = applications if applications else []
        self.messages = messages if messages else []

    def check_balance(self):
        want_currency = input('Выберите желаемую валюту -- BYN, RUB, USD: ').lower()
        if want_currency in ("byn", "бун", "бел. руб.", "белорусский рубль"):
            print(self.have_byn)
        elif want_currency in ("rub", "руб", "рус. руб.", "русский рубль", "российский рубль"):
            print(self.have_rub)
        elif want_currency in ("юсд", "usd", "долар", "доллар"):
            print(self.have_usd)
        else:
            print("У нас и у вас нет такой валюты на счету :(")

    def get_user_id(self):
        print(f"Ваш ID пользователя: {self.user_id}")

    def get_numer_of_schet(self):
        print(f"Ваш номер счета: {self.number_of_schet}")

    def get_history_of_operations(self):
        print("Ваш список операций:")
        for op in self.history_of_operations:
            print(f"- {op}")

    def send_money(self, conn):
        cursor = conn.cursor()

        send_user_id = input("Введите ID получателя: ")
        currency = input("Выберите валюту перевода (BYN / RUB / USD): ").lower()
        try:
            amount = float(input("Введите сумму перевода: "))
        except ValueError:
            print("Неверное число")
            return

        # Комиссии
        commission = {
            "byn": 1.0,
            "rub": 25.0,
            "usd": 1.5
        }

        if currency not in commission:
            print("Неверная валюта.")
            return

        total_amount = amount + commission[currency]

        # Проверка баланса
        if currency == "byn" and self.have_byn < total_amount:
            print("Недостаточно средств.")
            return
        if currency == "rub" and self.have_rub < total_amount:
            print("Недостаточно средств.")
            return
        if currency == "usd" and self.have_usd < total_amount:
            print("Недостаточно средств.")
            return

        # Поиск получателя
        cursor.execute("SELECT have_byn, have_usd, have_rub FROM users WHERE user_id = ?", (send_user_id,))
        result = cursor.fetchone()
        if not result:
            print("Получатель не найден.")
            return

        # Списание у отправителя
        if currency == "byn":
            self.have_byn -= total_amount
            cursor.execute("UPDATE users SET have_byn = ? WHERE user_id = ?", (self.have_byn, self.user_id))
        elif currency == "rub":
            self.have_rub -= total_amount
            cursor.execute("UPDATE users SET have_rub = ? WHERE user_id = ?", (self.have_rub, self.user_id))
        elif currency == "usd":
            self.have_usd -= total_amount
            cursor.execute("UPDATE users SET have_usd = ? WHERE user_id = ?", (self.have_usd, self.user_id))

        # Зачисление получателю
        if currency == "byn":
            new_value = result[0] + amount
            cursor.execute("UPDATE users SET have_byn = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "usd":
            new_value = result[1] + amount
            cursor.execute("UPDATE users SET have_usd = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "rub":
            new_value = result[2] + amount
            cursor.execute("UPDATE users SET have_rub = ? WHERE user_id = ?", (new_value, send_user_id))

        conn.commit()

        operation = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Отправлено {amount} {currency.upper()} пользователю {send_user_id} (комиссия {commission[currency]})"
        self.history_of_operations.append(operation)

        print("Перевод выполнен успешно.")
