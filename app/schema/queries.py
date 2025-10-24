import strawberry
from typing import List, Optional
from app.models import Doctor, Department, OnboardingMetadata
from app.database import db
from app.schema.helpers import (
    build_complete_doctor,
    get_doctor_qualifications,
    get_doctor_address,
    get_doctor_appointment_settings,
    get_doctor_schedules,
    get_doctor_departments
)


@strawberry.type
class Query:

    @strawberry.field
    def departments(self) -> List[Department]:
        query = "SELECT id, name, icon_name FROM departments ORDER BY name"
        results = db.execute_query(query)
        print('results----',query, results, '\n\n')
        return [Department(**row) for row in results]
    
    @strawberry.field
    def search_departments(self, search: str) -> List[Department]:
    #Search departments by name 
        
        query = """
            SELECT id, name, icon_name FROM departments 
            WHERE LOWER(name) LIKE LOWER(%s)
            ORDER BY name
            """
        results = db.execute_query(query, (f'%{search}%',))
        
        print(results, 'serach results-----\n\n')
        
        return [Department(**row) for row in results]
    
    @strawberry.field
    def doctor(self, id: int) -> Optional[Doctor]:
        #doctor info with all the fields

        query = "SELECT * FROM doctors WHERE id = %s"
        result = db.execute_one(query, (id,))
        if not result:
            return None
        return build_complete_doctor(result)
    
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
            print('duplicate emai------',email)
            conditions.append("email = %s")
            params.append(email)

        if register_no:
            conditions.append("register_no = %s")
            params.append(register_no)
        
        query = f"SELECT * FROM doctors WHERE {' OR '.join(conditions)}"
        results = db.execute_query(query, tuple(params))
        # for row in results:
        #     print(row , '------multiple')
        return [build_complete_doctor(row) for row in results]
    
    @strawberry.field
    def onboarding_metadata(self, doctor_id: int) -> Optional[OnboardingMetadata]:
        print('doctor details is completed---------')

        query = "SELECT * FROM doctors WHERE id = %s"
        doctor = db.execute_one(query, (doctor_id,))
        if not doctor:
            return None
        
        completed_steps = [1]
        
        if doctor.get('name'):
            completed_steps.append(2)
        if get_doctor_qualifications(doctor_id):
            completed_steps.append(3)
        if get_doctor_address(doctor_id):
            completed_steps.append(4)
        if get_doctor_appointment_settings(doctor_id):
            completed_steps.append(5)
        if get_doctor_schedules(doctor_id):
            completed_steps.append(6)
        if get_doctor_departments(doctor_id):
            completed_steps.append(7)
        if doctor.get('profile_image_url'):
            completed_steps.append(8)
        
        return OnboardingMetadata(
            total_steps=8,
            completed_steps=completed_steps,
            current_step=doctor.get('current_step', 1),
            is_complete=doctor.get('onboarding_status') == 'completed'
        )
    
    @strawberry.field
    def all_doctors(self, status: Optional[str] = None) -> List[Doctor]:
        
        if status:
            query = "SELECT * FROM doctors WHERE onboarding_status = %s ORDER BY created_at DESC"
            results = db.execute_query(query, (status,))
        else:
            query = "SELECT * FROM doctors ORDER BY created_at DESC"
            results = db.execute_query(query)
        
        return [build_complete_doctor(row) for row in results]

