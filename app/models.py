import strawberry
from typing import Optional, List

@strawberry.type
class Department:
    id: int
    name: str
    icon_name: Optional[str] = None

@strawberry.type
class Address:
    id: Optional[int] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    flat_house: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@strawberry.type
class AppointmentSettings:
    id: Optional[int] = None
    consultation_charge: Optional[int] = None
    follow_up_charge: Optional[int] = None
    follow_up_period_days: Optional[int] = None
    advance_booking_days: Optional[int] = None
    avg_duration_minutes: Optional[int] = None

@strawberry.type
class Schedule:
    id: Optional[int] = None
    day_of_week: int 
    start_time: str
    end_time: str
    is_available: bool = True

@strawberry.type
class Doctor:
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    register_no: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    onboarding_status: str = "in_progress"
    current_step: int = 1
    departments: Optional[List[Department]] = None
    qualifications: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    address: Optional[Address] = None
    appointment_settings: Optional[AppointmentSettings] = None
    schedules: Optional[List[Schedule]] = None

@strawberry.type
class OnboardingMetadata:
    total_steps: int
    completed_steps: List[int]
    current_step: int
    is_complete: bool

# Input Types
@strawberry.input
class AddressInput:
    country: str
    state: str
    city: str
    pincode: str
    flat_house: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@strawberry.input
class AppointmentSettingsInput:
    consultation_charge: int
    follow_up_charge: int
    follow_up_period_days: int
    advance_booking_days: int
    avg_duration_minutes: int

@strawberry.input
class ScheduleInput:
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True