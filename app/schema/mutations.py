import strawberry
from typing import List, Optional
from app.models import Doctor, AddressInput, AppointmentSettingsInput, ScheduleInput
from app.database import db
from app.schema.helpers import build_complete_doctor

@strawberry.type
class Mutation:

    @strawberry.mutation
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
    
    @strawberry.mutation
    def update_doctor_name(self, doctor_id: int, name: str) -> Doctor:
        

        query = """
            UPDATE doctors SET name = %s, current_step = GREATEST(current_step, 2),
            updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *
        """

        result = db.execute_mutation(query, (name, doctor_id))
        if not result:
            raise ValueError(f"Doctor {doctor_id} not found")
        return build_complete_doctor(result)
    
    @strawberry.mutation
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
    
    @strawberry.mutation 
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
    
    @strawberry.mutation
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
    
    @strawberry.mutation
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
    
    @strawberry.mutation
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
    
    @strawberry.mutation 
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
    
    @strawberry.mutation 
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

