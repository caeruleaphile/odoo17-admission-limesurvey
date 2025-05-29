from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta

class TestLimeSurveyConfig(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data
        self.open_date = datetime.now()
        self.close_date = self.open_date + timedelta(days=30)
        
        # Create a test form
        self.test_form = self.env['limesurvey.config'].create({
            'name': 'Bachelor 2025',
            'remote_id': 12,
            'form_type': 'student',
            'survey_url': 'https://survey.example.com/12',
            'open_date': self.open_date,
            'close_date': self.close_date,
        })

    def test_create_limesurvey_config_successfully(self):
        """Test the creation of a LimeSurvey configuration."""
        self.assertEqual(self.test_form.name, 'Bachelor 2025')
        self.assertEqual(self.test_form.remote_id, 12)
        self.assertEqual(self.test_form.form_type, 'student')
        self.assertEqual(self.test_form.survey_url, 'https://survey.example.com/12')
        self.assertEqual(self.test_form.open_date, self.open_date)
        self.assertEqual(self.test_form.close_date, self.close_date)
        self.assertTrue(self.test_form.active)
        self.assertFalse(self.test_form.connected)

    def test_limesurvey_config_connection_flag(self):
        """Test the connection simulation method."""
        self.assertFalse(self.test_form.connected)
        self.test_form.connect_to_limesurvey()
        self.assertTrue(self.test_form.connected) 