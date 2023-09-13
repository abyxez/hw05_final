# final_django_project

Автор проекта - Константин Мельник.

***

Эта работа является первой финальной в ходе изучения Django. Здесь описана работа бэкенда, а также фронтенда на языке HTML(+CSS).
В проекте можно оставлять посты и комментарии к ним в различных группах, имитирует работу соц. сети. 

***

## Tecnhologies

- Python 3.10
- Django 2.2.16
- HTML/CSS

***

Локальзый запуск проекта:
```
git clone https://github.com/abyxez/hw05_final

cd hw05_final/
```

Cоздать и активировать виртуальное окружение (macOS/Linux) : 
```
python3 -m venv env

source venv/bin/activate
```

or (Windows)
```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt: 

```
python3 -m pip install --upgrade pip

pip install -r requirements.txt
```

Выполнить миграции: 
```
cd hw05_final/

python3 manage.py migrate

python3 manage.py runserver
```
