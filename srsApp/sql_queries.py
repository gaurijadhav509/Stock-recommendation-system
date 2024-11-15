from django.db import connection
from .models import Users
from django.utils import timezone

#### function for getting one user from table(USERS).
def get_one_user(email):
    query = "SELECT * FROM stock_recommendation_system_db.users WHERE email = %s"
    users = Users.objects.raw(query, [email])
    user_data = {}
    for user in users:
        user_data['user_id'] = user.user_id
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['name'] = user.name
        user_data['created_at'] = user.created_at

    return user_data

def get_one_user_by_id(user_id):
    query = "SELECT * FROM stock_recommendation_system_db.users WHERE user_id = %s"
    users = Users.objects.raw(query, [user_id])
    user_data = {}
    for user in users:
        user_data['user_id'] = user.user_id
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['name'] = user.name
        user_data['created_at'] = user.created_at

    return user_data

### checking that if user is already exists in the database or not in USERS table.
def check_user_exists(email):
    query = "SELECT * FROM stock_recommendation_system_db.users WHERE email = %s"
    users = Users.objects.raw(query, [email])
    return bool(users)

### Insert query for inserting user data in the table USERS.
def insert_user(name, email, password):
    created_at = timezone.now()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO stock_recommendation_system_db.users (name, email, password, created_at) VALUES (%s, %s, %s, %s)",
            [name, email, password, created_at]
        )
