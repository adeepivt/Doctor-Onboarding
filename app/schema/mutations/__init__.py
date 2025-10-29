import strawberry
from .doctor_mutations import DoctorMutation
from .onboarding_mutations import OnboardingMutation

@strawberry.type
class Mutation(DoctorMutation, OnboardingMutation):
    pass
