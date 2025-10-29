import strawberry
from .department_queries import DepartmentQuery
from .doctor_queries import DoctorQuery
from .on_boarding_queries import OnboardingQuery

@strawberry.type
class Query(DepartmentQuery, DoctorQuery, OnboardingQuery):
    pass
