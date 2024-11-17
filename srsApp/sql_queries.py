from django.db import connection
from .models import *
from django.utils import timezone
from django.db import connection

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

# Function to insert or update investment preferences in the Investment_Preferences table
def upsert_investment_preferences(user_id, risk_tolerance, asset_type, preferred_region, preferred_exchange):
    # Fetch the Users instance using user_id
    try:
        user_instance = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        raise ValueError(f"User with id {user_id} does not exist.")
    
    # Check if the investment preference record exists for the user
    query_check = """
        SELECT COUNT(*) 
        FROM stock_recommendation_system_db.investment_preferences 
        WHERE preferred_region = %s AND preferred_exchange = %s AND risk_tolerance = %s AND asset_type = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query_check, [preferred_region, preferred_exchange, risk_tolerance, asset_type])
        exists = cursor.fetchone()[0] > 0
    
    if exists:
        # Update existing investment preference
        query_update = """
            UPDATE stock_recommendation_system_db.investment_preferences 
            SET risk_tolerance = %s, asset_type = %s, preferred_region = %s, preferred_exchange = %s
            WHERE preferred_region = %s AND preferred_exchange = %s AND risk_tolerance = %s AND asset_type = %s
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_update, [risk_tolerance, asset_type, preferred_region, preferred_exchange, preferred_region, preferred_exchange, risk_tolerance, asset_type])
            
        # Get the preference_id of the updated record
        query_select_preference_id = """
            SELECT preference_id 
            FROM stock_recommendation_system_db.investment_preferences 
            WHERE preferred_region = %s AND preferred_exchange = %s AND risk_tolerance = %s AND asset_type = %s
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_select_preference_id, [preferred_region, preferred_exchange, risk_tolerance, asset_type])
            preference_id = cursor.fetchone()[0]
    
    else:
        # Insert new investment preference record
        query_insert = """
            INSERT INTO stock_recommendation_system_db.investment_preferences 
            (preferred_region, preferred_exchange, risk_tolerance, asset_type)
            VALUES (%s, %s, %s, %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_insert, [preferred_region, preferred_exchange, risk_tolerance, asset_type])
        
        # Get the preference_id of the inserted record
        with connection.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            preference_id = cursor.fetchone()[0]
    
    # Insert record into the User_Investment_Preferences table
    # Check if the relationship already exists using raw query
    query_check_relationship = """
        SELECT COUNT(*) 
        FROM stock_recommendation_system_db.user_investment_preferences 
        WHERE user_id = %s AND preference_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query_check_relationship, [user_id, preference_id])
        relationship_exists = cursor.fetchone()[0] > 0
    
    if not relationship_exists:
        # Insert the relationship record into the user_investment_preferences table
        query_insert_relationship = """
            INSERT INTO stock_recommendation_system_db.user_investment_preferences 
            (user_id, preference_id)
            VALUES (%s, %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_insert_relationship, [user_id, preference_id])
    return preference_id

# Function to insert stock data into the Stocks table and map to relationship table
def insert_stock_and_map_to_investment_preference(stock_symbol, company_name, sector, market_cap, preference_id):
    created_at = timezone.now()
    
    # Check if the stock already exists to avoid duplicates
    query_check = """
        SELECT COUNT(*) 
        FROM stock_recommendation_system_db.stocks 
        WHERE stock_symbol = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query_check, [stock_symbol])
        exists = cursor.fetchone()[0] > 0
    
    if not exists:
        # Insert new stock record into the Stocks table
        query_insert = """
            INSERT INTO stock_recommendation_system_db.stocks 
            (stock_symbol, company_name, sector, market_cap, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_insert, [stock_symbol, company_name, sector, market_cap, created_at])
        
        # Fetch the stock_id of the inserted record
        with connection.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            stock_id = cursor.fetchone()[0]
    else:
        # If stock exists, fetch the existing stock_id
        query_get_stock_id = """
            SELECT stock_id 
            FROM stock_recommendation_system_db.stocks 
            WHERE stock_symbol = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query_get_stock_id, [stock_symbol])
            stock_id = cursor.fetchone()[0]
    
    # Check if the relationship already exists in the stock_investment_preferences table
    query_check_relationship = """
        SELECT COUNT(*) 
        FROM stock_recommendation_system_db.stock_investment_preferences 
        WHERE stock_id = %s AND preference_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query_check_relationship, [stock_id, preference_id])
        relationship_exists = cursor.fetchone()[0] > 0
    
    if not relationship_exists:
        # Insert the relationship record into the stock_investment_preferences table
        query_insert_relationship = """
            INSERT INTO stock_recommendation_system_db.stock_investment_preferences 
            (stock_id, preference_id)
            VALUES (%s, %s)
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query_insert_relationship, [stock_id, preference_id])
    
    return stock_id
