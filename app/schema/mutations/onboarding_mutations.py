import strawberry
from app.models import Doctor
from app.services import DoctorService
from app.database import db

@strawberry.type
class OnboardingMutation:

    @strawberry.mutation 
    def complete_onboarding(self, doctor_id: int) -> Doctor:
        query = """
            UPDATE doctors SET onboarding_status = 'completed',
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (doctor_id,))
        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        return DoctorService.build_complete_doctor(result)
