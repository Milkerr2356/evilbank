import sqlite3
import time
from datetime import datetime
from tqdm import tqdm#
import requests
# Функция для подключения к базе данных
DB_NAME = "bank.db"
conn = sqlite3.connect(DB_NAME)


# Метод для депозита на счет клиента
def deposit(conn):
    cursor = conn.cursor()

    # Запрашиваем ID клиента
    user_id = input("Введите ID клиента: ")

    # Запрашиваем валюту депозита
    currency = input("Введите валюту депозита  BYN / USD / RUB / EUR: ").lower()
    if currency not in ["byn", "usd", "rub"]:
        print("Неверная валюта.")
        return

    try:
        # Запрашиваем сумму депозита
        amount = float(input(f"Введите сумму для депозита в {currency.upper()}: "))
    except ValueError:
        print("Неверное значение суммы.")
        return

    if amount <= 0:
        print("Сумма депозита должна быть положительной.")
        return

    # Проверка на существование клиента в базе данных
    cursor.execute("SELECT have_byn, have_usd, have_rub,have_eur FROM clients WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    for i in tqdm(range(100), ncols=100, leave=False, desc="\033[36mОбработка транзакции..."):  # Циан
        time.sleep(0.04)
    if result:
        # Обновляем счет клиента в базе данных в зависимости от валюты
        if currency == "byn":
            new_balance = result[0] + amount
            cursor.execute("UPDATE clients SET have_byn = ? WHERE user_id = ?", (new_balance, user_id))
        elif currency == "usd":
            new_balance = result[1] + amount
            cursor.execute("UPDATE clients SET have_usd = ? WHERE user_id = ?", (new_balance, user_id))
        elif currency == "rub":
            new_balance = result[2] + amount
            cursor.execute("UPDATE clients SET have_rub = ? WHERE user_id = ?", (new_balance, user_id))
        elif currency == "eur":
            new_balance = result[2] + amount
            cursor.execute("UPDATE clients SET have_eur = ? WHERE user_id = ?", (new_balance, user_id))

        conn.commit()

        # Логирование операции
        operation = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Депозит {amount} {currency.upper()} на счет клиента {user_id}"
        print(f"Операция успешна. Сумма {amount} {currency.upper()} была зачислена на счет клиента с ID {user_id}.")
    else:
        print(f"Клиент с ID {user_id} не найден.")


# Метод для снятия средств с аккаунта клиента
def withdraw_money(conn):
    cursor = conn.cursor()

    # Запрашиваем ID клиента
    user_id = input("Введите ID клиента: ")

    # Запрашиваем валюту для снятия
    currency = input("Выберите валюту для снятия  BYN / USD / RUB / EUR: ").lower()

    # Запрашиваем сумму для снятия
    try:
        amount = float(input("Введите сумму для снятия: "))
    except ValueError:
        print("Неверное число.")
        return

    # Проверка на валидную валюту
    if currency not in ["byn", "usd", "rub","eur"]:
        print("Неверная валюта.")
        return

    # Проверка на наличие достаточно средств в базе данных
    cursor.execute(f"SELECT have_{currency}, name FROM clients WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        print("Клиент с таким ID не найден.")
        return

    # Получаем текущий баланс клиента по выбранной валюте
    current_balance = result[0]
    client_name = result[1]

    # Если средств недостаточно, выводим сообщение
    if current_balance < amount:
        print(f"У клиента {client_name} недостаточно средств на счете.")
        return

    # Если средств достаточно, производим снятие
    new_balance = current_balance - amount

    # Обновляем баланс клиента в базе данных
    for i in tqdm(range(100), ncols=100, leave=False, desc="\033[36mОбработка транзакции..."):  # Циан
        time.sleep(0.04)
    cursor.execute(f"UPDATE clients SET have_{currency} = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

    # Логирование операции
    operation = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Снятие {amount} {currency.upper()} с счета клиента {user_id}"
    print(f"Снятие {amount} {currency.upper()} с вашего счета завершено успешно.")




def get_exchange_rates():
    for _ in tqdm(range(100), ncols=100, leave=False, desc="\033[36mЗапрос курсов валют..."):
        time.sleep(0.01)
    url = "https://www.nbrb.by/api/exrates/rates?periodicity=0"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("\033[31mОшибка при получении курсов валют\033[0m")
            return None
        rates = response.json()
        exchange_rates = {}
        for rate in rates:
            if rate['Cur_Abbreviation'] in ['USD', 'EUR', 'RUB']:
                exchange_rates[rate['Cur_Abbreviation']] = rate['Cur_OfficialRate']
        return exchange_rates
    except Exception as e:
        print("\033[31mОшибка при обращении к API:\033[0m", e)
        return None

def show_exchange_rates():
    rates = get_exchange_rates()
    if not rates:
        return

    # Наценка банка при продаже валюты клиенту (покупка клиентом)
    sell_bonus = {
        "USD": 0.1,
        "EUR": 0.11,
        "RUB": 0.003
    }

    print("\n\033[36mКурсы обмена валют:\033[0m")
    print(f"{'Валюта':<10}{'Покупка (BYN → Валюта)':<30}{'Продажа (Валюта → BYN)':<30}")
    print("-" * 70)

    for currency, rate in rates.items():
        buy_rate = rate - sell_bonus[currency]  # Клиент покупает валюту дороже
        sell_rate = rate  # Клиент продаёт валюту дешевле
        print(f"{currency:<10}{buy_rate:<30.4f}{sell_rate:<30.4f}")

    print("-" * 70)
    time.sleep(3)



def exchange_currency(user_id):
    cursor = conn.cursor()

    rates = get_exchange_rates()
    if not rates:
        return

    print("\n\033[36mВарианты обмена:\033[0m")
    print("1. Купить USD за BYN")
    print("2. Продать USD за BYN")
    print("3. Купить EUR за BYN")
    print("4. Продать EUR за BYN")
    print("5. Купить RUB за BYN")
    print("6. Продать RUB за BYN")

    try:
        choice = int(input("\nВыберите вариант: "))
    except ValueError:
        print("\033[31mВведите число.\033[0m")
        return

    if choice not in range(1, 7):
        print("\033[31mНет такого варианта.\033[0m")
        return

    # Получаем текущие балансы
    cursor.execute("SELECT have_byn, have_usd, have_eur, have_rub FROM clients WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        print("\033[31mПользователь не найден.\033[0m")
        return

    have_byn, have_usd, have_eur, have_rub = result

    try:
        amount = float(input("Введите сумму для обмена: "))
    except ValueError:
        print("\033[31mНеверная сумма.\033[0m")
        return

    # Настройка курсов покупки
    sell_bonus = {
        "USD": 0.1,
        "EUR": 0.11,
        "RUB": 0.003
    }

    if choice == 1:  # Купить USD
        rate = rates["USD"] - sell_bonus["USD"]
        total_cost = amount * rate
        if have_byn < total_cost:
            print("\033[31mНедостаточно BYN.\033[0m")
            return
        have_byn -= total_cost
        have_usd += amount

    elif choice == 2:  # Продать USD
        rate = rates["USD"]
        if have_usd < amount:
            print("\033[31mНедостаточно USD.\033[0m")
            return
        have_usd -= amount
        have_byn += amount * rate

    elif choice == 3:  # Купить EUR
        rate = rates["EUR"] - sell_bonus["EUR"]
        total_cost = amount * rate
        if have_byn < total_cost:
            print("\033[31mНедостаточно BYN.\033[0m")
            return
        have_byn -= total_cost
        have_eur += amount

    elif choice == 4:  # Продать EUR
        rate = rates["EUR"]
        if have_eur < amount:
            print("\033[31mНедостаточно EUR.\033[0m")
            return
        have_eur -= amount
        have_byn += amount * rate

    elif choice == 5:  # Купить RUB
        rate = rates["RUB"] - sell_bonus["RUB"]
        total_cost = amount * rate
        if have_byn < total_cost:
            print("\033[31mНедостаточно BYN.\033[0m")
            return
        have_byn -= total_cost
        have_rub += amount

    elif choice == 6:  # Продать RUB
        rate = rates["RUB"]
        if have_rub < amount:
            print("\033[31mНедостаточно RUB.\033[0m")
            return
        have_rub -= amount
        have_byn += amount * rate

    # Сохраняем изменения
    cursor.execute("""
        UPDATE clients
        SET have_byn = ?, have_usd = ?, have_eur = ?, have_rub = ?
        WHERE user_id = ?
    """, (have_byn, have_usd, have_eur, have_rub, user_id))
    conn.commit()
    for _ in tqdm(range(100), ncols=100, leave=False, desc="\033[36mВыполняем обмен..."):
        time.sleep(0.1)

    print("\033[32mОбмен успешно выполнен!\033[0m")
    time.sleep(0.22)
    print(f"\n\033[36mВаши новые балансы:\033[0m\n"
          f"BYN: {have_byn:.2f}\n"
          f"USD: {have_usd:.2f}\n"
          f"EUR: {have_eur:.2f}\n"
          f"RUB: {have_rub:.2f}")
    time.sleep(2)


while True:
    print("""\033[34m

 _  _   _ ______  __
| | | | __ ) \\/ /
| | | | __ \\ \\ / 
| |_| | |_) /  \\ 
 \\___/|_____/\\/\\_\\            
                                  _  _____ __  __ 
                               / \\|_   _|  \\/  |
                              / _ \\ | | | |\\/| |
                             / ___ \\| | | |  | |
                            /_/   \\_\\_| |_|  |_|

\033[0m
        Добро пожаловать!
    """)
    print("Выберите действие  1) Снять валюту  2) Внести депозит по валюте  3)Просмотреть курс валют  4) Обменять валюту  5)Выход")
    do = int(input("\t"))
    if do == 1:
        withdraw_money(conn)
    elif do == 2:
        deposit(conn)
    elif do == 3:
        show_exchange_rates()
    elif do == 4:
        print("Введите свой user_id")
        user_id = input("\t")
        exchange_currency(user_id)
    elif do == 5:
        break
    else:
        print("Неверня команда")