import os
import numpy as np
import shutil
import re
def check_and_create_files(state_names, template_conf_file, template_bngl, conf_dir, bngl_dir, template_state_name="Arizona"):
    for state, abbrev in state_names.items():
        conf_file_path = os.path.join(conf_dir, f"{state}.conf")
        bngl_file_path = os.path.join(bngl_dir, f"{state}.bngl")

        # Check for conf file
        if not os.path.exists(conf_file_path):
            print(f"Creating .conf file for {state} from template.")
            shutil.copy(template_conf_file, conf_file_path)
            with open(conf_file_path, 'r') as conf_file:
                conf_content = conf_file.read()
            conf_content = conf_content.replace(template_state_name, state)
            with open(conf_file_path, 'w') as conf_file:
                conf_file.write(conf_content)

        # Check for bngl file
        if not os.path.exists(bngl_file_path):
            print(f"Creating .bngl file for {state} from template.")
            shutil.copy(template_bngl, bngl_file_path)
            with open(bngl_file_path, 'r') as bngl_file:
                bngl_content = bngl_file.read()
            bngl_content = bngl_content.replace(template_state_name, state)
            with open(bngl_file_path, 'w') as bngl_file:
                bngl_file.write(bngl_content)

def generate_combined_mle_file_AMCMC(state_names, base_dir, output_file):
    with open(output_file, 'w') as combined_mle_file:
        for state in state_names:
            params_file_path = os.path.join(base_dir, state, 'Results/sorted_params_final.txt')
            if os.path.exists(params_file_path):
                with open(params_file_path, 'r') as params_file:
                    lines = params_file.readlines()
                    
                    if len(lines) > 1:  # Ensure there are at least 2 lines (skip first row)
                        # Get row 2 (index 1, after skipping header row 0)
                        second_row = lines[1].strip()
                        # Split by tab (or whitespace) to get columns
                        columns = second_row.split()
                        
                        # Skip first two columns (indices 0 and 1), then extract columns 2-8 (indices 2-8)
                        # Reorder as: 2, 4, 5, 6, 7, 3, 8 (0-indexed)
                        if len(columns) > 8:
                            # Extract columns 2-8 (skip first two columns)
                            params = columns[2:9]  # columns 2 through 8 (inclusive)
                            # Reorder: 2, 4, 5, 6, 7, 3, 8
                            # params indices: 0=col2, 1=col3, 2=col4, 3=col5, 4=col6, 5=col7, 6=col8
                            reordered_params = [
                                params[0],  # col2 (index 0 in params)
                                params[2],  # col4 (index 2 in params)
                                params[3],  # col5 (index 3 in params)
                                params[4],  # col6 (index 4 in params)
                                params[5],  # col7 (index 5 in params)
                                params[1],  # col3 (index 1 in params)
                                params[6]   # col8 (index 6 in params)
                            ]
                            # Join with spaces
                            formatted_params = " ".join(reordered_params)
                            # Write to the combined file in the desired format
                            combined_mle_file.write(f"{state}: {formatted_params}\n")
                        else:
                            print(f"Skipping {state}: Not enough columns in row 2.")
            else:
                print(f"Skipping {state}: sorted_params_final.txt file not found.")

def generate_combined_mle_file_DE(state_names, base_dir, output_file):
    with open(output_file, 'w') as combined_mle_file:
        for state in state_names:
            params_file_path = os.path.join(base_dir, state, 'Results/sorted_params_final.txt')
            if os.path.exists(params_file_path):
                with open(params_file_path, 'r') as params_file:
                    lines = params_file.readlines()
                    
                    if len(lines) > 1:  # Ensure there are at least 2 lines
                        second_row = lines[1].strip()  # Second row contains the params
                        # Split the parameters into a list and join them with commas
                        formatted_params = ", ".join(second_row.split())
                        # Write to the combined file in the desired format
                        combined_mle_file.write(f"{state}: {formatted_params}\n")
            else:
                print(f"Skipping {state}: params_0.txt file not found.")                

def update_starting_params_from_mle_AMCMC(state_names, conf_dir, mle_file):
    # Read the MLEs from State_MLEs.txt
    state_mles = {}
    with open(mle_file, 'r') as mle_file:
        for line in mle_file:
            state, params = line.split(": ")
            state_mles[state] = params.strip()
    
    # Update each state's conf file
    for state in state_names:
        if state not in state_mles:
            print(f"Skipping {state}: No MLE found.")
            continue  # Skip states with no MLE
        
        conf_file_path = os.path.join(conf_dir, f"{state}.conf")
        
        if os.path.exists(conf_file_path):
            with open(conf_file_path, 'r') as conf_file:
                conf_content = conf_file.readlines()
            
            # Look for the `starting_params` section
            starting_params_found = False
            for i, line in enumerate(conf_content):
                if line.startswith("starting_params ="):
                    starting_params_found = True
                    # Replace existing starting_params
                    conf_content[i] = f"starting_params = {state_mles[state]}\n"
                    if i + 1 < len(conf_content):
                        del conf_content[i + 1]  # Remove the next line if it exists to avoid duplication
                    break
            
            if not starting_params_found:
                # Add a new `starting_params` section if not found
                conf_content.append(f"\nstarting_params = {state_mles[state]}\n")
            
            # Write the updated content back to the conf file
            with open(conf_file_path, 'w') as conf_file:
                conf_file.writelines(conf_content)
        else:
            print(f"Skipping {state}: Conf file not found.")

def update_starting_params_from_mle_DE(state_names, conf_dir, mle_file):
    # Read the MLEs from State_MLEs.txt
    state_mles = {}
    with open(mle_file, 'r') as mle_file:
        for line in mle_file:
            state, params = line.split(": ")
            # Split parameters and omit the first two columns (generation number and objective function score)
            params_list = params.strip().split(", ")[2:]
            state_mles[state] = ", ".join(params_list)
    
    # Update each state's conf file
    for state in state_names:
        if state not in state_mles:
            print(f"Skipping {state}: No MLE found.")
            continue  # Skip states with no MLE
        
        conf_file_path = os.path.join(conf_dir, f"{state}.conf")
        
        if os.path.exists(conf_file_path):
            with open(conf_file_path, 'r') as conf_file:
                conf_content = conf_file.readlines()
            
            # Look for the `starting_params` section
            starting_params_found = False
            for i, line in enumerate(conf_content):
                if line.startswith("starting_params ="):
                    starting_params_found = True
                    # Replace existing starting_params
                    conf_content[i] = f"starting_params = {state_mles[state]}\n"
                    if i + 1 < len(conf_content):
                        del conf_content[i + 1]  # Remove the next line if it exists to avoid duplication
                    break
            
            if not starting_params_found:
                # Add a new `starting_params` section if not found
                conf_content.append(f"\nstarting_params = {state_mles[state]}\n")
            
            # Write the updated content back to the conf file
            with open(conf_file_path, 'w') as conf_file:
                conf_file.writelines(conf_content)
        else:
            print(f"Skipping {state}: Conf file not found.")

def add_params_to_bngl(state_names, conf_dir, bngl_dir):
    """
    Adds new parameters from conf files to the BNGL files.

    Args:
        state_names (list): List of state names.
        conf_dir (str): Directory containing the conf files.
        bngl_dir (str): Directory containing the BNGL files.
    """
    # Iterate over each state
    for state in state_names:
        conf_file_path = os.path.join(conf_dir, f"{state}.conf")
        bngl_file_path = os.path.join(bngl_dir, f"{state}.bngl")

        if os.path.exists(conf_file_path) and os.path.exists(bngl_file_path):
            # Read the conf file to find new parameters
            with open(conf_file_path, 'r') as conf_file:
                conf_lines = conf_file.readlines()

            # Extract the parameters to add to the BNGL file
            params_to_add = []
            for line in conf_lines:
                if line.startswith("uniform_var") and "__FREE" in line:
                    parts = line.split()
                    param_name = parts[2].split('=')[0]  # Extract param name
                    param_short = param_name.split('__')[0]  # e.g., b4 from b4__FREE
                    params_to_add.append((param_short, param_name))

            # Read the BNGL file
            with open(bngl_file_path, 'r') as bngl_file:
                bngl_lines = bngl_file.readlines()

            # Check existing parameters in the BNGL file
            existing_params = set()
            inside_param_block = False
            for line in bngl_lines:
                if "begin parameters" in line:
                    inside_param_block = True
                elif "end parameters" in line:
                    inside_param_block = False
                elif inside_param_block:
                    if " " in line:  # Check for spaces to ensure it's a parameter line
                        existing_param = line.split()[0]  # Get the first part of the line (the param name)
                        existing_params.add(existing_param)

            # Add new parameters to the parameters block
            updated_bngl_lines = []
            inside_param_block = False
            for line in bngl_lines:
                updated_bngl_lines.append(line)
                if "begin parameters" in line:
                    inside_param_block = True
                elif "end parameters" in line and inside_param_block:
                    # Add the new parameters here, above "end parameters"
                    for short_name, full_name in params_to_add:
                        if short_name not in existing_params:  # Only add if it's not already present
                            updated_bngl_lines.insert(-1, f"{short_name} {full_name}\n")  # Change to use space
                    inside_param_block = False

            # Write the updated content back to the BNGL file
            with open(bngl_file_path, 'w') as bngl_file:
                bngl_file.writelines(updated_bngl_lines)

        else:
            print(f"Skipping {state}: Missing conf or bngl file.")


def update_conf_with_free_params(state_names, config_dir):
    global free_params  # Access the free_params defined in the script

    for state in state_names:
        conf_file_path = f"{config_dir}/{state}.conf"

        # Read the existing lines from the configuration file
        try:
            with open(conf_file_path, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print(f"Configuration file for {state} not found. Skipping.")
            continue

        # Prepare to hold updated lines
        updated_lines = []
        param_names_in_conf = set()
        last_uniform_var_index = -1

        # Go through each line and update or add the free parameters
        for index, line in enumerate(lines):
            if line.startswith("uniform_var ="):
                param_name = line.split()[2]  # Assuming the format is uniform_var = param__FREE value1 value2
                param_names_in_conf.add(param_name)
                last_uniform_var_index = index  # Track the last uniform_var line

                if param_name in free_params:
                    # Update existing parameter with new values from free_params
                    new_values = free_params[param_name]
                    updated_line = f"uniform_var = {param_name} {new_values[0]} {new_values[1]}\n"
                    updated_lines.append(updated_line)
                else:
                    # Keep the original line if parameter is not in free_params
                    updated_lines.append(line)
            else:
                # Copy other lines as is
                updated_lines.append(line)

        # Prepare new parameter lines for those not already in the file
        new_param_lines = [
            f"uniform_var = {param} {values[0]} {values[1]}\n"
            for param, values in free_params.items()
            if param not in param_names_in_conf
        ]

        # Insert new parameters after the most recent uniform_var line
        if new_param_lines and last_uniform_var_index != -1:
            updated_lines = (
                updated_lines[:last_uniform_var_index + 1]
                + new_param_lines
                + updated_lines[last_uniform_var_index + 1:]
            )
        elif new_param_lines:
            # If there were no uniform_var lines, append new parameters at the end
            updated_lines.extend(new_param_lines)

        # Write the updated lines back to the configuration file
        with open(conf_file_path, 'w') as file:
            file.writelines(updated_lines)

        print(f"Updated configuration for {state}")
                
def update_conf_file_keys(state_names, config_updates, conf_base_dir):
    """
    Function to update configuration keys in all .conf files for the given states.
    - state_names: A list of state names (e.g., ['Arizona', 'Alabama'])
    - config_updates: The dictionary of config keys and their updated values.
    - conf_base_dir: The directory containing the .conf files.
    """
    for state_name in state_names:
        conf_file = os.path.join(conf_base_dir, f"{state_name}.conf")
        
        # Check if the configuration file exists
        if not os.path.exists(conf_file):
            print(f"File not found: {conf_file}. Skipping {state_name}...")
            continue

        # Read the .conf file
        with open(conf_file, 'r') as file:
            lines = file.readlines()

        # Prepare updated content
        new_lines = []

        for line in lines:
            updated_line = line
            # Check if the line contains a configuration key
            for key, new_value in config_updates.items():
                if line.startswith(key):
                    # Convert new_value to string if it's not already
                    new_value_str = str(new_value)
                    # Update the line with the new value
                    updated_line = f"{key} = {new_value_str}\n"
                    break  # Stop checking once a match is found

            new_lines.append(updated_line)  # Append the (possibly updated) line

        # Write the updated lines back to the .conf file
        with open(conf_file, 'w') as file:
            file.writelines(new_lines)


def add_params_to_bngl(state_names, conf_dir, bngl_dir):
    """
    Adds new parameters from conf files to the BNGL files.

    Args:
        state_names (list): List of state names.
        conf_dir (str): Directory containing the conf files.
        bngl_dir (str): Directory containing the BNGL files.
    """
    # Iterate over each state
    for state in state_names:
        conf_file_path = os.path.join(conf_dir, f"{state}.conf")
        bngl_file_path = os.path.join(bngl_dir, f"{state}.bngl")

        if os.path.exists(conf_file_path) and os.path.exists(bngl_file_path):
            # Read the conf file to find new parameters
            with open(conf_file_path, 'r') as conf_file:
                conf_lines = conf_file.readlines()

            # Extract the parameters to add to the BNGL file
            params_to_add = []
            for line in conf_lines:
                if line.startswith("uniform_var") and "__FREE" in line:
                    parts = line.split()
                    param_name = parts[2].split('=')[0]  # Extract param name
                    param_short = param_name.split('__')[0]  # e.g., b4 from b4__FREE
                    params_to_add.append((param_short, param_name))

            # Read the BNGL file
            with open(bngl_file_path, 'r') as bngl_file:
                bngl_lines = bngl_file.readlines()

            # Check existing parameters in the BNGL file
            existing_params = set()
            inside_param_block = False
            for line in bngl_lines:
                if "begin parameters" in line:
                    inside_param_block = True
                elif "end parameters" in line:
                    inside_param_block = False
                elif inside_param_block:
                    if " " in line:  # Check for spaces to ensure it's a parameter line
                        existing_param = line.split()[0]  # Get the first part of the line (the param name)
                        existing_params.add(existing_param)

            # Prepare the updated BNGL lines
            updated_bngl_lines = []
            inside_param_block = False
            for line in bngl_lines:
                updated_bngl_lines.append(line)
                if "begin parameters" in line:
                    inside_param_block = True
                elif "end parameters" in line and inside_param_block:
                    # Add the new parameters here, above "end parameters"
                    for short_name, full_name in params_to_add:
                        if short_name not in existing_params:  # Only add if it's not already present
                            updated_bngl_lines.insert(-1, f"{short_name} {full_name}\n")  # No equals sign
                    inside_param_block = False  # Exit parameter block

            # Write the updated content back to the BNGL file
            with open(bngl_file_path, 'w') as bngl_file:
                bngl_file.writelines(updated_bngl_lines)

        else:
            print(f"Skipping {state}: Missing conf or bngl file.")



def update_beta_function(base_bngl_dir, params_to_add, user_defined_beta):
    global global_params_added  # Reference the global list

    # Loop through each BNGL file in the specified directory
    for filename in os.listdir(base_bngl_dir):
        if filename.endswith('.bngl'):
            bngl_file_path = os.path.join(base_bngl_dir, filename)
            print(f"Processing {bngl_file_path}")

            # Read the BNGL file
            with open(bngl_file_path, 'r') as bngl_file:
                bngl_lines = bngl_file.readlines()

            # Update the beta() function
            beta_found = False
            new_beta_steps = []
            for short_name, _ in params_to_add:
                if short_name.startswith("b") and short_name not in [param[0] for param in global_params_added]:
                    new_beta_steps.append(short_name)

            # Replace the beta() function with the user-defined one
            beta_function_lines = []
            in_beta_function = False
            for line in bngl_lines:
                if "beta()=" in line:
                    in_beta_function = True
                    beta_function_lines.append("beta()=" + user_defined_beta + "\n")
                if in_beta_function and "0))" in line:
                    in_beta_function = False
                    continue  # Skip original beta function lines
                if not in_beta_function:
                    beta_function_lines.append(line)

            # Write the updated content back to the BNGL file
            with open(bngl_file_path, 'w') as bngl_file:
                bngl_file.writelines(beta_function_lines)

        else:
            print(f"Skipping {filename}: Not a BNGL file.")


def update_simulation_actions(base_bngl_dir, t_start, t_end, n_steps):
    # Loop through each .bngl file in the directory
    for file_name in os.listdir(base_bngl_dir):
        if file_name.endswith(".bngl"):
            bngl_file_path = os.path.join(base_bngl_dir, file_name)
            
            # Read the content of the .bngl file
            with open(bngl_file_path, 'r') as bngl_file:
                bngl_lines = bngl_file.readlines()
            
            # Update simulation actions by finding the specific line to modify
            inside_actions_block = False
            updated_bngl_lines = []
            for line in bngl_lines:
                # Detect the beginning and end of the actions block
                if "begin actions" in line:
                    inside_actions_block = True
                elif "end actions" in line:
                    inside_actions_block = False
                
                # Check if we're inside the actions block and looking at the simulate action
                if inside_actions_block and "simulate({" in line:
                    # Use regex to replace the values of t_start, t_end, and n_steps
                    line = re.sub(r't_start=>\d+', f't_start=>{t_start}', line)
                    line = re.sub(r't_end=>\d+', f't_end=>{t_end}', line)
                    line = re.sub(r'n_steps=>\d+', f'n_steps=>{n_steps}', line)
                
                # Add the (possibly modified) line back to the list
                updated_bngl_lines.append(line)
            
            # Write the modified content back to the .bngl file
            with open(bngl_file_path, 'w') as bngl_file:
                bngl_file.writelines(updated_bngl_lines)
            
            print(f"Updated simulation actions for {file_name}.")



# Define directories and file paths
state_names = {
    "District_of_Columbia": "DC",
    "Puerto_Rico": "PR",
    "Florida": "FL",
    "Alabama": "AL",
    "Alaska": "AK",
    "Arkansas": "AR",
    "Arizona": "AZ",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Iowa": "IA",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Massachusetts": "MA",
    "Maryland": "MD",
    "Maine": "ME",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Missouri": "MO",
    "Mississippi": "MS",
    "Montana": "MT",
    "North_Carolina": "NC",
    "North_Dakota": "ND",
    "Nebraska": "NE",
    "New_Hampshire": "NH",
    "New_Jersey": "NJ",
    "New_Mexico": "NM",
    "Nevada": "NV",
    "New_York": "NY",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode_Island": "RI",
    "South_Carolina": "SC",
    "South_Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West_Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Configuration keys that will be updated
config_updates = {
    "bng_command": "/opt/anaconda3/lib/python3.12/site-packages/bionetgen/bng-mac/BNG2.pl",
    "fit_type": "am",
    "objfunc": "neg_bin_dynamic",
    "step_size": 0.02,
    "population_size": 1,
    "parallel_count": 1,
    "verbosity": 0,
    "burn_in": 1500,
    "adaptive": 1500,
    "max_iterations": 70000,
    "continue_run": 1,
    "sample_every": 1,
    "output_noise_trajectory": "H_weekly",
    "refine": 0,
}

free_params = {    # uniform_var with range values for multiple parameters
    "b0__FREE" : np.array([0.05, 2.0]),
    "b1__FREE": np.array([0.05, 2.0]),
    "mult__FREE": np.array([1.0, 9000]),
    "gamma__FREE": np.array([0.01, 1.2]),
    "t0__FREE": np.array([0, 7]),
    "t1__FREE": np.array([8, 22]),
    "r__FREE": np.array([20, 4000]),
    #"c__FREE": np.array([-200, 50])
    # Add more parameters as needed
}
#dont edit this
global_params_added = []


conf_base_dir = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/conf_files"
base_dir = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/results"  # Base directory where state directories are located
base_conf_dir = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/conf_files"  # Base directory where .conf files are located
output_file_AMCMC = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/State_MLEs_AMCMC.txt"
output_file_DE = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/State_MLEs_DE.txt"
template_conf_file = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/template_conf/Alabama.conf"  # Path to the template .conf file
template_state_name = "Alabama"  # The state name used in the template
base_bngl_dir = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/model_files"
template_bngl_file = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/template_bngl/Alabama.bngl"

user_defined_beta = (
    "if(t>=t0 && t<t0+t1,b0,\\\n"
    "if(t>=t0+t1,b1,\\\n"
	"0))\n"
)
#user_defined_beta = (
  #  "if(t>=t0 && t<t0+t1,b0,\\\n"
   # "if(t>=t0+t1 && t<t0+t1+t2,b1,\\\n"
   # "if(t>=t0+t1+t2 && t<t0+t1+t2+t3,b2,\\\n"
    #"if(t>=t0+t1+t2+t3 && t<t0+t1+t2+t3+t4,b3,\\\n"
    #"if(t>=t0+t1+t2+t3+t4,b4,\\\n"
    #"0)))))\n"
#)


# 1. Check and create conf and BNGL files for all 50 states if missing
#check_and_create_files(state_names, template_conf_file, template_bngl_file, conf_base_dir, base_bngl_dir, template_state_name)

# 2.1. Generate combined MLE file based on second row of params_0.txt files for AMCMC runs
generate_combined_mle_file_AMCMC(state_names, base_dir, output_file_AMCMC)

# 2.2. Generate combined MLE file based on second row of sorted_parms_fimal.txt files for DE runs
#generate_combined_mle_file_DE(state_names, base_dir, output_file_DE)

# 3.1. Update conf files with starting_params from combined MLE file for AMCMC
update_starting_params_from_mle_AMCMC(state_names, base_conf_dir, output_file_AMCMC)

# 3.2. Update conf files with starting_params from combined MLE file for DE
#update_starting_params_from_mle_DE(state_names, base_conf_dir, output_file_DE)

# 4. Update conf files with new free_params
#update_conf_with_free_params(state_names, base_conf_dir)

#5. Update conf files with new keys
update_conf_file_keys(state_names, config_updates, conf_base_dir)

# 6. Add new parameters to the BNGL files
#add_params_to_bngl(state_names, base_conf_dir, base_bngl_dir)

# 7. Update the beta() function in the BNGL files
#update_beta_function(base_bngl_dir, global_params_added, user_defined_beta)

#8. Update simulation actions in the BNGL files
update_simulation_actions(base_bngl_dir, 0, 32, 32)