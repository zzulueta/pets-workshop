import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Changed from relative import to absolute import

# filepath: server/test_app.py
class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a test client using Flask's test client
        self.app = app.test_client()
        self.app.testing = True
        # Turn off database initialization for tests
        app.config['TESTING'] = True
        # Create application context for tests
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        # Clean up application context
        self.app_context.pop()
        
    def _create_mock_dog(self, dog_id, name, breed):
        """Helper method to create a mock dog with standard attributes"""
        dog = MagicMock(spec=['to_dict', 'id', 'name', 'breed'])
        dog.id = dog_id
        dog.name = name
        dog.breed = breed
        dog.to_dict.return_value = {'id': dog_id, 'name': name, 'breed': breed}
        return dog
        
    def _setup_query_mock(self, mock_query, dogs):
        """Helper method to configure the query mock"""
        mock_query_instance = MagicMock()
        mock_query.return_value = mock_query_instance
        mock_query_instance.join.return_value = mock_query_instance
        mock_query_instance.all.return_value = dogs
        return mock_query_instance

    @patch('app.db.session.query')
    def test_get_dogs_success(self, mock_query):
        """Test successful retrieval of multiple dogs"""
        # Arrange
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador")
        dog2 = self._create_mock_dog(2, "Max", "German Shepherd")
        mock_dogs = [dog1, dog2]
        
        self._setup_query_mock(mock_query, mock_dogs)
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        # Verify first dog
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Buddy")
        self.assertEqual(data[0]['breed'], "Labrador")
        
        # Verify second dog
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "Max")
        self.assertEqual(data[1]['breed'], "German Shepherd")
        
        # Verify query was called
        mock_query.assert_called_once()
        
    @patch('app.db.session.query')
    def test_get_dogs_empty(self, mock_query):
        """Test retrieval when no dogs are available"""
        # Arrange
        self._setup_query_mock(mock_query, [])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])
        
    @patch('app.db.session.query')
    def test_get_dogs_structure(self, mock_query):
        """Test the response structure for a single dog"""
        # Arrange
        dog = self._create_mock_dog(1, "Buddy", "Labrador")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0].keys()), {'id', 'name', 'breed'})

    @patch('app.Breed')
    def test_get_breeds_success(self, mock_breed):
        """Test successful retrieval of breeds"""
        # Arrange
        breed1 = MagicMock()
        breed1.id = 1
        breed1.name = "Labrador Retriever"
        breed2 = MagicMock()
        breed2.id = 2
        breed2.name = "German Shepherd"
        
        mock_breed.query.all.return_value = [breed1, breed2]
        
        # Act
        response = self.app.get('/api/breeds')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], "Labrador Retriever")
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "German Shepherd")

    @patch('app.AdoptionApplication')
    def test_get_adoption_applications_empty(self, mock_app):
        """Test retrieval when no applications exist"""
        # Arrange
        mock_app.query.order_by.return_value.all.return_value = []
        
        # Act
        response = self.app.get('/api/applications')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    @patch('app.AdoptionApplication')
    def test_get_adoption_applications_success(self, mock_app):
        """Test successful retrieval of adoption applications"""
        # Arrange
        mock_application = MagicMock()
        mock_application.to_dict.return_value = {
            'id': 1,
            'dog_id': 2,
            'applicant_name': 'John Doe',
            'email': 'john@example.com',
            'application_status': 'Submitted'
        }
        mock_app.query.order_by.return_value.all.return_value = [mock_application]
        
        # Act
        response = self.app.get('/api/applications')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['applicant_name'], 'John Doe')

    @patch('app.AdoptionApplication')
    def test_get_adoption_application_by_id_success(self, mock_app):
        """Test successful retrieval of specific adoption application"""
        # Arrange
        mock_application = MagicMock()
        mock_application.to_dict.return_value = {
            'id': 1,
            'dog_id': 2,
            'applicant_name': 'John Doe',
            'email': 'john@example.com',
            'application_status': 'Submitted'
        }
        mock_app.query.get.return_value = mock_application
        
        # Act
        response = self.app.get('/api/applications/1')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['applicant_name'], 'John Doe')

    @patch('app.AdoptionApplication')
    def test_get_adoption_application_by_id_not_found(self, mock_app):
        """Test retrieval of non-existent adoption application"""
        # Arrange
        mock_app.query.get.return_value = None
        
        # Act
        response = self.app.get('/api/applications/999')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Application not found')

    @patch('app.db.session')
    @patch('app.Dog')
    def test_submit_adoption_application_success(self, mock_dog, mock_db_session):
        """Test successful submission of adoption application"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog_instance = MagicMock()
        mock_dog_instance.status = AdoptionStatus.AVAILABLE
        mock_dog.query.get.return_value = mock_dog_instance
        
        # Act
        response = self.app.post('/api/dogs/1/adopt', 
                               data=json.dumps({
                                   'applicant_name': 'Jane Smith',
                                   'email': 'jane@example.com',
                                   'phone': '555-123-4567',
                                   'message': 'I love this dog!'
                               }),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Adoption application submitted successfully')
        self.assertIn('application_id', data)

    @patch('app.Dog')
    def test_submit_adoption_application_dog_not_found(self, mock_dog):
        """Test submission for non-existent dog"""
        # Arrange
        mock_dog.query.get.return_value = None
        
        # Act
        response = self.app.post('/api/dogs/999/adopt', 
                               data=json.dumps({
                                   'applicant_name': 'Jane Smith',
                                   'email': 'jane@example.com'
                               }),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Dog not found')

    @patch('app.Dog')
    def test_submit_adoption_application_dog_not_available(self, mock_dog):
        """Test submission for dog that's not available"""
        # Arrange
        from models.dog import AdoptionStatus
        mock_dog_instance = MagicMock()
        mock_dog_instance.status = AdoptionStatus.ADOPTED
        mock_dog.query.get.return_value = mock_dog_instance
        
        # Act
        response = self.app.post('/api/dogs/1/adopt', 
                               data=json.dumps({
                                   'applicant_name': 'Jane Smith',
                                   'email': 'jane@example.com'
                               }),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Dog is not available for adoption')

    def test_submit_adoption_application_missing_required_fields(self):
        """Test submission with missing required fields"""
        # Act
        response = self.app.post('/api/dogs/1/adopt', 
                               data=json.dumps({
                                   'applicant_name': 'Jane Smith'
                                   # Missing email
                               }),
                               content_type='application/json')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'email is required')

    def test_submit_adoption_application_no_json_body(self):
        """Test submission without JSON body"""
        # Act
        response = self.app.post('/api/dogs/1/adopt')
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'JSON body required')


if __name__ == '__main__':
    unittest.main()