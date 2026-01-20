# StockBot

StockBot is a smart kitchen inventory monitor that helps users to keep track of their groceries, reducing food waste, saving money and helping the environment. 

Food waste costs Canadian household $1300.00 anually on average and generates 6.9 million tonnes of CO2. Over half of this food waste is avoidable. 92% of shoppers go to the grocery store without knowing what is already in stock at home. This leads to either buying excess groceries that expire before use, or needing to make additional trips for forgotten groceries. 

StockBot enables users to check their kitchen inventory from anywhere via a mobile app. An integrated camera and force sensor system detects groceries using AI and tracks their usage, letting users know what they own and how much remains. It also warns users of potentially expiring items, further facilitating grocery management. 

# Tools
- Django REST Framework
- React Native
- Expo Go
- Render
- PostgreSQL

# Run StockBot Locally

1. cd into the backend directory. Follow the steps in ./backend/README to set up your local backend environment. Keep your virtual environment activated.

2. Create a second command prompt terminal and cd into the frontend directory. Follow the steps in ./frontend/stockbot-frontend/README to set up your local frontend environment. Keep your virtual environment activated.

3. In your backend terminal, run the Django server and make it accessible outside of localhost

```
python manage.py runserver 0.0.0.0:8000
```

4. In your frontend terminal, run the React Native application and open it on Expo Go.

```
npx expo start -c
```