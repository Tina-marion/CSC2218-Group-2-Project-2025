# infrastructure/config.py
from dataclasses import dataclass

@dataclass
class Settings:
    use_memory_repositories: bool = True
    # Add other configuration parameters here

settings = Settings()