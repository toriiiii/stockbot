# Backend

StockBot utilizes Django REST Framework with a SQLite database.

## Prerequisites
- Python

## Venv Setup

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

## DB Setup

StockBot uses a PostgreSQL database deployed on Render. To connect to the database, set the following environment variable:
```
DATABASE_URL=postgresql://stockbot_db_fzxp_user:LRvHfiWRWJf0eSXuEIDQJjv3SqzxLjpv@dpg-d5km5kh4tr6s73br7tbg-a.oregon-postgres.render.com/stockbot_db_fzxp
```
This is the current external URL for database. Due to Render's free tier limitations, the database expires every month. This link will expire on February 14th, 2026.

## Django Admin Setup

1. Run development server and visit http://127.0.0.1:8000/ to test if it works
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

2. Create superuser for admin site access
```
python manage.py createsuperuser
```

3. Run server again and visit the admin site (http://127.0.0.1:8000/admin)
```
python manage.py runserver
```