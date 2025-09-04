# filepath: server/models/adoption_application.py
from datetime import datetime
from enum import Enum
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates

class ApplicationStatus(Enum):
    SUBMITTED = 'Submitted'
    UNDER_REVIEW = 'Under Review'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    COMPLETED = 'Completed'

class AdoptionApplication(BaseModel):
    __tablename__ = 'adoption_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable=False)
    
    # Contact information
    applicant_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Application details
    message = db.Column(db.Text, nullable=True)
    application_status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with Dog model
    dog = db.relationship('Dog', backref='adoption_applications')
    
    @validates('applicant_name')
    def validate_applicant_name(self, key, name):
        return self.validate_string_length('Applicant name', name, min_length=2)
    
    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError("Valid email address is required")
        return email.strip().lower()
    
    @validates('phone')
    def validate_phone(self, key, phone):
        if phone is not None:
            phone = phone.strip()
            if len(phone) > 0 and len(phone) < 10:
                raise ValueError("Phone number must be at least 10 digits")
        return phone
    
    @validates('message')
    def validate_message(self, key, message):
        return self.validate_string_length('Message', message, min_length=1, allow_none=True)
    
    def __repr__(self):
        return f'<AdoptionApplication {self.id}: {self.applicant_name} for Dog {self.dog_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dog_id': self.dog_id,
            'dog_name': self.dog.name if self.dog else None,
            'applicant_name': self.applicant_name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'application_status': self.application_status.value if self.application_status else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }