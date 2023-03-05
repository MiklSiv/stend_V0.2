import time
import socket
import threading
import sqlite3
import spisokAbonentRead

# переменные



COM_FlAG = {"COM1": ["close", 'ser', "close", spisokAbonentRead.COM1_read],
            "MEAT": ["close", 'ser', "close"],
            "TPortable": ["close", 'ser', "close"],
            "MOOS": ["close", 'ser', "close"],
            "NRight": ["close", 'ser', "close"],
            "NLeft": ["close", 'ser', "close"],
            "PRight": ["close", 'ser', "close"],
            "PLeft": ["close", 'ser', "close"],
            "KWR102": ["close", 'ser', "close"],
            "BASE": ["close", 'ser', "close"],
            "DS1820": ["close", 'ser', "close"]}

COM_FlAG_loop = {"NLeft" : ['message', 'ask'],
                 "NRight" : ['message', 'ask'],
                 "PRight" : ['message', 'ask'],
                 "PLeft" : ['message', 'ask']}




COM_config = {}

def com_config():# чтение файла с конфигурациями
    COM_conf = []
    try:
        with open('text_config.txt', 'r') as conf:
            while a := conf.readline():
                COM_conf.append(a.split())
        for i in COM_conf:
            COM_config[i[0]] = i[1]
        return True
    except:
        return False

# чтение информации с абонентов

def loop_read(name):
    print(COM_FlAG[name])

    while COM_FlAG[name][1]:
        while COM_FlAG[name][0] == 'open':
            if COM_FlAG[name][1].isOpen():
                for i in COM_FlAG[name][3].keys():
                    try:
                        COM_FlAG[name][1].write(i.encode('utf-8'))
                        while True:
                            ask = COM_FlAG[name][1].readline().decode('utf-8')
                            if ask[0] != '#':
                                break
                        COM_FlAG[name][3][i] = ask
                        #print(ask)
                    except:
                        print('<loop_read - COM error>')

            COM_FlAG[name][2] = 'open'
            print ("open com")
            time.sleep(2)
            COM_FlAG[name][2] = 'close'
            print("close com")

def read_abonentov(com):
    ab1 = threading.Thread(target=loop_read, args= (com,))
    ab1.start()



# управление обращением к сом портам

def client_to_com(client): #разовое обращение к портам
    try:
        print ('clien give')
        data = client.recv(1024).decode('utf-8').split()  # спиок входных данных типа [x, y]: x - имя сом порта, у - команда для компорта
        if len(data) != 2:
            client.send('<ASK_error - bad struct message>'.encode('utf-8'))
        elif data[0] not in COM_FlAG:
            client.send('<ASK_error - com abonent NULL>'.encode('utf-8'))

        elif data[0] in COM_FlAG_loop:
            COM_FlAG_loop[data[0]][0] = data[1]
            time.sleep(2)
            client.send(COM_FlAG_loop[data[0]][1].encode('utf-8'))

        else:
            while COM_FlAG[data[0]][0] == 'close' or COM_FlAG[data[0]][2] == 'close':
                time.sleep(0.1)
            else:
                try:
                    COM_FlAG[data[0]][0] = 'close'
                    if COM_FlAG[data[0]][1].isOpen():
                        COM_FlAG[data[0]][1].write(data[1].encode('utf-8'))
                        while True:
                            ask = COM_FlAG[data[0]][1].readline().decode('utf-8')
                            if ask[0] != '#':
                                break
                        with sqlite3.connect('data_base.db') as tabl:
                            cursor = tabl.cursor()
                            zaps = (time.time(), data[1], ask)
                            cursor.execute(f'''INSERT INTO {data[0]} (time, in_com, out_com) VALUES (?, ?, ?)''', zaps)
                            tabl.commit()
                        client.send(ask.encode('utf-8'))
                        COM_FlAG[data[0]][0] = 'open'
                    else:
                        client.send('<ASK_error - COM error>'.encode('utf-8'))
                except:
                    client.send('<ASK_error - COM error>'.encode('utf-8'))
    except:
        pass


def loop(ser, com_name): # обращение к порту с зацикливанием
    def write_table():
        with sqlite3.connect('data_base.db') as tabl:
            cursor = tabl.cursor()
            zaps = (time.time(), COM_FlAG_loop[com_name][0], COM_FlAG_loop[com_name][1])
            cursor.execute(f'''INSERT INTO {com_name} (time, in_com, out_com) VALUES (?, ?, ?)''', zaps)
            tabl.commit()


    def send_loop():
        in_text = "0"
        while COM_FlAG_loop[com_name][0] == 'message':
            time.sleep(0.5)
        count = 2
        while count:
            try:
                ser.write(COM_FlAG_loop[com_name][0].encode('utf-8'))
            except:
                print('ex send start')
            count -= 1
        while COM_FlAG[com_name][0]:
            try:
                if in_text != COM_FlAG_loop[com_name][0]:
                    in_text = COM_FlAG_loop[com_name][0]
                    write_table()
                if ser.isOpen():
                    ser.write(in_text.encode('utf-8'))
            except:
                print ('ex send prog')
            time.sleep(1)
        return print('end sendloop')


    def read_loop():
        while COM_FlAG_loop[com_name][0] == 'message':
            time.sleep(0.5)

        out_text = ''
        flag = False
        while COM_FlAG[com_name][0]:
            try:
                a = ser.read().decode('utf-8')
                if a == "U":
                    if COM_FlAG_loop[com_name][1] != out_text:
                        COM_FlAG_loop[com_name][1] = out_text
                        write_table()
                    out_text = a
                    flag = True
                elif flag == False:
                    pass
                else:
                    out_text += a
            except:
                pass
        return print('end readloop')
    send_lo = threading.Thread(target= send_loop)
    read_lo = threading.Thread(target= read_loop)
    send_lo.start()
    read_lo.start()



# блок управления сервером
SERVER_FLAG = False
server = ''

def server_on(): # включение сервера
    global server, SERVER_FLAG
    SERVER_FLAG = True
    Spisok_client = [False] * 1000
    SERVER_ADDRESS = ('localhost', 5000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(SERVER_ADDRESS)
    server.listen(10)
    print(server)
    while SERVER_FLAG:  # сканер появления клиентов. отправка сообщения в сом порт и обратно
        print ('server poisk')
        try:
            client, address = server.accept()
            for i in Spisok_client:
                if i == False:
                    i = threading.Thread(target=client_to_com, args = (client, ))
                    i.start()
                    break
        except:
            print('exept poisk')
            pass
    SERVER_FLAG = False

def server_off(): #отключение сервера
    global SERVER_FLAG
    if SERVER_FLAG:
        SERVER_FLAG = False
        server.close()



