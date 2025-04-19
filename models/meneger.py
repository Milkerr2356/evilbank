# Основные классы и функции менеджера
import json

from glances.globals import json_dumps

import client
import sqlite3


class Meneger:

    def __init__(self, name, surname, date_birthday, date_s_meneger, user_id,
                    applications=None, zp_in_byn = 0.0, messages=None):
        self.name = name
        self.surname = surname
        self.date_birthday = date_birthday
        self.date_s_meneger = date_s_meneger
        self.applications = applications
        self.user_id = user_id
        self.zp_in_byn = zp_in_byn
        self.messages = messages if messages else []

    def chek_zp_in_byn(self,user_id):
        print(f"Ваша ЗП = {self.zp_in_byn}")


    def chek_messages(self,user_id,conn):
        for messages in self.messages:
            print(f"ваши сообщения: \n {messages} ")

    def send_application(self,conn):
        cursor = conn.cursor()
        send_user_id = input('Введи id пользователя:')
        cursor.execute("SELECT messages FROM users WHERE user_id = ?",(send_user_id))
        result = cursor.fetchone()
        if result:
            messages_json = result[0]
            if messages_json:
                messages = json.loads(messages_json)
            else:
                messages = []
            send_message = input("Введи сообщение:")
            messages.append(send_message)
            cursor.execute("UPDATE users SET messages = ? WHERE user_id = ?",(json.dumps(messages),send_user_id))
            conn.commit()
            print("Сообщение оправлено")
        else:
            print("Пользователь не найден")

