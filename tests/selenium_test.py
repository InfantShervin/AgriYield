import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class AgriYieldE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Run in headless mode for CI/CD
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        # Determine URL
        cls.base_url = os.getenv("APP_URL", "http://localhost:3000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_page_title(self):
        self.driver.get(self.base_url)
        self.assertIn("AgriYield", self.driver.title)

    def test_full_prediction_flow(self):
        self.driver.get(self.base_url)
        
        # Fill in the form
        self.driver.find_element(By.ID, "temperature").clear()
        self.driver.find_element(By.ID, "temperature").send_keys("28.5")
        
        self.driver.find_element(By.ID, "humidity").clear()
        self.driver.find_element(By.ID, "humidity").send_keys("75")
        
        self.driver.find_element(By.ID, "precipitation").clear()
        self.driver.find_element(By.ID, "precipitation").send_keys("150")
        
        self.driver.find_element(By.ID, "soil_ph").clear()
        self.driver.find_element(By.ID, "soil_ph").send_keys("6.5")
        
        self.driver.find_element(By.ID, "soil_nutrients").clear()
        self.driver.find_element(By.ID, "soil_nutrients").send_keys("120")
        
        self.driver.find_element(By.ID, "latitude").clear()
        self.driver.find_element(By.ID, "latitude").send_keys("20.5")
        
        self.driver.find_element(By.ID, "longitude").clear()
        self.driver.find_element(By.ID, "longitude").send_keys("78.5")
        
        # Click Predict Button
        predict_btn = self.driver.find_element(By.ID, "predictBtn")
        predict_btn.click()
        
        # Wait for results to appear
        time.sleep(3)
        
        result_card = self.driver.find_element(By.ID, "resultCard")
        self.assertTrue(result_card.is_displayed(), "Result card should be visible after prediction")
        
        yield_val = self.driver.find_element(By.ID, "yieldValue").text
        print(f"DEBUG: Predicted Yield: {yield_val}")
        self.assertNotEqual(yield_val, "0.00", "Yield value should be updated from default 0.00")

if __name__ == "__main__":
    unittest.main()
