import oracledb
from configparser import ConfigParser


def initialize_oracle_client(lib_dir):
    """Initialize the Oracle client."""
    oracledb.init_oracle_client(lib_dir=lib_dir)


def load_config(file_path):
    """Load configuration from the specified INI file."""
    config = ConfigParser()
    config.read(file_path)
    return config


def create_connection():
    """Create and return a database connection."""
    try:
        lib_dir = r"c:\Users\user\instantclient_23_5"  # Change to your local address with instantclient.
        initialize_oracle_client(lib_dir)
        config = load_config("config_dev.ini")
        db_config_d = config["database_dwh"]
        connection = oracledb.connect(
            user=db_config_d["user"],
            password=db_config_d["password"],
            host=db_config_d["host"],
            port=db_config_d["port"],  # type: ignore
            service_name=db_config_d["service_name"],
        )
        return connection
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        return None


connection = create_connection()
