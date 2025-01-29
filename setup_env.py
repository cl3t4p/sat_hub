import os
import subprocess
import sys

def main():
    # Check if Python version is 3.6 or higher
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher is required to run this script.")
        sys.exit(1)

    # Define virtual environment directory
    venv_dir = ".venv"

    # Step 1: Create a virtual environment if it doesn't exist
    if os.path.exists(venv_dir):
        print(f"Virtual environment '{venv_dir}' already exists.")
    else:
        print(f"Creating virtual environment in '{venv_dir}'...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    # Step 2: Activate virtual environment
    activate_script = os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "activate")

    if not os.path.exists(activate_script):
        print("Error: Virtual environment activation script not found.")
        sys.exit(1)

    print("Virtual environment created successfully!")


    # Step 3: Install dependencies if requirements.txt exists
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from '{requirements_file}'...")
        subprocess.run([os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "pip"), "install", "-r", requirements_file], check=True)
        print("Dependencies installed successfully!")
    else:
        print(f"No '{requirements_file}' file found. Skipping dependency installation.")



    # Build libs
    main_dir = os.getcwd()
    venv_dir = os.path.join(main_dir, venv_dir)

    print(f"venv_dir: {venv_dir}")

    if os.path.exists("libs"):
        for folder in os.listdir("libs"):
            if os.path.isdir(os.path.join("libs", folder)):
                # If folder starts with _, skip it
                if folder.startswith("_"):
                    continue
                print(f"Building {folder}...")
                # Enter the folder and run the command
                os.chdir(os.path.join("libs", folder))
                subprocess.run([os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "python"), "setup.py", "build"], check=True)
                subprocess.run([os.path.join(venv_dir, "Scripts" if os.name == "nt" else "bin", "pip"), "install", "."], check=True)
                print(f"{folder} built successfully!")
                os.chdir(main_dir)
    else:
        print("No 'libs' directory found. Skipping building of libraries.")
    print("Setup complete. Happy coding!")

if __name__ == "__main__":
    main()