import os
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, Response, request
from models import init_db, db, Dog, Breed
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
    # Optional query parameters
    req_breed: Optional[str] = None
    req_status: Optional[str] = None
    if 'breed' in request.args:
        req_breed = request.args.get('breed')
    if 'status' in request.args:
        req_status = request.args.get('status')

    # Start base query
    query = db.session.query(
        Dog.id,
        Dog.name,
        Breed.name.label('breed'),
        Dog.status
    ).join(Breed, Dog.breed_id == Breed.id)

    # Apply breed filter if provided (case-sensitive matches breed name)
    if req_breed:
        query = query.filter(Breed.name == req_breed)

    # Apply status filter if provided; accept 'Available' or 'Adopted' (case-insensitive)
    if req_status:
        s = req_status.strip().lower()
        if s == 'available':
            query = query.filter(Dog.status == AdoptionStatus.AVAILABLE)
        elif s == 'adopted':
            query = query.filter(Dog.status == AdoptionStatus.ADOPTED)

    dogs_query = query.all()

    # Convert the result to a list of dictionaries
    dogs_list: List[Dict[str, Any]] = [
        {
            'id': dog.id,
            'name': dog.name,
            'breed': dog.breed,
            'status': dog.status.name if dog.status is not None else None
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

## HERE

if __name__ == '__main__':
    app.run(debug=True, port=5100) # Port 5100 to avoid macOS conflicts