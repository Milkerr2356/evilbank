# client_database.py

import sqlite3
import json

class ClientDatabase:
    def __init__(self, db_name='bank.db'):
        self.db_name = db_name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    surname TEXT,
                    date_birthday TEXT,
                    telephone_number TEXT,
                    date_s_client TEXT,
                    number_of_schet TEXT,
                    have_byn REAL,
                    have_rub REAL,
                    have_usd REAL,
                    history_of_operations TEXT,
                    applications TEXT,
                    messages TEXT
                )
            ''')
            conn.commit()

    def save_client(self, client):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO clients (
                    user_id, name, surname, telephone_number, date_birthday, date_s_client,
                    number_of_schet, have_byn, have_rub, have_usd,
                    history_of_operations, applications, messages
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client.user_id,
                client.name,
                client.surname,
                client.date_birthday,
                client.date_s_client,
                client.number_of_schet,
                client.have_byn,
                client.have_rub,
                client.have_usd,
                json.dumps(client.history_of_operations),
                json.dumps(client.applicatios),
                json.dumps(client.messages)
            ))
            conn.commit()
