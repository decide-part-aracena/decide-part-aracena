from rest_framework.test import APIClient
from base import mods
from selenium import webdriver
from selenium.webdriver.common.by import By
from base.tests import BaseTestCase
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

class TestUsers(StaticLiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()
        mods.mock_query(self.client)
        
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        self.client = None
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
    
    def test_new_user_positive(self):
        '''Test if an administrator can create a valid user'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.ID, "newUser").click()
        self.assertTrue(self.live_server_url+"/authentication/registeruser/" == self.driver.current_url)
        
        self.driver.find_element(By.ID, "id_username").send_keys("Josdelsan9")
        self.driver.find_element(By.ID, "id_first_name").send_keys("Jose Maria")
        self.driver.find_element(By.ID, "id_last_name").send_keys("Delgado")
        self.driver.find_element(By.ID, "id_email").send_keys("josdelsan9@gmail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("fire1234")
        self.driver.find_element(By.ID, "id_password2").send_keys("fire1234", Keys.ENTER)
        self.assertTrue(self.live_server_url+"/users/" == self.driver.current_url)

        self.driver.find_element(By.ID, "myInput").send_keys("Josdelsan9", Keys.ENTER)

    def test_new_user_already_exists(self):
        '''Test if an administrator can create an user that already exists'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.ID, "newUser").click()
        self.assertTrue(self.live_server_url+"/authentication/registeruser/" == self.driver.current_url)
        
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_first_name").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_last_name").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_email").send_keys("noadmin@gmail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("fire1noadmin234")
        self.driver.find_element(By.ID, "id_password2").send_keys("fire1noadmin234", Keys.ENTER)
        self.assertTrue(self.live_server_url+"/authentication/registeruser/" 
            == self.driver.current_url)

    def test_new_user_negative(self):
        '''Test if an administrator can create an user that has no good attributes'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.ID, "newUser").click()
        self.assertTrue(self.live_server_url+"/authentication/registeruser/" == self.driver.current_url)
        
        self.driver.find_element(By.ID, "id_username").send_keys("")
        self.driver.find_element(By.ID, "id_first_name").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_last_name").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_email").send_keys("notanemail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("short")
        self.driver.find_element(By.ID, "id_password2").send_keys("short", Keys.ENTER)
        self.assertTrue(self.live_server_url+"/authentication/registeruser/" 
            == self.driver.current_url)
    
    def test_edit_user_positive(self):
        '''Test if an administrator can edit a valid user'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.LINK_TEXT, "Edit").click()
        
        self.driver.find_element(By.ID, "id_first_name").send_keys("noadmin 2")
        self.driver.find_element(By.ID, "id_email").send_keys("noadmin9@gmail.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(7)").click()

        firstname = self.driver.find_element(By.ID, "id_first_name")
        self.assertTrue(firstname.get_attribute("value") == "noadmin 2")
        email = self.driver.find_element(By.ID, "id_email")
        self.assertTrue(email.get_attribute("value") == "noadmin9@gmail.com")
    
    def test_edit_user_negative(self):
        '''Test if an administrator can edit an invalid user'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.LINK_TEXT, "Edit").click()
        
        self.driver.find_element(By.ID, "id_email").send_keys("nomail.com")
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(7)").click()

        self.driver.find_element(By.LINK_TEXT, "Back to list").click()
        self.driver.find_element(By.LINK_TEXT, "Edit").click()
        email = self.driver.find_element(By.ID, "id_email")
        self.assertTrue(email.get_attribute("value") == "")

    def test_delete_user(self):
        '''Test if an administrator can delete an user'''
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/")
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        
        self.driver.get(self.live_server_url+"/users")
        self.driver.find_element(By.LINK_TEXT, "Delete").click()
        
        self.driver.switch_to.alert.accept()
        self.assertTrue(self.live_server_url+"/users/" == self.driver.current_url)

class TestUsersModel(StaticLiveServerTestCase):

    def setUp(self):
        self.users = User(email = "testuseremail@email.com", username= "TestUser", password="complexpassword")
        self.users.save()

    def tearDown(self):
        self.users = None
        super().tearDown()

    def test_stored_user(self):
        self.assertEqual(User.objects.count(),1)
    
    def test_delete_user(self):
        self.users.delete()
        self.assertEqual(User.objects.count(),0)
    
    def test_update_user(self):
        user = User.objects.first()
        user.username = "NewUser"
        user.save()
        self.assertEqual(User.objects.first().__getattribute__('username'),"NewUser")
        self.assertNotEqual(User.objects.first().__getattribute__('username'),"TestUser")
    
    def test_create_user(self):
        user = User.objects.create_superuser("ImNewHere", "thisis@valid.email", "newpass"),
        User.objects.create_user("notAdmin", "butvalid@email.com", "andpass")
        self.users = self.users , user
        self.assertEqual(User.objects.count(),3)
        self.assertEqual(User.objects.first().__getattribute__('username'),"TestUser")
        first_user = User.objects.get(email="thisis@valid.email")
        second_user = User.objects.get(username="notAdmin")
        self.assertEqual(first_user.__getattribute__('username'),"ImNewHere")
        self.assertEqual(first_user.__getattribute__('is_staff'),True)
        self.assertEqual(second_user.__getattribute__('email'),"butvalid@email.com")
        self.assertEqual(second_user.__getattribute__('is_staff'),False)