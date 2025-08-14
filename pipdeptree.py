import subprocess
import platform
import shutil
from pathlib import Path

# Define paths
project_dir = Path(__file__).parent.resolve()
venv_dir = project_dir / ".venv"
pyproject_file = project_dir / "pyproject.toml"
requirements_file = project_dir / "requirements.txt"
deps_output = project_dir / "depsssssssss.json"

# Detect OS
def get_os_type():
    system = platform.system()
    print(f"Detected OS: {system}")
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

# OS-specific pipdeptree path
def get_pipdeptree_cmd(os_type):
    if os_type == "windows":
        return [str(venv_dir / "Scripts" / "pipdeptree.exe")]
    else:
        return [str(venv_dir / "bin" / "pipdeptree")]

# Create virtual environment
def create_venv():
    print("Creating virtual environment")
    subprocess.run(["uv", "venv"], check=True)

# Install dependencies
def install_dependencies():
    if pyproject_file.exists():
        print("Detected pyproject.toml. Proceeding with installation...")
        print("Installing from pyproject.toml...")
        subprocess.run(["uv", "pip", "install", "."], check=True)
    if requirements_file.exists():
        print("Detected requirements.txt. Proceeding with installation...")
        print("Installing from requirements.txt...")
        subprocess.run(["uv", "pip", "install", "-r", str(requirements_file)], check=True)
    if not pyproject_file.exists() and not requirements_file.exists():
        print("No pyproject.toml or requirements.txt found. Skipping dependency installation.")

# Install pipdeptree
def install_pipdeptree():
    print("Installing pipdeptree...")
    subprocess.run(["uv", "pip", "install", "pipdeptree"], check=True)

# Export dependency tree
def export_deps(os_type):
    print("Exporting dependency tree...")
    cmd = get_pipdeptree_cmd(os_type) + ["--json-tree"]
    with deps_output.open("w") as f:
        subprocess.run(cmd, stdout=f, check=True)

# Cleanup virtual environment
def cleanup_venv():
    if venv_dir.exists():
        print("Removing virtual environment...")
        shutil.rmtree(venv_dir)
        print(".venv directory removed.")

# OS-specific logic dispatcher
def run_for_windows():
    print("Running on Windows...")
    create_venv()
    install_dependencies()
    install_pipdeptree()
    export_deps("windows")
    cleanup_venv()

def run_for_linux():
    print("Running on Linux...")
    create_venv()
    install_dependencies()
    install_pipdeptree()
    export_deps("linux")
    cleanup_venv()

def run_for_macos():
    print("Running on macOS...")
    create_venv()
    install_dependencies()
    install_pipdeptree()
    export_deps("macos")
    cleanup_venv()

# Main dispatcher
def main():
    print("Starting setup...")
    os_type = get_os_type()
    if os_type == "windows":
        run_for_windows()
    elif os_type == "linux":
        run_for_linux()
    elif os_type == "macos":
        run_for_macos()

    print("Setup complete. Dependency tree saved to depsssssssss.json.")

if __name__ == "__main__":
    main()

