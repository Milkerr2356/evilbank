# main.py

from client import Client
from client_database import ClientDatabase

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
