#!E:\PythonP\Python3.13\python.exe

import os
from http import cookies
import datetime
import sys

# Включаем отладочную информацию (для разработки)

# Создаем объект для работы с cookies
cookie = cookies.SimpleCookie()

# Получаем cookies из окружения
if 'HTTP_COOKIE' in os.environ:
    cookie.load(os.environ['HTTP_COOKIE'])

# Получаем или устанавливаем счетчик посещений
visit_count = 1
if 'visits' in cookie:
    visit_count = int(cookie['visits'].value) + 1

# Устанавливаем новую cookie
cookie['visits'] = visit_count
# Устанавливаем срок действия - 1 год
expires = datetime.datetime.now() + datetime.timedelta(days=365)
cookie['visits']['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
cookie['visits']['path'] = '/'

# Выводим HTTP заголовки
sys.stdout.reconfigure(encoding='utf-8')
print("Content-Type: text/html; charset=utf-8")
print(cookie.output())  # Печатаем заголовки Set-Cookie
print()  # Пустая строка между заголовками и телом

# Выводим HTML

print(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Пример CGI с Cookies на Python</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .info {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Пример работы с Cookies в CGI (Python)</h1>
    <div class="info">
        <p>Этот скрипт демонстрирует использование cookies в CGI на Python.</p>
        <p>Вы посетили эту страницу: <strong>{visit_count}</strong> раз(а)</p>
        <p>Попробуйте обновить страницу, чтобы увеличить счетчик.</p>
    </div>
</body>
</html>
""")