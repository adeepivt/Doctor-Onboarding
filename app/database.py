import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self):
        self.connection = None
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://docuser:docpass@db:5432/docdb"
        )
    
    def connect(self):
        """Establish database connection"""
        if not self.connection or self.connection.closed:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            cursor.close()
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return single result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
    
    def execute_mutation(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute INSERT/UPDATE/DELETE and return result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            print(query, params, 'mutation --- params\n\n')
            cursor.execute(query, params)
            conn.commit()
            try:
                result = cursor.fetchone()
                return dict(result) if result else None
            except:
                return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute_batch(self, query: str, params_list: List[tuple]) -> None:
        """Execute batch INSERT operations"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            for params in params_list:
                cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


db = Database()