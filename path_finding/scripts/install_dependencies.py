"""
Install required dependencies for the pathfinding comparison system
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    """Install all required packages"""
    packages = [
        "numpy",
        "matplotlib",
        "networkx",
        "scikit-learn",
        "torch",
        "torch-geometric"
    ]
    
    print("Installing dependencies for Robot Pathfinding Comparison System...")
    print("=" * 60)
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 60)
    print(f"Installation complete: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("✓ All dependencies installed successfully!")
        print("You can now run the pathfinding comparison system.")
    else:
        print("⚠ Some packages failed to install. Please install them manually:")
        print("pip install numpy matplotlib networkx scikit-learn torch torch-geometric")

if __name__ == "__main__":
    main()
