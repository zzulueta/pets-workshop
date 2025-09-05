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
        
    def _create_mock_dog(self, dog_id, name, breed, age=None, gender=None, description=None, status=None):
        """Helper method to create a mock dog with standard attributes"""
        dog = MagicMock(spec=['to_dict', 'id', 'name', 'breed', 'age', 'gender', 'description', 'status'])
        dog.id = dog_id
        dog.name = name
        dog.breed = breed
        dog.age = age
        dog.gender = gender
        dog.description = description
        dog.status = MagicMock()
        dog.status.name = status or 'AVAILABLE'
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
        dog1 = self._create_mock_dog(1, "Buddy", "Labrador", age=3, gender="Male", description="Friendly dog", status="AVAILABLE")
        dog2 = self._create_mock_dog(2, "Max", "German Shepherd", age=5, gender="Male", description="Smart dog", status="AVAILABLE")
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
        self.assertEqual(data[0]['age'], 3)
        self.assertEqual(data[0]['gender'], "Male")
        self.assertEqual(data[0]['description'], "Friendly dog")
        self.assertEqual(data[0]['status'], "AVAILABLE")
        
        # Verify second dog
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], "Max")
        self.assertEqual(data[1]['breed'], "German Shepherd")
        self.assertEqual(data[1]['age'], 5)
        self.assertEqual(data[1]['gender'], "Male")
        self.assertEqual(data[1]['description'], "Smart dog")
        self.assertEqual(data[1]['status'], "AVAILABLE")
        
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
        dog = self._create_mock_dog(1, "Buddy", "Labrador", age=3, gender="Male", description="Friendly dog", status="AVAILABLE")
        self._setup_query_mock(mock_query, [dog])
        
        # Act
        response = self.app.get('/api/dogs')
        
        # Assert
        data = json.loads(response.data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0].keys()), {'id', 'name', 'breed', 'age', 'gender', 'description', 'status'})


if __name__ == '__main__':
    unittest.main()