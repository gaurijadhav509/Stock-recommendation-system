from django.db import models

# Create your models here.
#### Entity Tables.
### 1. Users Table
class Users(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField()
    # email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Users"

### 1. Stocks Table

class Stocks(models.Model):
    stock_id = models.AutoField(primary_key=True, null=False)
    stock_symbol = models.CharField(max_length=10, null=False)
    company_name = models.CharField(max_length=255, null=False)
    sector = models.CharField(max_length=100)
    market_cap = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Stocks"

#### Investment Preferences Table.
class Investment_Preferences(models.Model):
    class Risk_Tolerance(models.IntegerChoices):
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3,
    
    class Asset_Type(models.IntegerChoices):
        STOcKS = 1,
        BONDS = 2,
        OPTIONS = 3,
    preference_id = models.AutoField(primary_key=True, null=False)
    preferred_region = models.CharField(max_length=100)
    preferred_exchange = models.CharField(max_length=100)
    risk_tolerance = models.IntegerField(
        choices=Risk_Tolerance.choices,
        default=Risk_Tolerance.LOW
    )
    asset_type = models.IntegerField(
        choices=Asset_Type.choices,
        default=Asset_Type.STOcKS
    )
    # user_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = "Investment_Preferences"

##### Tables for Relationships

## 1. User_Boookmarked Stocks
class User_Bookmarked_Stocks(models.Model):
    # user_id = models.IntegerField(primary_key=True, null=False)
    # stock_id = models.IntegerField(primary_key=True, null=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_bookmarked_stocks"
        unique_together = ('user', 'stock') ### making compsite key

class User_Investment_Preferences(models.Model):
    # user_id = models.IntegerField(primary_key=True, null=False)
    # prefrence_id = models.IntegerField(primary_key=True, null=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    preference = models.ForeignKey(Investment_Preferences, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_investment_preferences"
        unique_together = ('user', 'preference')

class Stock_Investment_Preferences(models.Model):
    # prefrence_id = models.IntegerField(primary_key=True, null=False)
    # stock_id = models.IntegerField(primary_key=True, null=False)
    preference = models.ForeignKey(Investment_Preferences, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "stock_investment_preferences"
        unique_together = ('stock', 'preference')


EXCHANGE_REGION_MAP = {
    'NYSE': 'North America',
    'NASDAQ': 'North America',
    'LSE': 'Europe',
    'BSE': 'Asia',
    'NSE': 'Asia',
    'HKEX': 'Asia',
    'ASX': 'Australia',
    # Add more exchanges as needed
}