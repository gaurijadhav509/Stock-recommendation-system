from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User

from .sql_queries import get_one_user

# Create your tests here.
class LoginViewTests(TestCase):
    ### 
    def setUp(self):
        self.email = 'sanket@gmail.com'
        self.password = 'san'
        self.user = User.objects.create_user(username=self.email, password=self.password)
    
    def test_login_with_valid_credentials(self):
        """Test that the Login page with valid credentials."""
        response = self.client.post(reverse('login'), {
            'u_email': self.email,
            'u_password': self.password,
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('login_success'))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Login Successful!')

    def test_login_with_invalid_credentials(self):
        """Test that the Login page password is again."""
        response = self.client.post(reverse('login'), {
            'u_email': self.email,
            'u_password': 'wrongpassword',
        }, follow=True)

        self.assertRedirects(response, reverse('login'))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'invalid username or password!')

    
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
        self.assertRedirects(response, reverse('login_success'))

        # Check if the success message is displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'User Registerd successfully!')

        # # Verify if the user is actually created
        user = get_one_user(email=self.valid_email)
        self.assertEqual(user['name'], self.valid_name)
        self.assertTrue(user['password'] == self.valid_password)

    def test_signup_with_existing_email(self):
        """Test that the sign up page with existing email address."""
        # Create a user with the same email for testing
        User.objects.create_user(username=self.valid_name, email=self.valid_email, password=self.valid_password)

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
        self.assertEqual(str(messages_list[0]), 'Password doesn\'t match.')

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

    def test_signup_post_empty_password(self):
        """Test that empty password is handled properly."""
        response = self.client.post(self.signup_url, {
            'u_name': self.valid_name,
            'u_email': self.valid_email,  
            'u_password': '', # Empty Password field
            'conf_password': self.confirm_password
        },)

        self.assertEqual(response.status_code, 200)

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Password doesn\'t match.')


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