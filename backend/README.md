# Backend

StockBot utilizes Django REST Framework with a SQLite database.

## Prerequisites
- Python

## Django Setup

1. Clone this repo 
```
git clone https://github.com/toriiiii/stockbot.git
```

2. Create virtual env inside the repo
```
python -m venv venv
venv/Scripts/activate
```

3. Install dependencies in requirements.txt
```
pip install -r requirements.txt
```

4. Run development server and visit http://127.0.0.1:8000/ to test if it works
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

5. Create superuser for admin site access
```
python manage.py createsuperuser
```

6. Run server again and visit the admin site (http://127.0.0.1:8000/admin)
```
python manage.py runserver
```