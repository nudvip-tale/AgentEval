import os

# Automatically load .env from the project root directory
try:
    config_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(config_dir, "..", "..", ".."))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()
except Exception:
    pass

from dynaconf import Dynaconf

path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
settings = Dynaconf(
    load_dotenv=True,
    envvar_prefix="DYNACONF",
    settings_files=[f'{path}/settings.yaml', f'{path}/.secrets.yaml'],
    environments=True,
    core_loaders=['YAML']
)