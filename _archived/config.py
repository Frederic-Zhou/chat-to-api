import yaml


# Load API configuration from YAML file
def load_handlers_config(file_path="cats_handlers.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


# Load system configuration from YAML file
def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


# Load the system configuration
config = load_config()
MESSAGE_HANDLER = load_handlers_config()

# Extract configurations
DB_CONNECTION_STRING = config["database"]["connection_string"]
RABBITMQ_URL = config["rabbitmq"]["url"]
RABBITMQ_QUEUE = config["rabbitmq"]["queue"]
MODEL_DIR = config["models_dir"]
MODEL_LANGS = config["models_langs"]
