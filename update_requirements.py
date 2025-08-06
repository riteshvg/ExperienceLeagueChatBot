#!/usr/bin/env python3
"""
Update requirements.txt with new dependencies for automated refresh system
"""

def update_requirements():
    """Add new dependencies to requirements.txt"""
    
    # Read current requirements
    try:
        with open('requirements.txt', 'r') as f:
            current_requirements = f.read()
    except FileNotFoundError:
        current_requirements = ""
    
    # New dependencies for auto-refresh system
    new_dependencies = [
        "schedule>=1.2.0",  # For scheduling refresh tasks
        "beautifulsoup4>=4.12.0",  # For parsing HTML content
        "requests>=2.31.0",  # Already present, but ensuring version
    ]
    
    # Check which dependencies are already present
    existing_lines = current_requirements.strip().split('\n') if current_requirements else []
    existing_packages = [line.split('>=')[0].split('==')[0] for line in existing_lines if line.strip()]
    
    # Add missing dependencies
    missing_dependencies = []
    for dep in new_dependencies:
        package_name = dep.split('>=')[0].split('==')[0]
        if package_name not in existing_packages:
            missing_dependencies.append(dep)
    
    # Write updated requirements
    if missing_dependencies:
        with open('requirements.txt', 'a') as f:
            f.write('\n# Auto-refresh system dependencies\n')
            for dep in missing_dependencies:
                f.write(f'{dep}\n')
        
        print(f"✅ Added {len(missing_dependencies)} new dependencies to requirements.txt:")
        for dep in missing_dependencies:
            print(f"  - {dep}")
    else:
        print("✅ All dependencies already present in requirements.txt")

if __name__ == "__main__":
    update_requirements() 