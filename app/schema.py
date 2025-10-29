import strawberry
from typing import List, Optional
from app.models import (
    Doctor, Department, Address, AppointmentSettings, Schedule,
    OnboardingMetadata, AddressInput, AppointmentSettingsInput, ScheduleInput
)
from app.database import db


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_doctor_mobile_numbers(doctor_id: int) -> List[str]:
    """Fetch mobile numbers for a doctor"""
    query = "SELECT mobile_number FROM doctor_mobile_numbers WHERE doctor_id = %s"
    results = db.execute_query(query, (doctor_id,))
    return [row['mobile_number'] for row in results]


def get_doctor_departments(doctor_id: int) -> List[Department]:
    """Fetch departments for a doctor"""
    query = """
        SELECT d.id, d.name, d.icon_name
        FROM departments d
        JOIN doctor_departments dd ON d.id = dd.department_id
        WHERE dd.doctor_id = %s
    """
    results = db.execute_query(query, (doctor_id,))
    return [Department(**row) for row in results]


def get_doctor_qualifications(doctor_id: int) -> List[str]:
    """Fetch qualifications for a doctor"""
    query = "SELECT qualification FROM qualifications WHERE doctor_id = %s"
    results = db.execute_query(query, (doctor_id,))
    return [row['qualification'] for row in results]


def get_doctor_specializations(doctor_id: int) -> List[str]:
    """Fetch specializations for a doctor"""
    query = "SELECT specialization FROM specializations WHERE doctor_id = %s"
    results = db.execute_query(query, (doctor_id,))
    return [row['specialization'] for row in results]


def get_doctor_address(doctor_id: int) -> Optional[Address]:
    
    query = """SELECT id, country, state, city, pincode, flat_house, latitude, longitude
        FROM addresses WHERE doctor_id = %s"""
    
    result = db.execute_one(query, (doctor_id,))

    return Address(**result) if result else None


def get_doctor_appointment_settings(doctor_id: int) -> Optional[AppointmentSettings]:
    """Fetch appointment settings for a doctor"""
    # query = "SELECT * FROM appointment_settings WHERE doctor_id = %s"
    query = """
            SELECT id, consultation_charge, follow_up_charge, follow_up_period_days,
               advance_booking_days, avg_duration_minutes
            FROM appointment_settings WHERE doctor_id = %s
        """
            
    result = db.execute_one(query, (doctor_id,))
    print(result, 'rrrrrrresult doctor appontment update')
    return AppointmentSettings(**result) if result else None


def get_doctor_schedules(doctor_id: int) -> List[Schedule]:
    """Fetch schedules for a doctor"""
    query = """
        SELECT id, day_of_week, start_time::text, end_time::text, is_available
        FROM schedules WHERE doctor_id = %s ORDER BY day_of_week
    """
    results = db.execute_query(query, (doctor_id,))
    return [Schedule(**row) for row in results]


def build_complete_doctor(doctor_data: dict) -> Doctor:
    
    doctor_id = doctor_data['id']
    print('inside build complete------\n\n', doctor_id)

    return Doctor(
        id=doctor_data['id'],
        name=doctor_data.get('name'),
        email=doctor_data.get('email'),
        mobile_numbers=get_doctor_mobile_numbers(doctor_id),  # CHANGED
        register_no=doctor_data.get('register_no'),
        bio=doctor_data.get('bio'),
        profile_image_url=doctor_data.get('profile_image_url'),
        onboarding_status=doctor_data.get('onboarding_status', 'in_progress'),
        current_step=doctor_data.get('current_step', 1),
        departments=get_doctor_departments(doctor_id),
        qualifications=get_doctor_qualifications(doctor_id),
        specializations=get_doctor_specializations(doctor_id),
        address=get_doctor_address(doctor_id),
        appointment_settings=get_doctor_appointment_settings(doctor_id),
        schedules=get_doctor_schedules(doctor_id),
        created_at=doctor_data.get('created_at'),
        updated_at=doctor_data.get('updated_at')
    )


@strawberry.type
class Query:

    @strawberry.field #tested
    def departments(self) -> List[Department]:
        query = "SELECT id, name, icon_name FROM departments ORDER BY name"
        results = db.execute_query(query)
        print('results----',query, results, '\n\n')
        return [Department(**row) for row in results]
    
    @strawberry.field #tested
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
    
    @strawberry.field #tested
    def doctor(self, id: int) -> Optional[Doctor]:
        #doctor info with all the fields

        query = "SELECT * FROM doctors WHERE id = %s"
        result = db.execute_one(query, (id,))
        if not result:
            return None
        return build_complete_doctor(result)
    
    @strawberry.field #tested
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
    
    @strawberry.field #tested
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
    
    @strawberry.field #tested
    def all_doctors(self, status: Optional[str] = None) -> List[Doctor]:
        
        if status:
            query = "SELECT * FROM doctors WHERE onboarding_status = %s ORDER BY created_at DESC"
            results = db.execute_query(query, (status,))
        else:
            query = "SELECT * FROM doctors ORDER BY created_at DESC"
            results = db.execute_query(query)
        
        return [build_complete_doctor(row) for row in results]


# ============================================
# MUTATIONS
# ============================================

@strawberry.type
class Mutation:

    @strawberry.mutation #tested
    def start_onboarding(
        self, 
        register_no: str, 
        email: str, 
        mobile_numbers: List[str]
    ) -> Doctor:
        
        check_query = "SELECT id FROM doctors WHERE email = %s OR register_no = %s"
        
        existing = db.execute_one(check_query, (email, register_no))
        
        if existing:
            raise ValueError("Doctor already registered")
        
    
        query = """
            INSERT INTO doctors (register_no, email, current_step)
            VALUES (%s, %s, 1) RETURNING *
        """
        result = db.execute_mutation(query, (register_no, email))
        doctor_id = result['id']
        
        print(mobile_numbers,'multiple mobilesn umbersssss\n')
        if mobile_numbers:
            
            mobile_query = """
                        INSERT INTO doctor_mobile_numbers (doctor_id, mobile_number)
                        VALUES (%s, %s)
                    """
            db.execute_batch(mobile_query, [(doctor_id, mobile) for mobile in mobile_numbers])
        
        return build_complete_doctor(result)
    
    @strawberry.mutation # tested
    def update_doctor_name(self, doctor_id: int, name: str) -> Doctor:
        

        query = """
            UPDATE doctors SET name = %s, current_step = GREATEST(current_step, 2),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """

        result = db.execute_mutation(query, (name, doctor_id))
        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        return build_complete_doctor(result)
    
    @strawberry.mutation # tested
    def update_qualifications_and_bio(
        self, doctor_id: int, qualifications: List[str],
        specializations: List[str], bio: Optional[str] = None
    ) -> Doctor:
        
        query = """
            UPDATE doctors SET bio = %s, current_step = GREATEST(current_step, 3),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (bio, doctor_id))
        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        
        db.execute_mutation("DELETE FROM qualifications WHERE doctor_id = %s", (doctor_id,))
        db.execute_mutation("DELETE FROM specializations WHERE doctor_id = %s", (doctor_id,))
        
        if qualifications:
            qual_query = "INSERT INTO qualifications (doctor_id, qualification) VALUES (%s, %s)"
            db.execute_batch(qual_query, [(doctor_id, q) for q in qualifications])
        
        if specializations:
            spec_query = "INSERT INTO specializations (doctor_id, specialization) VALUES (%s, %s)"
            db.execute_batch(spec_query, [(doctor_id, s) for s in specializations])
        
        return build_complete_doctor(result)
    
    @strawberry.mutation #testd
    def update_address(self, doctor_id: int, address_input: AddressInput) -> Doctor:
        

        check = db.execute_one("SELECT id FROM addresses WHERE doctor_id = %s", (doctor_id,))
        
        if check:
            query = """
                UPDATE addresses SET country = %s, state = %s, city = %s, pincode = %s,
                flat_house = %s, latitude = %s, longitude = %s WHERE doctor_id = %s
            """
            db.execute_mutation(query, (
                address_input.country, address_input.state, address_input.city,
                address_input.pincode, address_input.flat_house,
                address_input.latitude, address_input.longitude, doctor_id
            ))
        else:
            query = """
                INSERT INTO addresses (doctor_id, country, state, city, pincode, flat_house, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_mutation(query, (
                doctor_id, address_input.country, address_input.state, address_input.city,
                address_input.pincode, address_input.flat_house,
                address_input.latitude, address_input.longitude
            ))
        
        query = """
            UPDATE doctors SET current_step = GREATEST(current_step, 4),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (doctor_id,))
        return build_complete_doctor(result)
    
    @strawberry.mutation #testes
    def update_appointment_settings(
        self, doctor_id: int, settings: AppointmentSettingsInput
    ) -> Doctor:
        
        check = db.execute_one("SELECT id FROM appointment_settings WHERE doctor_id = %s", (doctor_id,))
        
        if check:
            print('inside if ffffffffff]\n\n')
            query = """
                UPDATE appointment_settings SET consultation_charge = %s, follow_up_charge = %s,
                follow_up_period_days = %s, advance_booking_days = %s, avg_duration_minutes = %s
                WHERE doctor_id = %s
            """
            db.execute_mutation(query, (
                settings.consultation_charge, settings.follow_up_charge,
                settings.follow_up_period_days, settings.advance_booking_days,
                settings.avg_duration_minutes, doctor_id
            ))
        else:
            print('not found exisitng appointment details----')
            query = """
                INSERT INTO appointment_settings
                (doctor_id, consultation_charge, follow_up_charge, follow_up_period_days,
                 advance_booking_days, avg_duration_minutes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_mutation(query, (
                doctor_id, settings.consultation_charge, settings.follow_up_charge,
                settings.follow_up_period_days, settings.advance_booking_days,
                settings.avg_duration_minutes
            ))
        
        query = """
            UPDATE doctors SET current_step = GREATEST(current_step, 5),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (doctor_id,))
        return build_complete_doctor(result)
    
    @strawberry.mutation #tested
    def update_schedule(self, doctor_id: int, schedules: List[ScheduleInput]) -> Doctor:
        
        db.execute_mutation("DELETE FROM schedules WHERE doctor_id = %s", (doctor_id,))
        
        if schedules:
            query = """
                INSERT INTO schedules (doctor_id, day_of_week, start_time, end_time, is_available)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.execute_batch(query, [
                (doctor_id, s.day_of_week, s.start_time, s.end_time, s.is_available)
                for s in schedules
            ])
        
        query = """
            UPDATE doctors SET current_step = GREATEST(current_step, 6),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (doctor_id,))
        return build_complete_doctor(result)
    
    @strawberry.mutation #tested
    def add_departments(self, doctor_id: int, department_ids: List[int]) -> Doctor:
        
        db.execute_mutation("DELETE FROM doctor_departments WHERE doctor_id = %s", (doctor_id,))
        
        if department_ids:
            query = "INSERT INTO doctor_departments (doctor_id, department_id) VALUES (%s, %s)"
            db.execute_batch(query, [(doctor_id, dept_id) for dept_id in department_ids])
        
        query = """
            UPDATE doctors SET current_step = GREATEST(current_step, 7),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        
        print('update query')
        result = db.execute_mutation(query, (doctor_id,))
        return build_complete_doctor(result)
    
    @strawberry.mutation #tested
    def update_profile_image(self, doctor_id: int, image_url: str) -> Doctor:
        
        print('imageurl', image_url)

        query = """
            UPDATE doctors SET profile_image_url = %s, current_step = GREATEST(current_step, 8),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (image_url, doctor_id))
        
        print('not getting reult image,\n\n')

        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        return build_complete_doctor(result)
    
    @strawberry.mutation #tested
    def complete_onboarding(self, doctor_id: int) -> Doctor:
        print('status completed--------')
        
        query = """
            UPDATE doctors SET onboarding_status = 'completed',
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """
        result = db.execute_mutation(query, (doctor_id,))
        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        
        return build_complete_doctor(result)


schema = strawberry.Schema(query=Query, mutation=Mutation)
