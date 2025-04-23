import sys
import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Backend directory: {BACKEND_DIR}")

# Add the backend directory to the Python path
sys.path.append(BACKEND_DIR)
print(f"Python path: {sys.path}")

# Try to import config
try:
    from configs.config import set_envs
    print("Successfully imported configs.config")
except ImportError as e:
    print(f"Failed to import configs.config: {e}")
    # Try to add the parent directory to the path
    try:
        sys.path.append(os.path.dirname(BACKEND_DIR))
        from configs.config import set_envs
        print("Successfully imported configs.config from parent directory")
    except ImportError as e:
        print(f"Failed to import configs.config from parent directory: {e}") 