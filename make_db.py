import pprint
import sqlite3
import os

def text_config():
    if os.path.isfile('text_config.txt'):
        pass
    else:
        with open('text_config.txt', 'w') as conf:
            S = '''COM1 1 (заменить цифру на номер сом порта)
            MEAT 1
            TPortable 1
            MOOS 1
            NRight 1 
            NLeft 1
            PRight 1
            PLeft 1 
            KWR102 1 
            BASE 1
            DS1820 1'''
            conf.write(S)



def creat_db():
    try:
        conn = sqlite3.connect('data_base.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS COM1 (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS MEAT (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS TABLE TPortable (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS MOOS (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS MOOS (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS NRight (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS NLeft (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS PRight (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS PLeft (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS KWR102 (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS BASE (time real, in_com text, out_com text)''')
        cursor.execute('''CREATE TABLE if NOT EXISTS DS1820 (time real, in_com text, out_com text)''')
        conn.commit()
        conn.close()
    except:
        pass


