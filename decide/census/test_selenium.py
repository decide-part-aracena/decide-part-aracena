from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase

class TestSearch(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_search(self):
        self.driver.get("http://127.0.0.1:8000/authentication/loginuser/?next=/base/")
        self.driver.set_window_size(923, 1016)
        self.driver.find_element(By.ID, "id_username").send_keys("juaalvcam")
        self.driver.find_element(By.ID, "id_password").send_keys("JuanjoUS2023")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get("http://127.0.0.1:8000/census/census/")
        self.driver.find_element(By.ID, "myInput").click()
        self.driver.find_element(By.ID, "myInput").send_keys("4")