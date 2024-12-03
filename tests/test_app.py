import unittest
from unittest.mock import patch
from app.main import app, db, ExamsLocations

class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up the Flask test client and test database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['MAIL_SUPPRESS_SEND'] = True  # Suppress email sending
        cls.client = app.test_client()

        # Initialize database
        with app.app_context():
            db.create_all()
            # Add sample data
            sample_exam = ExamsLocations(
                Exam_Component_ID=101,
                Title="Math Final",
                Date_of_Test="2024-12-15",
                Time_of_Test="10:00 AM",
                Building="Main Hall",
                Room="101",
                Instructor="Dr. Smith",
                class_name="MATH",
                class_level="101"
            )
            db.session.add(sample_exam)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        with app.app_context():
            db.drop_all()

    def test_get_exam_info_valid(self):
        # Valid input for `/get_exam_info`
        response = self.client.post('/get_exam_info', json=[
            {
                "Exam_Component_ID": 101,
                "class": "MATH",
                "class_level": "101"
            }
        ])
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Title'], "Math Final")

    def test_get_exam_info_no_results(self):
        # Input with no matching results
        response = self.client.post('/get_exam_info', json=[
            {
                "Exam_Component_ID": 999,
                "class": "SCIENCE",
                "class_level": "102"
            }
        ])
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertIn("No class was found", data[0]['message'])

    def test_send_exam_info_valid(self):
        # Valid input for `/send_exam_info`
        with patch('app.main.mail.send') as mock_mail_send:
            response = self.client.post('/send_exam_info', json={
                "email": "test@example.com",
                "exam_info": [
                    {
                        "Exam_Component_ID": 101,
                        "Title": "Math Final",
                        "Date_of_Test": "2024-12-15",
                        "Time_of_Test": "10:00 AM",
                        "Building": "Main Hall",
                        "Room": "101",
                        "Instructor": "Dr. Smith"
                    }
                ]
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn("Email sent successfully", response.get_json()['message'])
            mock_mail_send.assert_called_once()

    def test_send_exam_info_invalid_email(self):
        # Invalid input for `/send_exam_info`
        response = self.client.post('/send_exam_info', json={
            "email": "",
            "exam_info": []
        })
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

if __name__ == '__main__':
    unittest.main()
