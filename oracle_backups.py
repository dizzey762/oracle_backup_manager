import os
import datetime
import shutil
import logging

# Constants
SECONDS_IN_A_DAY = 86400  # 1 day = 86400 seconds


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def oracle_backup_manager(
    connection,
    backup_directory=None,
    days_threshold=None,
    object_type=None,
    object_name=None,
):
    """Main function to manage the backup of Oracle database objects."""
    valid_object_types = {"PACKAGE", "PROCEDURE", "FUNCTION"}

    if object_type and object_type.upper() not in valid_object_types:
        logging.error(
            f"Invalid object_type '{object_type}'. Please enter one of the following: {', '.join(valid_object_types)}."
        )
        return  # Exit the function if the object type is invalid

    days_threshold_seconds = (
        (days_threshold * SECONDS_IN_A_DAY) if days_threshold is not None else None
    )

    if backup_directory is None:
        backup_directory = os.getcwd()  # Use current directory if none is provided
    object_type = object_type.upper() if object_type else None

    def delete_old_folders(base_folder_path, threshold_seconds):
        """Delete date-time folders older than days_threshold inside directories."""
        now = datetime.datetime.now()
        deleted_count = 0
        for item in os.listdir(base_folder_path):
            item_path = os.path.join(base_folder_path, item)
            if os.path.isdir(item_path):
                for sub_dir in os.listdir(item_path):
                    sub_dir_path = os.path.join(item_path, sub_dir)
                    if os.path.isdir(sub_dir_path):
                        try:
                            creation_time = datetime.datetime.fromtimestamp(
                                os.path.getctime(sub_dir_path)
                            )
                            if (
                                threshold_seconds is not None
                                and (now - creation_time).total_seconds()
                                > threshold_seconds
                            ):  # Check if older than x days
                                shutil.rmtree(
                                    sub_dir_path
                                )  # Remove directory and its contents
                                logging.info(
                                    f"Deleted old date-time folder: {sub_dir_path}"
                                )
                                deleted_count += 1
                        except Exception as e:
                            logging.error(
                                f"Error processing folder '{sub_dir_path}': {e}"
                            )
        if deleted_count == 0:
            logging.info(f"No objects older than {days_threshold} days found.")
        else:
            logging.info(f"Total objects deleted: {deleted_count}")

    def backup_objects(object_type, backup_path):
        """Generic backup function for packages, procedures, and functions."""

        cursor = connection.cursor()  # Use the passed connection
        query = f"SELECT OBJECT_NAME FROM USER_OBJECTS WHERE OBJECT_TYPE = '{object_type.upper()}'"

        try:
            cursor.execute(query)
            objects = cursor.fetchall()
            if not objects:
                logging.info(f"No {object_type}s found.")
                return

            backup_folder = os.path.join(backup_path, f"{object_type.lower()}_backups")
            os.makedirs(backup_folder, exist_ok=True)
            current_date_time = datetime.datetime.now()
            current_date = current_date_time.strftime("%Y-%m-%d")
            current_time = current_date_time.strftime("%H-%M")

            backup_count = 0

            for obj in objects:
                object_name = obj[0]
                obj_folder = os.path.join(backup_folder, object_name)
                os.makedirs(obj_folder, exist_ok=True)
                date_time_folder = os.path.join(
                    obj_folder, f"{current_date}_{current_time}"
                )
                os.makedirs(date_time_folder, exist_ok=True)

                ddl_query = f"SELECT dbms_metadata.get_ddl('{object_type.upper()}', '{object_name}') FROM dual"
                cursor.execute(ddl_query)
                ddl_result = cursor.fetchone()

                if ddl_result:
                    ddl_text = ddl_result[0].read()
                    backup_file_path = os.path.join(
                        date_time_folder, f"{object_name}.sql"
                    )
                    with open(backup_file_path, "w") as file:
                        file.write(ddl_text)
                    logging.info(
                        f"Backup of {object_type.lower()} '{object_name}' created successfully at {backup_file_path}"
                    )
                    backup_count += 1
                else:
                    logging.warning(
                        f"No DDL found for {object_type.lower()} '{object_name}'"
                    )
            print(f"Total {object_type.lower()}s backed up: {backup_count}")

        except Exception as e:
            logging.error(f"Error retrieving {object_type}s or DDL: {e}")
        finally:
            delete_old_folders(backup_folder, days_threshold_seconds)

    def backup_specific_object(object_type, object_name, backup_path):
        """Backup a specific object (package, procedure, or function)."""
        object_name = object_name.upper()
        cursor = connection.cursor()  # Use the passed connection
        check_query = f"SELECT COUNT(*) FROM USER_OBJECTS WHERE OBJECT_TYPE = '{object_type.upper()}' AND OBJECT_NAME = '{object_name}'"
        cursor.execute(check_query)
        exists = cursor.fetchone()[0]
        if exists == 0:
            logging.error(
                f"The specified {object_type.lower()} '{object_name}' does not exist."
            )
            return  # Exit if the object does not exist
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.datetime.now().strftime("%H-%M")
        specific_folder = os.path.join(backup_path, f"{object_type.lower()}_backups")
        os.makedirs(specific_folder, exist_ok=True)
        specific_object_folder = os.path.join(specific_folder, f"{object_name}")
        os.makedirs(specific_object_folder, exist_ok=True)

        try:
            ddl_query = f"SELECT dbms_metadata.get_ddl('{object_type.upper()}', '{object_name}') FROM dual"
            cursor.execute(ddl_query)
            ddl_result = cursor.fetchone()

            if ddl_result:
                ddl_text = ddl_result[0].read()
                date_time_subfolder = os.path.join(
                    specific_object_folder, f"{current_date}_{current_time}"
                )
                os.makedirs(date_time_subfolder, exist_ok=True)
                backup_file_path = os.path.join(
                    date_time_subfolder, f"{object_name}.sql"
                )
                with open(backup_file_path, "w") as file:
                    file.write(ddl_text)
                logging.info(
                    f"Backup of {object_type.lower()} '{object_name}' created successfully at {backup_file_path}"
                )
            else:
                logging.warning(
                    f"No DDL found for {object_type.lower()} '{object_name}'"
                )

        except Exception as e:
            logging.error(f"Error retrieving {object_type.lower()} or DDL: {e}")
        finally:
            delete_old_folders(specific_folder, days_threshold_seconds)

    if object_name and not object_type:
        while True:
            object_type = input(
                "You provided an object name. Please enter the object type (PACKAGE/PROCEDURE/FUNCTION): "
            ).upper()
            if object_type in valid_object_types:
                break
            else:
                logging.warning(
                    "Invalid object type. Please enter one of the following: PACKAGE, PROCEDURE, FUNCTION."
                )

    if object_type:
        if not object_name:
            object_name = input(
                f"Enter the name of the {object_type.lower()} you want to backup: "
            ).upper()
        backup_specific_object(object_type, object_name, backup_directory)
    else:
        # Р’Р·Р°РёРјРѕРґРµР№СЃС‚РІРёРµ СЃ РїРѕР»СЊР·РѕРІР°С‚РµР»РµРј
        while True:
            user_input = input(
                "Choose an option:\nSelect from 1 to 6. \n 1. Backup packages \n 2. Backup procedures\n 3. Backup functions\n 4. List of objects\n 5. Backup specific object\n 6. Exit\n"
            )
            if user_input == "1":
                backup_objects("PACKAGE", backup_directory)
            elif user_input == "2":
                backup_objects("PROCEDURE", backup_directory)
            elif user_input == "3":
                backup_objects("FUNCTION", backup_directory)
            elif user_input == "4":
                obj_type = input("Enter object type (PACKAGE/PROCEDURE/FUNCTION): ")
                list_objects(connection, obj_type)
            elif user_input == "5":
                while True:
                    obj_type = input(
                        "Enter object type (PACKAGE/PROCEDURE/FUNCTION): "
                    ).upper()
                    if obj_type in valid_object_types:
                        obj_name = input("Enter object name: ").upper()
                        backup_specific_object(obj_type, obj_name, backup_directory)
                        break  # Exit the inner while loop after successful backup
                    else:
                        logging.warning(
                            "Invalid object type. Please enter one of the following: PACKAGE, PROCEDURE, FUNCTION."
                        )
            elif user_input == "6":
                logging.info("Exiting the program.")
                break
            else:
                logging.warning("Invalid choice. Select from 1 to 6.")


def list_objects(connection, object_type):
    """List objects of a specified type."""
    cursor = connection.cursor()
    query = f"SELECT OBJECT_NAME FROM USER_OBJECTS WHERE OBJECT_TYPE='{object_type.upper()}'"

    try:
        cursor.execute(query)
        objects = cursor.fetchall()
        if not objects:
            logging.info(f"No {object_type}s found.")
            return

        logging.info(f"{object_type.capitalize()}s:")
        for obj in objects:
            print(obj[0])  # Print the name of each object

    except Exception as e:
        logging.error(f"Error retrieving {object_type}s: {e}")
    finally:
        cursor.close()
