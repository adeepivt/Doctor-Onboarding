import strawberry
from typing import List, Optional
from app.models import Doctor
from app.services import DoctorService
from app.database import db

@strawberry.type
class DoctorQuery:

    @strawberry.field
    def doctor(self, id: int) -> Optional[Doctor]:
        query = "SELECT * FROM doctors WHERE id = %s"
        result = db.execute_one(query, (id,))
        if not result:
            return None
        return DoctorService.build_complete_doctor(result)
    
    @strawberry.field
    def check_registration(
        self,
        email: Optional[str] = None,
        register_no: Optional[str] = None
    ) -> List[Doctor]:
        if not email and not register_no:
            return []
        
        conditions = []
        params = []
        
        if email:
            conditions.append("email = %s")
            params.append(email)
        if register_no:
            conditions.append("register_no = %s")
            params.append(register_no)
        
        query = f"SELECT * FROM doctors WHERE {' OR '.join(conditions)}"
        results = db.execute_query(query, tuple(params))
        return [DoctorService.build_complete_doctor(row) for row in results]
    
    @strawberry.field
    def all_doctors(self, status: Optional[str] = None) -> List[Doctor]:
        if status:
            query = "SELECT * FROM doctors WHERE onboarding_status = %s ORDER BY created_at DESC"
            results = db.execute_query(query, (status,))
        else:
            query = "SELECT * FROM doctors ORDER BY created_at DESC"
            results = db.execute_query(query)
        return [DoctorService.build_complete_doctor(row) for row in results]
