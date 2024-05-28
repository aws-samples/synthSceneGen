import subprocess
import os
import sys
import traceback


def validate_code():
    # Assuming your shell script is named 'myscript.sh'
    script_path = '/home/ubuntu/environment/carla-agent-test/refresh-env.sh'
    result = subprocess.run(['sh', script_path])
    cmd = [
    "sudo",
    "docker",
    "run",
    "-it",
    "--expose",
    "9090",
    "-p",
    "0.0.0.0:9090:22",
    "-v",
    "/home/ubuntu/environment/carla-output/images:/app/carla-output/images",
    "--name",
    "carla-1",
    "carla-agent-env:latest"]
    with open("docker.log", "wb") as log_file:
        subprocess.run(cmd, stdout=log_file)
    
    # Read the contents of the log file
    with open("docker.log", "r") as log_file:
        log_contents = log_file.read()

    return(log_contents)

def save_code_to_file(input_code):
    script_name = "script.py"
    file_dir = "/home/ubuntu/environment/carla-agent-test/"
    file_name = f"{file_dir}{script_name}"
    with open(file_name, "w") as f:
        f.write(input_code)
    return()

def delete_prev_images():
    directory_path = "/home/ubuntu/environment/carla-output/images"

# Check if the directory exists
    if os.path.exists(directory_path):
        # Get a list of files in the directory
        files_in_directory = os.listdir(directory_path)

        if files_in_directory:
            # There are files in the directory
            print(f"The directory {directory_path} contains files.")

            # Ask for confirmation before deleting
            confirm_delete = "y"

            if confirm_delete.lower() == "y":
                # Iterate over all files in the directory
                for filename in files_in_directory:
                    file_path = os.path.join(directory_path, filename)
                    try:
                        # Check if it's a file
                        if os.path.isfile(file_path):
                            # Delete the file
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")

                print("All files have been deleted from the directory.")
            else:
                print("No files were deleted.")
        else:
            print(f"The directory {directory_path} is empty.")
    else:
        print(f"The directory {directory_path} does not exist.")