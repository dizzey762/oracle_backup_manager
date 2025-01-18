*The Oracle Backup Manager is a Python program designed to facilitate the backup of Oracle database objects such as packages, procedures, and functions. It allows users to manage backups efficiently, delete old backups based on a specified threshold, and retrieve the Data Definition Language (DDL) for specified objects.*

# Features
Backup Management: Supports backing up packages, procedures, and functions.
Object Listing: Lists existing objects of specified types in the database.
Old Backup Deletion: Automatically deletes backups older than a specified number of days.
Flexible Input: Allows users to specify object types and names interactively.

# Usage
To use the Oracle Backup Manager, you need to establish a connection to your Oracle database. The main function is oracle_backup_manager, which can be called with the following parameters:

# Interactive Menu
If object_type and object_name are not provided, the program will present an interactive menu allowing users to choose from various options

# Functions Description
*delete_old_folders(base_folder_path, threshold_seconds)*

Deletes folders older than the specified threshold within the given base folder path.

*backup_objects(object_type, backup_path)*

Backs up all objects of the specified type (PACKAGE, PROCEDURE, FUNCTION) into designated folders.

*backup_specific_object(object_type, object_name, backup_path)*

Backs up a specific database object by its name and type.

*list_objects(connection, object_type)*

Lists all objects of a specified type in the database.