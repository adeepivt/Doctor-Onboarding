import strawberry
from typing import List
from app.models import Department
from app.services import DepartmentService

@strawberry.type
class DepartmentQuery:

    @strawberry.field
    def departments(self) -> List[Department]:
        return DepartmentService.get_all_departments()
    
    @strawberry.field
    def search_departments(self, search: str) -> List[Department]:
        return DepartmentService.search_departments(search)
