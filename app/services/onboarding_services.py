from typing import Optional, List
from app.models import OnboardingMetadata
from app.database import db
from app.services.doctor_services import DoctorService

class OnboardingService:
    @staticmethod
    def get_onboarding_metadata(doctor_id: int) -> Optional[OnboardingMetadata]:
        query = "SELECT * FROM doctors WHERE id = %s"
        doctor = db.execute_one(query, (doctor_id,))
        if not doctor:
            return None
        
        completed_steps: List[int] = [1]
        
        if doctor.get('name'):
            completed_steps.append(2)
        if DoctorService.get_qualifications(doctor_id):
            completed_steps.append(3)
        if DoctorService.get_address(doctor_id):
            completed_steps.append(4)
        if DoctorService.get_appointment_settings(doctor_id):
            completed_steps.append(5)
        if DoctorService.get_schedules(doctor_id):
            completed_steps.append(6)
        if DoctorService.get_departments(doctor_id):
            completed_steps.append(7)
        if doctor.get('profile_image_url'):
            completed_steps.append(8)
        
        return OnboardingMetadata(
            total_steps=8,
            completed_steps=completed_steps,
            current_step=doctor.get('current_step', 1),
            is_complete=doctor.get('onboarding_status') == 'completed'
        )
