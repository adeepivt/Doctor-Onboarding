import strawberry
from typing import Optional
from app.models import OnboardingMetadata
from app.services import OnboardingService

@strawberry.type
class OnboardingQuery:

    @strawberry.field
    def onboarding_metadata(self, doctor_id: int) -> Optional[OnboardingMetadata]:
        return OnboardingService.get_onboarding_metadata(doctor_id)
