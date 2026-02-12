from django.urls import *
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Printer

class SeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Run in headless mode
        chrome_options.add_argument("--window-size=1280,720")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # expose driver/wait via instance for convenience
        self.driver = self.__class__.driver
        self.wait = self.__class__.wait

        self.user = User.objects.create_user("testuser", password="testpassword123")
        self.admin = User.objects.create_superuser("testadminuser", "admin@example.com", "testadminpassword123")
        
        # Create test printer data
        self.printer = Printer.objects.create(
            brand="Test Brand",
            model="Test Model",
            location="Test Location",
            ip_address="192.168.1.1",
            mac_address="00:1A:2B:3C:4D:5E",
            manufacture_date="2025-06-20",
            comments="Test comments"
        )

    def test_home_redirect_not_logged_in(self):
        self.driver.get(f"{self.live_server_url}/")
        self.wait.until(EC.url_contains("/login/"))
        self.assertIn("/login/", self.driver.current_url)

    def test_register_flow(self):
        self.driver.get(f"{self.live_server_url}/register/")
        self.wait.until(EC.url_matches(f"{self.live_server_url}/register/"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))).send_keys("testuser2")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_password1"))).send_keys("testpassword123")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_password2"))).send_keys("testpassword123")
        #self.driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpassword123")
        #self.driver.find_element(By.CSS_SELECTOR, "#id_confirm_password").send_keys("testpassword123")
        self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        # home page should load
        self.wait.until(EC.url_matches(f"{self.live_server_url}/"))
        # Wait for the page content to load
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("Printers List", self.driver.page_source)
        
    def test_logout(self):
        """Test user logout."""
        # log in
        self.driver.get(f"{self.live_server_url}/login/")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))).send_keys("testuser")
        self.driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpassword123")
        self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        #log out
        self.driver.get(f"{self.live_server_url}/")
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Log off"))).click()
        self.client.logout()
        response = self.client.get('/login/')
        self.assertNotContains(response, 'testuser')

    def test_login_flow(self):
        self.driver.get(f"{self.live_server_url}/login/")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))).send_keys("testuser")
        self.driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpassword123")
        self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        # home page should load
        self.wait.until(EC.url_matches(f"{self.live_server_url}/"))
        # Wait for the page content to load
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("Printers List", self.driver.page_source)

    def test_home_logged_in(self):
        """Tests the home page when the user is logged in.
            It should display the home page."""
        # log in
        self.driver.get(f"{self.live_server_url}/login/")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))).send_keys("testuser")
        self.driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpassword123")
        self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        # home page should load
        self.wait.until(EC.url_matches(f"{self.live_server_url}/"))
        # Wait for the page content to load
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("Printers List", self.driver.page_source)

    def test_admin_can_delete_printer(self):
        # log in as admin
        self.driver.get(f"{self.live_server_url}/login/")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))).send_keys("testadminuser")
        self.driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testadminpassword123")
        self.driver.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        # open delete modal for first printer
        delete_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".table tbody tr:first-child .fa-trash"))
        )
        delete_btn.click()
        confirm = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal.in .btn-primary"))
        )
        confirm.click()
        # assert it’s gone
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.in")))
        self.assertNotIn("Test Brand", self.driver.page_source)