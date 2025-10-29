from typing import List, Optional, Dict
from app.models import Doctor
from app.database import db
from app.models import Department, Address, AppointmentSettings, Schedule

class DoctorService:
    @staticmethod
    def get_mobile_numbers(doctor_id: int) -> List[str]:
        query = "SELECT mobile_number FROM doctor_mobile_numbers WHERE doctor_id = %s"
        results = db.execute_query(query, (doctor_id,))
        return [row['mobile_number'] for row in results]

    @staticmethod
    def get_departments(doctor_id: int) -> List[Department]:
        query = """
            SELECT d.id, d.name, d.icon_name
            FROM departments d
            JOIN doctor_departments dd ON d.id = dd.department_id
            WHERE dd.doctor_id = %s
        """
        results = db.execute_query(query, (doctor_id,))
        return [Department(**row) for row in results]

    @staticmethod
    def get_qualifications(doctor_id: int) -> List[str]:
        query = "SELECT qualification FROM qualifications WHERE doctor_id = %s"
        results = db.execute_query(query, (doctor_id,))
        return [row['qualification'] for row in results]

    @staticmethod
    def get_specializations(doctor_id: int) -> List[str]:
        query = "SELECT specialization FROM specializations WHERE doctor_id = %s"
        results = db.execute_query(query, (doctor_id,))
        return [row['specialization'] for row in results]

    @staticmethod
    def get_address(doctor_id: int) -> Optional[Address]:
        query = """SELECT id, country, state, city, pincode, flat_house, latitude, longitude
            FROM addresses WHERE doctor_id = %s"""
        result = db.execute_one(query, (doctor_id,))
        return Address(**result) if result else None

    @staticmethod
    def get_appointment_settings(doctor_id: int) -> Optional[AppointmentSettings]:
        query = """
            SELECT id, consultation_charge, follow_up_charge, follow_up_period_days,
                   advance_booking_days, avg_duration_minutes
            FROM appointment_settings WHERE doctor_id = %s
        """
        result = db.execute_one(query, (doctor_id,))
        return AppointmentSettings(**result) if result else None

    @staticmethod
    def get_schedules(doctor_id: int) -> List[Schedule]:
        query = """
            SELECT id, day_of_week, start_time::text, end_time::text, is_available
            FROM schedules WHERE doctor_id = %s ORDER BY day_of_week
        """
        results = db.execute_query(query, (doctor_id,))
        return [Schedule(**row) for row in results]

    @staticmethod
    def build_complete_doctor(doctor_data: Dict) -> Doctor:
        doctor_id = doctor_data['id']
        return Doctor(
            id=doctor_data['id'],
            name=doctor_data.get('name'),
            email=doctor_data.get('email'),
            mobile_numbers=DoctorService.get_mobile_numbers(doctor_id),
            register_no=doctor_data.get('register_no'),
            bio=doctor_data.get('bio'),
            profile_image_url=doctor_data.get('profile_image_url'),
            onboarding_status=doctor_data.get('onboarding_status', 'in_progress'),
            current_step=doctor_data.get('current_step', 1),
            departments=DoctorService.get_departments(doctor_id),
            qualifications=DoctorService.get_qualifications(doctor_id),
            specializations=DoctorService.get_specializations(doctor_id),
            address=DoctorService.get_address(doctor_id),
            appointment_settings=DoctorService.get_appointment_settings(doctor_id),
            schedules=DoctorService.get_schedules(doctor_id),
            created_at=doctor_data.get('created_at'),
            updated_at=doctor_data.get('updated_at')
        )
