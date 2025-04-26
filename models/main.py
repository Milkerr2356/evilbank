# main.py

import time
from client import *
from client_db import ClientDatabase
from meneger import Meneger
from models.client import login_client, register_client
from tqdm import tqdm#


conn = sqlite3.connect(DB_NAME)

def create_client_from_db_row(row):
    return Client(
        user_id=row[0],
        name=row[1],
        surname=row[2],
        date_birthday=row[3],
        telephone_number=row[4],
        date_s_client=row[5],
        number_of_schet=row[6],
        have_byn=row[7],
        have_rub=row[8],
        have_usd=row[9],
        have_eur=row[10],  # ← если EUR будет 10-м
        history_of_operations=json.loads(row[11] or "[]"),
        applications=json.loads(row[12] or "[]"),
        messages=json.loads(row[13] or "[]"),
        password=row[14],
        is_manager=bool(row[15])
    )



if __name__ == "__main__":
    db = ClientDatabase()

    client1 = Client(
        name="Maxim",
        surname="Zhy",
        date_birthday="2010-12-29",
        date_s_client="2023-10-01",
        number_of_schet="BY00UNBS00000000000000000001",
        telephone_number=375259429876,
        password="qwerty",
        user_id="user_max_001",
        have_byn=2500.0,
        have_usd=150.0,
        have_rub=7000.0,
        history_of_operations=["Открытие счета", "Пополнение на 2500 BYN"],
        applications=["Заявка на дебетовую карту"],
        messages=["Ваш счёт успешно создан."]
    )

    db.save_client(client1)


while True:
    print("\033[34m ")
    print(""" 
 _   _ ______  __
| | | | __ ) \\/ /                       Финансы. Технологии. Уверенность.
| | | | __ \\ \\ / 
| |_| | |_) /  \\
 \\___/|____/_/\\_\\ 
        
    """)
    print("\033[0m ДОБРО ПОЖАЛОВАТЬ ! ")
    print("Выберите действие: \n 1. ВХОД \n 2.РЕГИСТРАЦИЯ  3. Выход")
    result_log_reg = input("\t")
    if result_log_reg in ["1", "2", "3"]:
        if result_log_reg == "1":
            user_data = login_client(conn)
            if user_data:

                password_input = input("Введите пароль: ")
                if hash_password(password_input) != user_data[14]:
                    print("Неверный пароль.")
                    continue

                if user_data[14] == 1:
                    print("Вход выполнен как менеджер.")

                    # Создаём объект менеджера
                    manager = Meneger(
                        name=user_data[1],
                        surname=user_data[2],
                        date_birthday=user_data[3],
                        date_s_meneger=user_data[5],
                        user_id=user_data[0],
                        applications=json.loads(user_data[11]) if user_data[11] else [],
                        zp_in_byn=user_data[7],
                        messages=json.loads(user_data[12]) if user_data[12] else []
                    )
                    while True:
                        print("\nВыберите действие: ")
                        print("1. Просмотреть входящие сообщения")
                        print("2. Отправить сообщение клиенту")
                        print("3.break")
                        result_meneger = int(input("\t"))

                        if result_meneger == 1:
                            manager.chek_messages(manager.user_id, conn)
                        elif result_meneger == 2:
                            manager.send_application(conn)
                        elif result_meneger == 3:
                            break
                        else:
                            print("Неверный выбор!")
                else:
                    client = create_client_from_db_row(user_data)
                    while True:
                        print("Выберите действие: ")
                        print("\n 1. Проверить баланс \n 2.Посмотреть user_id \n 3.Посмотреть номер счета \n 4.Просмотреть список операций \n 5.написать в тех поддердержку \n 6.Просмотреть список сообщений \n 7.Отправить перевод \n 8. Перевести деньги \n 9. Просмотреть курс валют НБРБ \n 10. Выход\n " )
                        reesult_do = int(input("\t"))
                        if reesult_do == 1:
                            client.check_balance()
                            continue
                            print("\n \n")

                        elif reesult_do == 2:
                            client.get_user_id()
                            print("\n \n")

                        elif reesult_do == 3:
                            client.get_numer_of_schet()
                            print("\n \n")

                        elif reesult_do == 4:
                            client.get_history_of_operations()
                            print("\n \n")

                        elif reesult_do == 5:
                            client.send_message_to_manager(client)
                            print("\n \n")

                        elif reesult_do == 6:
                            client.get_applications()
                            print("\n \n")

                        elif reesult_do == 7:
                            client.send_money()
                            print("\n \n")

                        elif reesult_do == 8:
                            client.transit_money()
                            print("\n \n")


                        elif reesult_do == 9:
                            get_exchange_rates()
                            print("\n \n")

                        elif reesult_do == 10:
                            break

                        else:
                            print("Неверный выбор!")
                            print("\n \n")


        if result_log_reg == "2":

            register_client(conn)
            print("\n \n")

            continue
        if result_log_reg == "3":
            break
        else:
            print("Невреная команда!!! ")
            print("\n \n")

    elif result_log_reg == "Easter":
            print("\nХристс воскресе!")
    elif result_log_reg == "New_Year":
        print("С Новым годом!!")
    else:
        print("Неверная команда!!")
        print("\n \n")