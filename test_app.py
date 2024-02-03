import unittest
from app import app
import time

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index_page(self):
        start_time = time.time()
        response = self.app.get('/')
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Crop Disease Diagnosis and Management', response.data)
        print("Test test_index_page took", end_time - start_time, "seconds")

    def test_plant_names_endpoint(self):
        start_time = time.time()
        response = self.app.get('/plant_names')
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('plant_names', data)
        print("Test test_plant_names_endpoint took", end_time - start_time, "seconds")

    def test_plant_symptoms_endpoint(self):
        start_time = time.time()
        response = self.app.get('/plant_symptoms/beans')
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('plant_symptoms', data)
        print("Test test_plant_symptoms_endpoint took", end_time - start_time, "seconds")

    def test_match_diseases_endpoint(self):
        start_time = time.time()
        data = {'selected_symptoms': ['yellowing leaves', 'stunted growth']}
        response = self.app.post('/match_diseases', json=data)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('matched_diseases', data)
        print("Test test_match_diseases_endpoint took", end_time - start_time, "seconds")

    def test_save_excel_endpoint(self):
        start_time = time.time()
        response = self.app.get('/save_excel')
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        print("Test test_save_excel_endpoint took", end_time - start_time, "seconds")

if __name__ == '__main__':
    unittest.main()
