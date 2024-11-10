from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .models import Users, Investment_Preferences, Stocks
import json
from srsApp.services import get_recommendations_from_gemini



class InvestmentPreferencesViewTests(TestCase):
    
    def test_investment_preferences_view_renders_template(self):
        """Test that the investment preferences page renders correctly."""
        response = self.client.get(reverse('investment_preferences_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'investment_preferences.html')


class SubmitInvestmentPreferencesTests(TestCase):

    def test_submit_investment_preferences_exchange_region_mismatch(self):
        """Test when the exchange does not match the preferred region."""
        Users.objects.create(user_id=1, name='Test User', email='test@example.com', password='testpassword')

        # Mock EXCHANGE_REGION_MAP to simulate the mismatch
        with patch('srsApp.views.EXCHANGE_REGION_MAP', {'NASDAQ': 'Europe'}):
            response = self.client.post(reverse('submit_investment_preferences'), {
                'risk_tolerance': 5,
                'asset_type': 1,
                'preferred_region': 'North America',
                'preferred_exchange': 'LSE'
            })
            
            self.assertEqual(response.status_code, 200)
            # Check if error message is passed in context
            self.assertIn('error', response.context)
            self.assertEqual(response.context['error'], "The exchange 'LSE' is not located in the preferred region 'North America'.")
    

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
            user_id=user_instance.user_id,
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
            user_id=user_instance.user_id,
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
            user_id=user_instance.user_id,
            risk_tolerance=3,
            asset_type=1,  # Assuming '1' is for Stocks
            preferred_region='North America',
            preferred_exchange='NASDAQ'
        )

        # Expecting a ValueError to be raised due to the empty response
        with self.assertRaises(ValueError):
            get_recommendations_from_gemini(investment_preference)