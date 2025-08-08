import sqlite3
from abc import ABC, abstractmethod

class DatabaseClient(ABC):
    NOT_IMPLEMENTED_MSG = "This method should be overridden by subclasses."
    
    @abstractmethod
    def open_connection(self):
        """Open a connection to the database."""
        raise NotImplementedError(self.NOT_IMPLEMENTED_MSG)

    @abstractmethod
    def execute_query(self, query: str):
        """Execute a query on the database."""
        raise NotImplementedError(self.NOT_IMPLEMENTED_MSG)

    @abstractmethod
    def close_connection(self):
        """Close the database connection."""
        raise NotImplementedError(self.NOT_IMPLEMENTED_MSG)


class SQLiteClient(DatabaseClient):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def open_connection(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def _execute(self, query, params=None):
        with self.connection:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

    def execute_query(self, query, params=None):
        self._execute(query, params)
        self.connection.commit()

    def fetch_all(self, query, params=None):
        self._execute(query, params)
        return self.cursor.fetchall()
    
    def execute_script(self, script):
        self.cursor.executescript(script)
        self.connection.commit()