# Stock-recommendation-system
Stock Recommendation system for ENSF 607-608

# Final demo videos #
https://drive.google.com/drive/u/0/folders/1v7XQC9bWrwBGTJUQDE1afHY3CuaMPWDn

# ENSF 607 Documentation #
https://github.com/gaurijadhav509/Stock-recommendation-system/tree/main/Documentation%20-607

# ENSF 608 Documentation #
https://github.com/gaurijadhav509/Stock-recommendation-system/tree/main/Documentation-608

# How to run locally #

Create a database on mysql using name - stock_recommendation_system_db
Provide correct privileges for the user (User details in settings.py file)

Run below commands(In root folder in cmd) - 

```py -m venv stock_recommendation_system

stock_recommendation_system\Scripts\activate.bat

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
```


App url - http://127.0.0.1:8000/srsApp/
