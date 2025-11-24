import importlib.util
import os
from fastapi import FastAPI, APIRouter
from pathlib import Path
from typing import Dict, Any

MODULES_DIR = Path(__file__).parent

def load_module_config(module_path: Path) -> Dict[str, Any] | None:
    """Loads the module_config from a module's module_config.py file."""
    config_file = module_path / "module_config.py"
    if not config_file.exists():
        return None

    spec = importlib.util.spec_from_file_location("module_config", config_file)
    if spec is None:
        return None
    module_config_module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        return None
    spec.loader.exec_module(module_config_module)

    return getattr(module_config_module, "module_config", None)

def register_module_routers(app: FastAPI):
    """
    Scans the modules directory, loads module configurations,
    and registers their API routers with the FastAPI application.
    """
    for module_path in MODULES_DIR.iterdir():
        if module_path.is_dir() and not module_path.name.startswith("__"):
            module_config = load_module_config(module_path)
            if module_config and "api_router" in module_config:
                router_path = module_path / module_config["api_router"]
                if router_path.exists():
                    try:
                        # Dynamically import the router
                        relative_path = os.path.relpath(router_path, Path(__file__).parent.parent)
                        module_name = relative_path.replace("\\", ".").replace("/", ".").replace(".py", "")
                        
                        router_module = importlib.import_module(f"api.{module_name}")
                        router: APIRouter = getattr(router_module, "router")
                        
                        # Register the router with a prefix from the module's slug
                        app.include_router(router, prefix=f"/api/v1/{module_config['slug']}", tags=[module_config['name']])
                        print(f"Registered API routes for module: {module_config['name']} at /api/v1/{module_config['slug']}")
                    except Exception as e:
                        print(f"Error loading router for module {module_path.name}: {e}")
