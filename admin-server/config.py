import json
import os

from dotenv import dotenv_values, find_dotenv, load_dotenv

dotenv_path = find_dotenv()
env_config = dotenv_values(dotenv_path, verbose=True)
load_dotenv(dotenv_path, verbose=True)

if __name__ == '__main__':
    print(json.dumps(env_config))
    print(os.getenv("DATABASE_URL"))
