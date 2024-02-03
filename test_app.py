import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a test client
        self.app = app.test_client()

    def tearDown(self):
        # Clean up resources after testing
        pass

    def test_index_page(self):
        # Test the index page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Crop Disease Diagnosis and Management', response.data)

    def test_plant_names_endpoint(self):
        # Test the /plant_names endpoint
        response = self.app.get('/plant_names')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('plant_names', data)
        # Add more assertions to check the correctness of plant names data

    def test_plant_symptoms_endpoint(self):
        # Test the /plant_symptoms/<plant> endpoint
        response = self.app.get('/plant_symptoms/beans')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('plant_symptoms', data)
        # Add more assertions to check the correctness of symptoms for maize

    def test_match_diseases_endpoint(self):
        # Test the /match_diseases endpoint
        data = {'selected_symptoms': ['yellowing leaves', 'stunted growth']}
        response = self.app.post('/match_diseases', json=data)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('matched_diseases', data)
        # Add more assertions to check the correctness of matched diseases data

    def test_save_excel_endpoint(self):
        # Test the /save_excel endpoint
        response = self.app.get('/save_excel')
        self.assertEqual(response.status_code, 200)
        # Add more assertions to check the correctness of generated Excel file

if __name__ == '__main__':
    unittest.main()
