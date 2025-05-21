#!E:\PythonP\Python3.13\python.exe

import os
import sys
import re
import mysql.connector as sq_con
from http import cookies
from urllib.parse import parse_qs
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
class SQL_con():
        config = {
            'host': 'localhost',       # Адрес сервера БД
            'user': 'root',          # Имя пользователя
            'password': '1234',     # Пароль
            'database': 'web_back',      # Название БД
        }
        @staticmethod
        def post_user(data):

            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                INSERT INTO users (fio, phone, email, birth_date, gender, bio)
                VALUES ('{data["fio"]}','{data["phone"]}','{data["email"]}',
                '{data["birth_date"]}' , {data["gender"]}, '{data["bio"]}');
                ''')
            conn.commit()
            conn.close()

        @staticmethod    
        def get_user_id(data):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            curr.execute(f'''
                SELECT * FROM users WHERE (fio='{data["fio"]}' AND phone = '{data["phone"]}'
                AND email = '{data["email"]}' AND birth_date = '{data["birth_date"]}'
                AND gender = {data["gender"]} AND bio = '{data["bio"]}');
                ''')
            user = curr.fetchall()
            conn.close()
            if(len(user)!=0):
                return user[0][0]
            return -1
        @staticmethod
        def post_language(user_id, data):
            conn = sq_con.connect(**SQL_con.config)
            curr = conn.cursor()
            for i in data:
                curr.execute(f'''
                    INSERT INTO users_languages VALUES ({user_id}, {i});
                    ''')
            conn.commit()
            conn.close()

def main():
    if method=='GET':
        cookie = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in os.environ:
            cookie.load(os.environ['HTTP_COOKIE'])
        env = Environment(
            loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
        )
        template = env.get_template('index.html')
        output = template.render(**cookie)
        #Выводим страницу
        print("Status: 200 OK")
        print("Content-Type: text/html; charset=utf-8")
        print()  # Пустая строка между заголовками и телом
        print(output)
    elif method=="POST":
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        post_data = sys.stdin.read(content_length)
        new_data = parse_qs(post_data)
        
        #Валидация
        errors = {}

        #Поля для вставки
        fields = {}

        #Имя
        try:
            fio = new_data['field-fio'][0]
            fields["fio"] = fio
            if fio == '':
                errors['er_fio'] = "ФИО обязательно для заполнения"
            elif not re.match(r'^[A-Za-zА-Яа-яёЁ\s-]{1,150}$', fio):
                errors['er_fio'] = 'ФИО должно содержать только буквы, пробелы и дефисы (макс. 150 символов)'
        except:
            errors['er_fio'] = "Поле Фио не может быть пустым"
            fields["fio"] = ""

        #email
        try:
            email = new_data['field-email'][0]
            fields["email"] = email
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
                errors['er_email'] = 'Введите корректный email'
        except:
            errors['er_email'] = "Поле email не может быть пустым"
            fields["email"] = ""

        #ЯП
        try:
            languages = new_data["languages"]
            fields["languages"] = languages 
        except:
            errors['er_languages'] = 'Выберете хотя бы 1 язык программирования'
            fields["languages"] = "" 

        #Дата рождения
        try:
            birth_date = datetime.strptime(new_data['field-birthday'][0], '%Y-%m-%d').date()
            fields["birth_date"] = birth_date
            if birth_date > datetime.now().date():
                errors['birth_date'] = 'Дата рождения не может быть в будущем'
        except ValueError:
            errors['er_birth_date'] = 'Некорректный формат даты. Используйте ГГГГ-ММ-ДД'
            fields["birth_date"] = new_data['field-birthday'][0]
        except KeyError:
            errors['er_birth_date'] = 'Поле даты не может быть пустым'
            fields["birth_date"] = " "

        #Телефон
        try:
            phone = new_data['field-tel'][0]
            fields["phone"] = phone
            cleaned_phone = re.sub(r'[^\d]', '', phone)
            # Проверяем основные форматы для России
            if not re.fullmatch(r'^(\+7|8)\d{10}$', cleaned_phone):
                errors['er_phone'] = "Введите корректный номер телефона(Россия)"
        except:
            errors["er_phone"] = "Поле email не может быть пустым"
            fields["phone"] = ""

        #Cогласие
        try:
            if not new_data["check-1"]:
                errors['er_contract_agreed'] = "Ознакомьтесь с контрактом для отправки"
        except:
            errors['er_contract_agreed'] = "Ознакомьтесь с контрактом для отправки" 

        #Пол
        gender = new_data["radio-group-1"][0]
        fields["checked"+gender] = "checked"
        #Биография
        try:
            bio = new_data["bio"][0]
        except:
            bio = ""
        fields["bio"] = bio

        #Подключаем печеньки
        cookie = cookies.SimpleCookie()
        if 'HTTP_COOKIE' in os.environ:
            cookie.load(os.environ['HTTP_COOKIE'])
        
        #Проверка на ошибки
        if errors:
            for field, error in fields.items():
                try:
                    del cookie["er_"+field]
                except Exception as e:
                    ...
            expires = datetime.now() + timedelta(days=365)
            for field, error in errors.items():
                cookie[field] = error
            for field, value in fields.items():
                if field != 'contract_agreed':
                    if field != "languages":
                        cookie[field] = value
                    else:
                        cookie[field] = ''.join(value)
                    cookie[field]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            env = Environment(
            loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
            )
            template = env.get_template('index.html')
            output = template.render(**cookie)
            for field, error in errors.items():
                del cookie[field]
            #Выводим страницу
            print("Status: 200 OK")
            print("Content-Type: text/html; charset=utf-8")
            print(cookie.output())  # Печатаем заголовки Set-Cookie
            print()  # Пустая строка между заголовками и телом
            print(output)
        else:
            expires = datetime.now() + timedelta(days=365)
            for field, error in fields.items():
                try:
                    del cookie["er_"+field]
                except Exception as e:
                    ...
            for field, value in fields.items():
                if field != 'contract_agreed':
                    if field != "languages":
                        cookie[field] = value
                    else:
                        cookie[field] = ''.join(value)
                    cookie[field]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
            #Переделываем данные
            new_data = {
                    "fio": fio,
                    "phone": phone,
                    "email": email,
                    "birth_date": birth_date,
                    "gender": gender,
                    "bio": bio,
                }
            #Закидываем данные в бд
            user_id = SQL_con().get_user_id(new_data)
            if (user_id==-1):
                SQL_con().post_user(new_data)
                SQL_con().post_language(SQL_con().get_user_id(new_data), languages)
                phrase = "Форма успешно отправлена"
            else:
                phrase = "Вы уже отправляли форму"
            print("Status: 200 OK")
            print("Content-Type: text/html; charset=utf-8")
            print(cookie.output())  # Печатаем заголовки Set-Cookie
            print()
            env = Environment(
                loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
            )
            template = env.get_template('index.html')
            output = template.render(**cookie, mess = phrase)
            print(output)
    else:
        print("Status: 404 Not Found")
        print("Content-Type: text/html; charset=utf-8")
        print("Wrong url (Change url to '/' pls)")
method = os.environ.get('REQUEST_METHOD', '')
sys.stdout.reconfigure(encoding='utf-8')
try:
    main()
except Exception as e:
    error_msg = f"Critical error: {e}"
    file = open("logs.txt", "w")
    file.write(error_msg)
    file.close()

