from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from .models import Census

from base.tests import BaseTestCase

class TestSelenium(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        for i in range(7):
            census = Census(voting_id = i+1, voter_id = i +4)
            census.save()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_search(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("juaalvcam")
        self.driver.find_element(By.ID, "id_password").send_keys("JuanjoUS2023")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+"/census/census/")
        self.driver.find_element(By.ID, "myInput").click()
        self.driver.find_element(By.ID, "myInput").send_keys("4")
        self.driver.get(self.live_server_url+"/census/census/")

    def test_pagina_2(self):
        self.driver.get(self.live_server_url+"/authentication/loginuser/?next=/base/")
        self.driver.find_element(By.ID, "id_username").send_keys("juaalvcam")
        self.driver.find_element(By.ID, "id_password").send_keys("JuanjoUS2023")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.driver.get(self.live_server_url+"/census/census/")
        self.driver.get(self.live_server_url+"/census/census/?page=2#pagtable")
        self.assertTrue(self.live_server_url+"/census/census/?page=2#pagtable"==self.driver.current_url)
