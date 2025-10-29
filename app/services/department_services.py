from typing import List
from app.models import Department
from app.database import db

class DepartmentService:
    @staticmethod
    def get_all_departments() -> List[Department]:
        query = "SELECT id, name, icon_name FROM departments ORDER BY name"
        results = db.execute_query(query)
        return [Department(**row) for row in results]

    @staticmethod
    def search_departments(search: str) -> List[Department]:
        query = """
            SELECT id, name, icon_name FROM departments
            WHERE LOWER(name) LIKE LOWER(%s)
            ORDER BY name
        """
        results = db.execute_query(query, (f'%{search}%',))
        return [Department(**row) for row in results]
