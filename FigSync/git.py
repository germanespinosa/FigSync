import subprocess

def is_git_accessible():
    try:
        # Run 'git --version' to check if Git is installed and accessible
        result = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check if the return code is 0 (indicating success)
        if result.returncode == 0:
            return True, result.stdout.decode().strip()  # Git is accessible, return version
        else:
            return False, result.stderr.decode().strip()  # Git is not accessible, return error message
    except FileNotFoundError:
        # If Git is not found in the system path
        return False, "Git is not installed or not in the system PATH."

