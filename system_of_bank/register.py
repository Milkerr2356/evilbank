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


def register_client(conn, clients_dict):
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