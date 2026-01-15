import subprocess
import os
from multiprocessing import Pool, cpu_count



# Function to run the command for a single file
def run_job(file_path):
    command = f"pybnf -c {file_path} -o"
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Job completed for {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running job for {file_path}: {e}")

def main(directory):
    # Get list of .conf files in the specified directory
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.conf')]
    
    # Determine the number of cores to use (leaving one core free)
    num_cores = max(cpu_count() - 1, 1)
    
    # Create a pool of worker processes
    with Pool(processes=num_cores) as pool:
        pool.map(run_job, files)

if __name__ == "__main__":
    # Set the directory containing the .conf files
    conf_directory = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/conf_files"
    main(conf_directory)
