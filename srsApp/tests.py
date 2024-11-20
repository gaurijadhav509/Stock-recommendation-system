from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .models import Users, Investment_Preferences, Stocks
import json
from srsApp.services import *
from .sql_queries import get_one_user

class ValidateExchangeRegionTestCase(TestCase):
    
    @patch('srsApp.views.EXCHANGE_REGION_MAP', {'NASDAQ': 'North America', 'LSE': 'Europe'})
    def test_validate_exchange_region_exchange_not_recognized(self):
        """Test when the exchange is not recognized."""
        preferred_exchange = 'UNKNOWN_EXCHANGE'
        preferred_region = 'North America'
        
        result = validate_exchange_region(preferred_exchange, preferred_region)
        
        self.assertEqual(result, f"Exchange '{preferred_exchange}' is not recognized.")

    @patch('srsApp.views.EXCHANGE_REGION_MAP', {'NASDAQ': 'North America', 'LSE': 'Europe'})
    def test_validate_exchange_region_match(self):
        """Test when the exchange matches the preferred region."""
        preferred_exchange = 'NASDAQ'
        preferred_region = 'North America'
        
        result = validate_exchange_region(preferred_exchange, preferred_region)
        
        self.assertIsNone(result)  # Since the exchange and region match, we expect None

    @patch('srsApp.views.EXCHANGE_REGION_MAP', {'NASDAQ': 'North America', 'LSE': 'Europe'})
    def test_validate_exchange_region_mismatch(self):
        """Test when the exchange does not match the preferred region."""
        preferred_exchange = 'NASDAQ'
        preferred_region = 'Europe'  # Mismatched region
        
        result = validate_exchange_region(preferred_exchange, preferred_region)
        
        self.assertEqual(result, f"The exchange '{preferred_exchange}' is not located in the preferred region '{preferred_region}'.")
        
class SubmitInvestmentPreferencesTests(TestCase):

    @patch('srsApp.services.genai.GenerativeModel.generate_content')
    def test_get_recommendations_from_gemini_successful(self, mock_generate_content):
        """Test when stock recommendations are fetched successfully from Gemini API."""

        # Mock the response from the Gemini model's generate_content method
        mock_generate_content.return_value = type('obj', (object,), {'text': '''
        [
            {"symbol": "AAPL", "company": "Apple Inc.", "sector": "Technology", "market_cap": 2.5},
            {"symbol": "GOOGL", "company": "Alphabet Inc.", "sector": "Technology", "market_cap": 1.8}
        ]
        '''})

        # Create a test user and investment preferences
        user_instance = Users.objects.create(user_id=1, name='Test User', email='test@example.com', password='testpassword')
        investment_preference = Investment_Preferences.objects.create(
            risk_tolerance=3,
            asset_type=1,  # Assuming '1' is for Stocks
            preferred_region='North America',
            preferred_exchange='NASDAQ'
        )

        # Call the function to fetch recommendations
        recommendations = get_recommendations_from_gemini(investment_preference)

        # Assert the recommendations contain the correct data
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]['symbol'], 'AAPL')
        self.assertEqual(recommendations[0]['company'], 'Apple Inc.')
        self.assertEqual(recommendations[1]['symbol'], 'GOOGL')
        self.assertEqual(recommendations[1]['company'], 'Alphabet Inc.')



    @patch('srsApp.services.genai.GenerativeModel.generate_content')
    def test_get_recommendations_from_gemini_error(self, mock_generate_content):
        """Test when an error occurs while fetching recommendations from Gemini."""

        # Mock an error from Gemini (e.g., API failure)
        mock_generate_content.side_effect = Exception("Gemini API error")

        # Create a test user and investment preferences
        user_instance = Users.objects.create(user_id=1, name='Test User', email='test@example.com', password='testpassword')
        investment_preference = Investment_Preferences.objects.create(
            risk_tolerance=3,
            asset_type=1,  # Assuming '1' is for Stocks
            preferred_region='North America',
            preferred_exchange='NASDAQ'
        )

        # Expecting a ValueError to be raised due to the exception in Gemini API
        with self.assertRaises(ValueError):
            get_recommendations_from_gemini(investment_preference)



    @patch('srsApp.services.genai.GenerativeModel.generate_content')
    def test_get_recommendations_from_gemini_empty_response(self, mock_generate_content):
        """Test when an empty response is received from Gemini."""
        
        # Mock an empty response from Gemini
        mock_generate_content.return_value = type('obj', (object,), {'text': ''})

        # Create a test user and investment preferences
        user_instance = Users.objects.create(user_id=1, name='Test User', email='test@example.com', password='testpassword')
        investment_preference = Investment_Preferences.objects.create(
            risk_tolerance=3,
            asset_type=1,  # Assuming '1' is for Stocks
            preferred_region='North America',
            preferred_exchange='NASDAQ'
        )

        # Expecting a ValueError to be raised due to the empty response
        with self.assertRaises(ValueError):
            get_recommendations_from_gemini(investment_preference)

class LoginViewTests(TestCase):
    ### 
    def setUp(self):
        self.email = 'sanket@gmail.com'
        self.password = 'sanket'
        self.user = Users.objects.create(email=self.email, password=self.password)
    
    def test_login_with_valid_credentials(self):
        """Test that the Login page with valid credentials."""
        response = self.client.post(reverse('login'), {
            'u_email': self.email,
            'u_password': self.password,
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('investment_preferences_view'))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Login successful!')

    def test_login_with_invalid_credentials(self):
        """Test that the Login page password is again."""
        response = self.client.post(reverse('login'), {
            'u_email': self.email,
            'u_password': 'wrongpassword',
        }, follow=True)

        self.assertRedirects(response, reverse('login'))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Invalid username or password!')

    
    def test_login_view_renders_template(self):
        """Test that the Login page renders correctly."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')



class SignupViewTests(TestCase):

    def setUp(self):
        self.valid_name = 'Test User'
        self.valid_email = 'testuser@example.com'
        self.valid_password = 'testpassword'
        self.invalid_email = 'invalid-email'
        self.invalid_password = 'short'
        self.confirm_password = self.valid_password
        self.signup_url = reverse('user_signup_view')

    def test_signup_with_valid_data(self):
        # POST request with valid data
        """Test that the sign up page with valid data."""
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': self.valid_email,
            'u_password': self.valid_password,
            'conf_password': self.confirm_password,
        }, follow= True)

        # Check if the user was redirected to the login success page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login'))

        # Check if the success message is displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'User registered successfully!')

        # # Verify if the user is actually created
        user = get_one_user(email=self.valid_email)
        self.assertEqual(user['name'], self.valid_name)
        self.assertTrue(user['password'] == self.valid_password)

    def test_signup_with_existing_email(self):
        """Test that the sign up page with existing email address."""
        # Create a user with the same email for testing
        Users.objects.create(name=self.valid_name, email=self.valid_email, password=self.valid_password)

        # POST request with the same email
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': 'sanket@gmail.com',
            'u_password': self.valid_password,
            'conf_password': self.confirm_password,
        }, follow=True)

        # Check if the user is redirected back to signup page with a warning
        self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, reverse('user_signup_view'))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'User already exists.')

    def test_signup_with_password_mismatch(self):
        """Test that the sign up page with password mismatch."""
        # POST request with mismatched passwords
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': self.valid_email,
            'u_password': self.valid_password,
            'conf_password': 'differentpassword',  # Mismatched password
        })

        # Check if the user is redirected back to signup page with a warning
        self.assertEqual(response.status_code, 200)  # Should render signup page
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Passwords do not match.')

    def test_signup_with_invalid_email(self):
        """Test that the sign up page with invalid email."""
        # POST request with invalid email
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': self.invalid_email,  # Invalid email
            'u_password': self.valid_password,
            'conf_password': self.confirm_password,
        },)

        # Check if the user is redirected back to signup page with a warning
        self.assertEqual(response.status_code, 200)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Email is invalid')

    def test_signup_post_empty_email(self):
        """Test that empty email is handled properly."""
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': '',  # Empty email field
            'u_password': self.valid_password,
            'conf_password': self.confirm_password
        },)

        self.assertEqual(response.status_code, 200)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Email is invalid')

    @patch('srsApp.views.insert_user')  # Mocking insert_user function
    def test_signup_with_server_error(self, mock_insert_user):
        # Simulate a server error by making insert_user raise an exception
        mock_insert_user.side_effect = Exception('Server Error')

        # POST request with valid data
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': self.valid_email,
            'u_password': self.valid_password,
            'conf_password': self.confirm_password,
        })

        # Check if the user is redirected back to signup page with a warning
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Something went wrong.')
    
    def test_signup_view_renders_template(self):
        """Test that the Signup page renders correctly."""
        response = self.client.get(reverse('user_signup_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')