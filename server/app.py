import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request
from models import init_db, db, Dog, Breed, AdoptionApplication
from models.dog import AdoptionStatus

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "dogshelter.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db(app)

@app.route('/api/dogs', methods=['GET'])
def get_dogs() -> Response:
    query = db.session.query(
        Dog.id, 
        Dog.name, 
        Breed.name.label('breed')
    ).join(Breed, Dog.breed_id == Breed.id)
    
    dogs_query = query.all()
    
    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed
        }
        for dog in dogs_query
    ]
    
    return jsonify(dogs_list)

@app.route('/api/dogs/<int:id>', methods=['GET'])
def get_dog(id: int) -> tuple[Response, int] | Response:
    # Query the specific dog by ID and join with breed to get breed name
    dog_query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.age,
        Dog.description,
        Dog.gender,
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id).filter(Dog.id == id).first()
    
    # Return 404 if dog not found
    if not dog_query:
        return jsonify({"error": "Dog not found"}), 404
    
    # Convert the result to a dictionary
    dog: Dict[str, Any] = {
        'id': dog_query.id,
        'name': dog_query.name,
        'breed': dog_query.breed,
        'age': dog_query.age,
        'description': dog_query.description,
        'gender': dog_query.gender,
        'status': dog_query.status.name
    }
    
    return jsonify(dog)

@app.route('/api/breeds', methods=['GET'])
def get_breeds() -> Response:
    """
    Retrieves all pet breeds from the database and returns them as a JSON response.
    Returns:
        Response: A Flask JSON response containing a list of dictionaries,
                  each representing a breed with 'id' and 'name' keys.
    """
    breeds_query = Breed.query.all()
    
    # Convert the result to a list of dictionaries
    breeds_list: List[Dict[str, Any]] = [
        {
            'id': breed.id,
            'name': breed.name
        }
        for breed in breeds_query
    ]
    
    return jsonify(breeds_list)

@app.route('/api/dogs/<int:dog_id>/adopt', methods=['POST'])
def submit_adoption_application(dog_id: int) -> tuple[Response, int] | Response:
    """
    Submit an adoption application for a specific dog.
    Expects JSON body with: applicant_name, email, phone (optional), message (optional)
    """
    try:
        # Validate that the dog exists
        dog = Dog.query.get(dog_id)
        if not dog:
            return jsonify({"error": "Dog not found"}), 404
        
        # Check if dog is available for adoption
        if dog.status != AdoptionStatus.AVAILABLE:
            return jsonify({"error": "Dog is not available for adoption"}), 400
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        # Validate required fields
        required_fields = ['applicant_name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400
        
        # Create adoption application
        application = AdoptionApplication(
            dog_id=dog_id,
            applicant_name=data['applicant_name'],
            email=data['email'],
            phone=data.get('phone'),
            message=data.get('message')
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            "message": "Adoption application submitted successfully",
            "application_id": application.id,
            "application": application.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit application"}), 500

@app.route('/api/applications', methods=['GET'])
def get_adoption_applications() -> Response:
    """
    Get all adoption applications for shelter staff to review.
    """
    try:
        applications = AdoptionApplication.query.order_by(AdoptionApplication.submitted_at.desc()).all()
        
        applications_list: List[Dict[str, Any]] = [
            app.to_dict() for app in applications
        ]
        
        return jsonify(applications_list)
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve applications"}), 500

@app.route('/api/applications/<int:application_id>', methods=['GET'])
def get_adoption_application(application_id: int) -> tuple[Response, int] | Response:
    """
    Get a specific adoption application by ID.
    """
    try:
        application = AdoptionApplication.query.get(application_id)
        if not application:
            return jsonify({"error": "Application not found"}), 404
            
        return jsonify(application.to_dict())
        
    except Exception as e:
        return jsonify({"error": "Failed to retrieve application"}), 500

## HERE

if __name__ == '__main__':
    app.run(debug=True, port=5100) # Port 5100 to avoid macOS conflicts