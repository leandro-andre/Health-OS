from django.db import DEFAULT_DB_ALIAS, connections


class DjangoDatabaseHealthChecker:
    def is_healthy(self) -> bool:
        try:
            connection = connections[DEFAULT_DB_ALIAS]
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            return False

        return True
