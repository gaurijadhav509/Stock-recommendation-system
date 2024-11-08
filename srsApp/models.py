from django.db import models

# Create your models here.
class Users(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField()
    # email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Users"
    
class Stocks(models.Model):
    stock_id = models.AutoField(primary_key=True, null=False)
    stock_symbol = models.CharField(max_length=10, null=False)
    company_name = models.CharField(max_length=255, null=False)
    sector = models.CharField(max_length=100)
    market_cap = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Stocks"

class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True, null=False)
    recommended_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(null=False)
    stock_id = models.IntegerField(null=False)
    # user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    # stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "Recommendation"
    
class Bookmarked_Stock(models.Model):
    bookmarked_id = models.AutoField(primary_key=True, null=False)
    bookmarked_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(null=False)
    stock_id = models.IntegerField(null=False)
    # user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    # stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "Bookmarked_Stocks"
    
class Investment_Prefrences(models.Model):
    class Risk_Tolerance(models.IntegerChoices):
        LOW = 1,
        MEDIUM = 2,
        HIGH = 3,
    
    class Asset_Type(models.IntegerChoices):
        STOcKS = 1,
        BONDS = 2,
        OPTIONS = 3,
    prefrences_id = models.AutoField(primary_key=True, null=False)
    user_id = models.IntegerField(null=False)
    preferred_region = models.CharField(max_length=100)
    preferred_exchage = models.CharField(max_length=100)
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
        db_table = "Investment_Prefrences"

# Tables for Relationships
class user_bookmarked_stocks_rel:
    user_id = models.IntegerField(primary_key=True, null=False)
    stock_id = models.IntegerField(primary_key=True, null=False)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_bookmarked_stocks_rel"

class user_recommended_stocks_rel:
    user_id = models.IntegerField(primary_key=True, null=False)
    stock_id = models.IntegerField(primary_key=True, null=False)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_recommended_stocks_rel"

class recommendation_to_stock_rel:
    recommendation_id = models.IntegerField(primary_key=True, null=False)
    stock_id = models.IntegerField(primary_key=True, null=False)
    recommendation_id = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "recommendation_to_stock_rel"

class stock_to_bookmarked_stock_rel:
    user_id = models.IntegerField(primary_key=True, null=False)
    stock_id = models.IntegerField(primary_key=True, null=False)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    stock_id = models.ForeignKey(Stocks, on_delete=models.CASCADE)

    class Meta:
        db_table = "stock_to_bookmarked_stock_rel"

class investment_preference_to_recommendation_rel:
    recommendation_id = models.IntegerField(primary_key=True, null=False)
    prefrences_id = models.IntegerField(primary_key=True, null=False)
    recommendation_id = models.ForeignKey(Recommendation, on_delete=models.CASCADE)
    prefrences_id = models.ForeignKey(Investment_Prefrences, on_delete=models.CASCADE)

    class Meta:
        db_table = "investment_preference_to_recommendation_rel"