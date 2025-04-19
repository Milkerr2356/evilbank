# main.py

from client
from client_db import ClientDatabase
from meneger import Meneger

from models.client import login_client, register_client

if __name__ == "__main__":
    db = ClientDatabase()

    client1 = Client(
        name="Алиса",
        surname="Сидорова",
        date_birthday="1998-04-15",
        date_s_client="2023-10-01",
        number_of_schet="BY00UNBS00000000000000000001",
        user_id="user_alice_001",
        have_byn=2500.0,
        have_usd=150.0,
        have_rub=7000.0,
        history_of_operations=["Открытие счета", "Пополнение на 2500 BYN"],
        applications=["Заявка на дебетовую карту"],
        messages=["Ваш счёт успешно создан."]
    )

    db.save_client(client1)


while True:
    print("ДОБРО ПОЖАЛОВАТЬ ! \n Вас приветстувает Universal Banking eXpress \n")
    print("Выберите действие: \n 1. ВХОД \n 2.РЕГИСТРАЦИЯ")
    result_log_reg = int(input("\t"))
    if result_log_reg == 1:
        if login_client() != None:
            print("Выберите действие: ")
            print("1. Проверить баланс \n 2.Посмотреть user_id \n 3.Посмотреть номер счета \n 4/")


    if result_log_reg == 2:
        register_client()