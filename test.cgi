#!E:\PythonP\Python3.13\python.exe

import mysql.connector as sq_con
def find_error():
    print("Content-Type: text/html\r\n\r\n")
    print("<h1>500 Server Error</h1>")
    print("<p>Произошла ошибка. Администратор уведомлен.</p>")
try:
    import os
    import sys
    import re
    import logging
    from datetime import datetime
    from urllib.parse import parse_qs
    from http import cookies
    from jinja2 import Environment, FileSystemLoader
    import html
    def escape_html(text):
        return html.escape(str(text))
    # По какой-то причине test.cgi не хочет импортировать database.propert
    # поэтому я просто запихнул класс сюда

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
    #os.environ получает инфу о переменных окружениях
    method = os.environ.get('REQUEST_METHOD', '')
    sys.stdout.reconfigure(encoding='utf-8')
    if method=="GET":
        cookie = cookies.SimpleCookie()
        try:
            cookie.load(os.environ['HTTP_COOKIE'])
        except:
            ...
        if len(cookie)<=1:
            print("Status: 200 OK\r")
            print("Content-Type: text/html; charset=UTF-8\r\n\r\n")
            env = Environment(
                loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
                autoescape=True                # Автоматическое экранирование HTML
                ) 
            template = env.get_template('index.html')
            output = template.render(**cookie)
            print(output)
        else:
            print("Status: 200 OK\r")
            print(cookie.output())
            print("Content-Type: text/html; charset=UTF-8\r\n\r\n")
            env = Environment(
                loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
                autoescape=True                # Автоматическое экранирование HTML
                ) 
            template = env.get_template('index.html')
            output = template.render(**cookie)
            print(output)
    elif method=="POST":
        cookie = cookies.SimpleCookie()
        try:
            cookie.load(os.environ['HTTP_COOKIE'])
        except:
            ...
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        post_data = sys.stdin.read(content_length)
        new_data = parse_qs(post_data)
        
        #Валидация
        errors = {}
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

        #телефон
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
        if errors:
            for field, error in errors.items():
                cookie[field] = error
            for field, value in fields.items():
                if field != 'contract_agreed':
                    cookie[field] = escape_html(value)
                if field == "languages":
                    cookie[field] = ''.join(value)

            print("Status: 200 OK\r")
            print(cookie.output())
            print("Content-Type: text/html; charset=UTF-8\r\n\r\n")

            env = Environment(
                loader=FileSystemLoader('.'),  # Ищем шаблоны в текущей директории
                autoescape=True                # Автоматическое экранирование HTML
                ) 
            template = env.get_template('index.html')
            output = template.render(**cookie)
            print(output)
        else:
            for field, value in fields.items():
                if field != 'contract_agreed':
                    cookie[field] = escape_html(value)
                    cookie[field]['max-age'] = 365 * 24 * 60 * 60
                    cookie[field]["path"] = "/"
                if field == "languages":
                    cookie[field] = ''.join(value)
                    cookie[field]['max-age'] = 365 * 24 * 60 * 60
                    cookie[field]["path"] = "/"
            # Очищаем ошибки (если были)
            for field in errors.keys():
                cookie[field] = ''
                cookie[field]['expires'] = 0
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

            print("Status: 200 OK\r")
            print(cookie.output())
            print("Content-Type: text/html\r\n\r\n")
            Success_html = f'''
    <head>
    <meta charset="UTF-8">
    <link href="static/styles.css" rel="stylesheet" type="text/css"/>
    <title> Дом Баззиков </title>
    </head>
    <body>
    <header>
    <div class = "title_block">
        <a href="test.cgi">
            <img class = "img-header" src="static/hyperbuzz_pin.png"/>
        </a>
        <h1> ДОМ БАЗЗИЛ </h1>
    </div>
    <nav>
        <div class = "a-1"><a href = "#">О сайте</a></div>
        <div class = "a-2"><a href = "#">Добавить статью</a></div>
        <div class = "a-3"> <a href = "#">Тех поддежка</a></div>
    </nav>
    </header>
    <div class="main_block">
    <form id = "tablo">
    <label>{phrase}</label>
    </form>
    </div>
    <footer>
    <p> Ковязин Кирилл (c)</p>
    </footer>
    </body> 
            '''
            print(Success_html)
    else:
        print("Status: 404 Not Found\r")
        print("Content-Type: text/html\r\n\r\n")
        print("Wrong url (Change url to '/' pls)")
except Exception as e:
    error_msg = f"Critical error: {e}"
    file = open("logs.txt", "w")
    file.write(error_msg)
    file.close()
    print("Content-Type: text/html\r\n\r\n")
    print("<h1>500 Server Error</h1>")
    print("<p>Произошла ошибка. Администратор уведомлен.</p>")