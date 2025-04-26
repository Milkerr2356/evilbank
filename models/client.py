import sqlite3
import json
import hashlib
import time

import requests #pip
from datetime import datetime
import uuid

from tqdm import tqdm#

DB_NAME = "bank.db"
conn = sqlite3.connect(DB_NAME)

# === Хелперы ===


def generate_new_schet(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT number_of_schet FROM clients
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


def generate_user_id(conn, name):
    name = name.lower()
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id FROM clients
                      WHERE user_id LIKE ? 
                      ORDER BY user_id DESC LIMIT 1""", (f"user_{name}_%",))
    result = cursor.fetchone()
    if result:
        last_id = result[0]
        try:
            number = int(last_id.split("_")[-1]) + 1
        except ValueError:
            number = 1
    else:
        number = 1
    return f"user_{name}_{number:03d}"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_exchange_rates():
    for i in tqdm(range(100), ncols=100, leave=False, desc="\033[36mОтправква запроса на сервер..."):  # Циан
        time.sleep(0.04)

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
    def __init__(self, name, surname, telephone_number,password, date_birthday, date_s_client, number_of_schet, user_id,
                 history_of_operations=None, applications=None, have_byn=0.0, have_usd=0.0, have_rub=0.0,have_eur=0.0, messages=None, is_manager=False):
        self.name = name
        self.surname = surname
        self.telephone_number = telephone_number
        self.password = hash_password(password)
        self.date_birthday = date_birthday
        self.date_s_client = date_s_client
        self.number_of_schet = number_of_schet
        self.user_id = user_id
        self.have_byn = have_byn
        self.have_rub = have_rub
        self.have_usd = have_usd
        self.have_eur = have_eur
        self.history_of_operations = history_of_operations if history_of_operations else []
        self.applications = applications if applications else []
        self.messages = messages if messages else []
        self.is_manager = is_manager


    def check_balance(self):
        want_currency = input('Выберите валюту (BYN, RUB, USD, EUR): ').lower()
        if want_currency == "byn":
            time.sleep(0.05)
            print(self.have_byn)
        elif want_currency == "rub":
            time.sleep(0.05)
            print(self.have_rub)
        elif want_currency == "usd":
            time.sleep(0.05)
            print(self.have_usd)
        elif want_currency == "eur":
            time.sleep(0.05)
            print(self.have_eur)
        else:
            print("Неверная валюта")

    @staticmethod
    def generate_console_receipt(sender_name, receiver_name, amount, user_id, operation, currency="BYN"):
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        transaction_id = uuid.uuid4().hex[:8]  # Генерируем уникальный номер транзакции

        line = "=" * 42
        currency_symbols = {
            "BYN": "Br",
            "USD": "$",
            "EUR": "€",
            "RUB": "₽",
            "PLN": "zł"
        }
        symbol = currency_symbols.get(currency.upper(), currency)  # Если валюты нет — пишем как есть

        time.sleep(0.03)
        receipt = f"""
    {line}
                \033[32mUNIVERSAL BANKING EXPRESS \033[0m
    {line}
    Дата и время      : {now}
    Операция          : {operation}
    Номер транзакции  : {transaction_id}
    ID пользователя   : {user_id}
    {line}
    Отправитель       : {sender_name}
    Получатель        : {receiver_name}
    Сумма             : {amount:.2f} {symbol}
    {line}
             \033[32mСпасибо за использование UBX! \033[0m
    {line}
    """
        print(receipt)



    def is_manager(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT is_manager FROM clients WHERE user_id = ?", (self.user_id,))
        result = cursor.fetchone()
        return result and result[0] == 1

    def send_money(self):
        cursor = conn.cursor()
        send_user_id = input("Введите ID получателя: ")
        currency = input("Выберите валюту перевода (BYN / RUB / USD / EUR): ").lower()

        try:
            amount = float(input("Введите сумму перевода: "))
        except ValueError:
            print("\033[31mНеверное число \033[0m")
            return

        commission = {
            "byn": 1.0,
            "rub": 25.0,
            "usd": 1.5,
            "eur": 1.2
        }

        if currency not in commission:
            print("\033[31mНеверная валюта. \033[0m")
            return

        total_amount = amount + commission[currency]

        # Проверка средств
        if currency == "byn" and self.have_byn < total_amount:
            print("\033[31mНедостаточно средств. \033[0m")
            return
        if currency == "rub" and self.have_rub < total_amount:
            print("\033[31mНедостаточно средств. \033[0m")
            return
        if currency == "usd" and self.have_usd < total_amount:
            print("\033[31mНедостаточно средств. \033[0m")
            return
        if currency == "eur" and self.have_eur < total_amount:
            print("\033[31mНедостаточно средств. \033[0m")
            return

        cursor.execute("SELECT have_byn, have_usd, have_rub, have_eur FROM clients WHERE user_id = ?", (send_user_id,))
        result = cursor.fetchone()
        if not result:
            print("\033[31mПолучатель не найден. \033[0m")
            return

        # Списание и начисление
        if currency == "byn":
            self.have_byn -= total_amount
            cursor.execute("UPDATE clients SET have_byn = ? WHERE user_id = ?", (self.have_byn, self.user_id))
            new_value = result[0] + amount
            cursor.execute("UPDATE clients SET have_byn = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "usd":
            self.have_usd -= total_amount
            cursor.execute("UPDATE clients SET have_usd = ? WHERE user_id = ?", (self.have_usd, self.user_id))
            new_value = result[1] + amount
            cursor.execute("UPDATE clients SET have_usd = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "rub":
            self.have_rub -= total_amount
            cursor.execute("UPDATE clients SET have_rub = ? WHERE user_id = ?", (self.have_rub, self.user_id))
            new_value = result[2] + amount
            cursor.execute("UPDATE clients SET have_rub = ? WHERE user_id = ?", (new_value, send_user_id))
        elif currency == "eur":
            self.have_eur -= total_amount
            cursor.execute("UPDATE clients SET have_eur = ? WHERE user_id = ?", (self.have_eur, self.user_id))
            new_value = result[3] + amount
            cursor.execute("UPDATE clients SET have_eur = ? WHERE user_id = ?", (new_value, send_user_id))

        conn.commit()
        operation = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Отправлено {amount} {currency.upper()} пользователю {send_user_id} (комиссия {commission[currency]})"
        self.history_of_operations.append(operation)

        for i in tqdm(range(100), ncols=100, leave=False, desc="\033[36mОбработка транзакции..."):
            time.sleep(0.04)

        print("\033[32mПеревод выполнен успешно. \033[0m")
        time.sleep(0.04)

        receiver_name = send_user_id
        sender_name = self.name
        user_id = self.user_id
        self.generate_console_receipt(sender_name, receiver_name, amount, user_id, "Перевод пользователю", currency)



    def transit_money(self):
        cursor = conn.cursor()
        category = ""
        print("Выберите категорию перевода: \n1.Kover marketplace ")
        want_kategory = int(input("\t"))
        if want_kategory == 1:
            user_name_m = input("введите id пользователя на маркетплэйсе \n \t")
            try:
                amount = float(input("Введите сумму перевода: "))
            except ValueError:
                print("\033[31mНеверное число \033[0m")
                return
            total = amount * 0.95
            if self.have_byn < total:
                print("\033[31mНедостаточно средств на счету. \033[0m")
                return
            else:
                self.have_byn -= amount * 0.95
                cursor.execute("UPDATE clients SET have_byn = ? WHERE user_id = ?", (self.have_byn, self.user_id))
                conn.commit()
                for i in tqdm(range(100), ncols=100, leave=False, desc="\033[36mОбработка транзакции..."):  # Циан
                    time.sleep(0.042)
                time.sleep(0.1)
                print("\033[32mПеревод выполнен успешно. \033[0m")
                print("\033[33mКешбэк 5% \033[0m")
                reciver_name = "Маркетплэйс"

        else:
            print("\033[31mДанной категории не существует \033[0m")
        target = want_kategory
        # Генерация чека
        receiver_name = target
        sender_name = self.name
        user_id = self.user_id
        operation = "Перевод в Kover marcetplace"
        currency = "BYN"
        amount = total
        self.generate_console_receipt(sender_name, receiver_name, amount, user_id, operation, currency)
        time.sleep(3)


    def get_user_id(self):
        print(f"\033[37mВаш ID пользователя: {self.user_id} \033[0m")

    def get_numer_of_schet(self):
        print(f"\033[37mВаш номер счета: {self.number_of_schet} \033[0m")

    def get_history_of_operations(self):
        time.sleep(0.02)
        print("Ваш список операций:")
        for op in self.history_of_operations:
            print(f"- {op}")

    def get_applications(self):
        time.sleep(0.022)
        print("Ваши сообщения :")
        for msg in self.messages:
            print(f"- {msg}")


    def send_message_to_manager(self,sender:"Client"):
        cursor = conn.cursor()

        #Выводим список менеджеров
        cursor.execute("SELECT user_id, name, surname FROM clients WHERE is_manager = 1")
        managers = cursor.fetchall()

        if not managers:
            print("\033[31mМенеджеры не найдены. \033[0m")
            return

        print("Список менеджеров:")
        for manager in managers:
            print(f"ID: {manager[0]} | Имя: {manager[1]} {manager[2]}")

        #Ввод ID менеджера
        selected_id = input("\nВведите ID менеджера, которому хотите отправить сообщение: ")

        #Проверяем существует ли такой менеджер
        cursor.execute("SELECT messages FROM clients WHERE user_id = ? AND is_manager = 1", (selected_id,))
        result = cursor.fetchone()

        if result:
            messages_json = result[0]
            messages = json.loads(messages_json) if messages_json else []

            #Ввод текста сообщения
            msg_text = input("Введите сообщение для менеджера: ")

            full_message = f"{msg_text} (от пользователя {sender.user_id})"
            messages.append(full_message)

            #Обновляем сообщения менеджера
            cursor.execute("UPDATE clients SET messages = ? WHERE user_id = ?", (json.dumps(messages), selected_id))
            conn.commit()
            print("\033[32mСообщение успешно отправлено! \033[0m")
        else:
            print("\033[31mМенеджер не найден. \033[0m")



# === Регистрация и вход ===
def register_client(conn):
    reg_meneger_codes = ("cHCp4", "1QWERTYUu", "t")
    name = input("Введите имя: ")
    surname = input("Введите фамилию: ")
    phone = input("Введите номер телефона: ")
    birthday = input("Введите дату рождения (ГГГГ-ММ-ДД): ")
    password = input("Придумайте пароль: ")
    is_manager_input = input("Вы регистрируетесь как менеджер? (да/нет): ").strip().lower()
    is_manager = False

    if is_manager_input == "да":
        reg_code = input("Введите код регистрации менеджера: ").strip()
        if reg_code in reg_meneger_codes:
            is_manager = True
            print("Код подтверждён. Регистрируем как менеджера.")
        else:
            print("\033[31mНеверный код. Регистрация будет продолжена как обычный клиент. \033[0m")
    date_now = datetime.now().strftime("%Y-%m-%d")
    number_of_schet = generate_new_schet(conn)
    user_id = generate_user_id(conn,name)
    hashed_password = hash_password(password)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (
            user_id, name, surname, telephone_number, date_birthday,
            date_s_client, number_of_schet, have_byn, have_usd, have_rub,have_eur,
            password, is_manager
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (
        user_id, name, surname, phone, birthday,
        date_now, number_of_schet, 0.0, 0.0, 0.0,0.0,
        hashed_password, int(is_manager)
    ))
    conn.commit()
    print(f"\033[32m\nРегистрация завершена!\n\033[37mВаш user_id: {user_id}\nВаш счёт: {number_of_schet} \033[0m")



def login_client(conn):
    user_id = input("Введите user_id: ")
    password = input("Введите пароль: ")
    hashed_password = hash_password(password)

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE user_id = ? AND password = ?", (user_id, hashed_password))
    user_data = cursor.fetchone()
    if not user_data:
        print("\033[31mНеверный логин или пароль. \033[0m")
        return None
    print("\033[32mУспешный вход. \n \033[0m")
    return user_data

