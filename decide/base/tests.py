from django.contrib.auth.models import User
from voting.models import Voting
from census.models import Census
from decide.settings import LOGIN_URL
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods

# Create non naive datetime objects
from datetime import datetime
from django.utils import timezone
import pytz

#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class BaseTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.token = None
        mods.mock_query(self.client)

        user_noadmin = User(username='noadmin')
        user_noadmin.set_password('qwerty')
        user_noadmin.save()

        user_admin = User(username='admin', is_staff=True)
        user_admin.set_password('qwerty')
        user_admin.save()

    def tearDown(self):
        self.client = None
        self.token = None

    def login(self, user='admin', password='qwerty'):
        data = {'username': user, 'password': password}
        response = mods.post('authentication/login', json=data, response=True)
        self.assertEqual(response.status_code, 200)
        self.token = response.json().get('token')
        self.assertTrue(self.token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def logout(self):
        self.client.credentials()


#Test de navegación

class NavBarTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
       
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


    def test_noAdminCorrectNavbar(self, user='noadmin', password='qwerty'):
        '''
        Test if a non admin user can access to the Home link in the navbar
        '''

        self.driver.get(f"{self.live_server_url}{LOGIN_URL}")
        self.driver.find_element(By.ID, "id_username").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password,Keys.ENTER)

        home_nav_nink_exists = len(self.driver.find_elements(By.ID, "nav-home"))
        admin_nav_link_exists = len(self.driver.find_elements(By.ID, "nav-administration"))
        user_nav_link_exists = len(self.driver.find_elements(By.ID, "nav-user"))

        self.assertTrue(home_nav_nink_exists == 1, msg='Navbar link called "Home" not found')
        self.assertTrue(admin_nav_link_exists == 0, msg='Navbar link called "Administration" found, expected not to be found if logged as non admin user')
        self.assertTrue(user_nav_link_exists == 1, msg='Navbar dropdown with user data not found')


    def test_adminCorrectNavbar(self, user='admin', password='qwerty'):
        '''
        Test if an admin can access to Home and Administration dropdown in the navbar
        '''

        self.driver.get(f"{self.live_server_url}{LOGIN_URL}")
        self.driver.find_element(By.ID, "id_username").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password,Keys.ENTER)

        home_nav_nink_exists = len(self.driver.find_elements(By.ID, "nav-home"))
        admin_nav_link_exists = len(self.driver.find_elements(By.ID, "nav-administration"))
        user_nav_link_exists = len(self.driver.find_elements(By.ID, "nav-user"))

        self.assertTrue(home_nav_nink_exists == 1, msg='Navbar link called "Home" not found')
        self.assertTrue(admin_nav_link_exists == 1, msg='Navbar link called "Administration" not found')
        self.assertTrue(user_nav_link_exists == 1, msg='Navbar dropdown with user data not found')


class IndexViewTestCase(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        #Create votings in different states and relate a user via census
        voter_id = User.objects.only('id').get(username='admin').id
        timezone.now()
        date = datetime(2000, 1, 1, tzinfo=pytz.UTC)

        voting_open = Voting(name='open voting', start_date=date)
        voting_open.save()
        census1 = Census(voter_id=voter_id, voting_id=voting_open.id)
        census1.save()

        voting_waiting = Voting(name='waiting voting', end_date=date)
        voting_waiting.save()
        census2 = Census(voter_id=voter_id, voting_id=voting_waiting.id)
        census2.save()

        voting_tally = Voting(name='tally voting', tally='{}')
        voting_tally.save()
        census3 = Census(voter_id=voter_id, voting_id=voting_tally.id)
        census3.save()


        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_indexPermissionCheck(self):
        '''
        Test that a non logged user cannot access index
        '''
        login_url = f'{self.live_server_url}{LOGIN_URL}'

        self.driver.get(f"{self.live_server_url}")
        url_value_after_get_index = self.driver.current_url
        self.driver.get(f"{self.live_server_url}/base")
        url_value_after_get_base = self.driver.current_url

        self.assertRegex(url_value_after_get_index,f'^{login_url}')
        self.assertRegex(url_value_after_get_base,f'^{login_url}')

    def test_indexNoVotingExist(self, user='noadmin', password='qwerty'):
        '''
        Test if the correct message is shown when the user has no votings associated via census
        '''
        open_msg='You do not have open votings'
        waiting_msg='You do not have votings waiting for result'
        previous_msg='You do not have votings to visualize'

        self.driver.get(f"{self.live_server_url}{LOGIN_URL}")
        self.driver.find_element(By.ID, "id_username").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password,Keys.ENTER)

        self.assertTrue(open_msg in self.driver.page_source, msg='Expected message "You do not have open votings"')
        self.assertTrue(waiting_msg in self.driver.page_source, msg='Expected message "You do not have votings waiting for result"')
        self.assertTrue(previous_msg in self.driver.page_source, msg='Expected message "You do not have votings to visualize"')


    def test_indexVotingsExist(self, user='admin', password='qwerty'):
        '''
        Test if votings are shown
        '''
        waiting_voting_name = 'waiting voting'

        self.driver.get(f"{self.live_server_url}{LOGIN_URL}")
        self.driver.find_element(By.ID, "id_username").send_keys(user)
        self.driver.find_element(By.ID, "id_password").send_keys(password,Keys.ENTER)

        try:
            vote_link = self.driver.find_element_by_link_text('Vote').get_attribute('href')
            result_link = self.driver.find_element_by_link_text('Results').get_attribute('href')

            self.assertRegex(vote_link,'\/booth\/[0-9]*', msg='Vote link does not match the pattern "\/booth\/[0-9]*"')
            self.assertRegex(result_link,'\/visualizer\/[0-9]*', msg='Results link does not match the pattern "\/visualizer\/[0-9]*"')
            self.assertTrue(waiting_voting_name in self.driver.page_source,msg='Voting waiting for result now found')
        except:
            self.assertRaises(NoSuchElementException,self.driver.find_element_by_link_text('Vote'), msg='Vote link not found')
            self.assertRaises(NoSuchElementException,self.driver.find_element_by_link_text('Results'), msg='Results link not found')

        