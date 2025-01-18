from connection_db import create_connection
from oracle_backups import oracle_backup_manager

connection = create_connection()

oracle_backup_manager(connection)
