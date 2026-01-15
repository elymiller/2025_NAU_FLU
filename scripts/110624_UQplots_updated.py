import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# Set the base directory where all result folders are stored
base_dir = '/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/results'
burn_in = 0.05  # Drop the first 25% of values for burn-in
output_dir = '/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/01-07-26'  # Directory for output PNG files

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List of all state names and abbreviations
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

# Loop through all subdirectories in the base directory
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)

    # Only process if the subdirectory is a directory and matches a state name
    if os.path.isdir(subdir_path) and subdir in state_names:
        print(f"Processing directory: {subdir}")

        state_name = subdir  # Extract the state name from the folder
        state_abbrev = state_names[state_name]  # Look up the abbreviation

        # Dynamically create the paths for traj_file, exp_file, params_file, and combined_params_file
        traj_file = os.path.join(base_dir, state_name, f'Results/A_MCMC/Runs/traj_noise_{state_name}_fluH_weekly_chain_0.txt')
        exp_file = os.path.join('/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/exp_files', f'{state_name}_flu.exp')
        #params_file = os.path.join(base_dir, state_name, 'Results/A_MCMC/Runs/params_0.txt')
        scores_file = os.path.join(base_dir, state_name, 'Results/A_MCMC/Runs/scores_0.txt')
        combined_params_file = os.path.join(base_dir, state_name, 'Results/A_MCMC/Runs/combined_params.txt')

        # Print the paths to verify if they are correct
        print(f"Checking files for {state_name}...")
        print(f"Trajectory file path: {traj_file}")
        print(f"Experiment file path: {exp_file}")
        #print(f"Params file path: {params_file}")
        print(f"Scores file path: {scores_file}")
        print(f"Combined Params file path: {combined_params_file}")

        # Check if the necessary files exist
        if os.path.exists(traj_file) and os.path.exists(exp_file) and os.path.exists(combined_params_file) and os.path.exists(scores_file):
            print(f"Files found for {state_name}, loading data...")

            # Load trajectory data
            try:
                d = np.genfromtxt(traj_file)
                print(f"Loaded trajectory data for {state_name}, shape: {d.shape}")
            except Exception as e:
                print(f"Error loading trajectory data for {state_name}: {e}")
                continue

            # Load observed data
            try:
                obs = np.genfromtxt(exp_file)
                print(f"Loaded observed data for {state_name}, shape: {obs.shape}")
            except Exception as e:
                print(f"Error loading observed data for {state_name}: {e}")
                continue

            # Check if trajectory data has content
            if d.size == 0:
                print(f"Warning: Trajectory data for {state_name} is empty. Skipping plot generation.")
                continue

            # Compute quantiles for uncertainty visualization
            qtlMark = 1.00 * np.array([0.010, 0.025, 0.050, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400, 0.450,
                                       0.500, 0.550, 0.600, 0.650, 0.700, 0.750, 0.800, 0.850, 0.900, 0.950,
                                       0.975, 0.990])
            qtlLog = np.zeros((len(qtlMark), d.shape[1]))
            for i in range(d.shape[1]):
                qtlLog[:, i] = np.quantile(d[:, i], qtlMark)

            # Define time span for the x-axis
            tSpan = np.linspace(0, d.shape[1] - 1, d.shape[1])

            # Create plot for uncertainty quantification
            plt.figure()
            colors = cm.plasma(np.linspace(0, 1, 12))
            for i in range(11):
                plt.fill_between(tSpan, qtlLog[i, :], qtlLog[22 - i, :], facecolor=colors[11 - i], zorder=i)
            plt.scatter(obs[:, 0], obs[:, 1], 10, marker='+', color='k', zorder=500)
            plt.title(f"Uncertainty Quantification for {state_name}")

            # Save plot as PNG
            png_filename = os.path.join(output_dir, f"{state_name}_UQ.png")
            plt.savefig(png_filename)
            plt.close()
            print(f"Plot saved as {png_filename}")
             # --- Scores Plot ---
            if os.path.exists(scores_file):
                try:
                    scores = np.genfromtxt(scores_file)
                    plt.figure()
                    plt.plot(scores, label="Objective Function Score", linewidth=0.8)
                    plt.xlabel("Epoch")
                    plt.ylabel("Objective Function Score")
                    plt.title(f"Trace Plot ({state_name})")
                    plt.legend()
                    png_filename = os.path.join(output_dir, f"{state_name}_chain.png")
                    plt.savefig(png_filename)
                    plt.close()
                except Exception as e:
                    print(f"Error generating scores plot for {state_name}: {e}")

                # --- Correlation Density Plot ---
                # --- Trace Plots for Parameters ---
                if os.path.exists(combined_params_file):
                    try:
                        # Load combined parameters and headers
                        combined_params = np.genfromtxt(combined_params_file, skip_header=1)
                        param_headers = np.genfromtxt(combined_params_file, max_rows=1, dtype=str)
                        
                        # Determine the number of parameters (columns)
                        num_params = combined_params.shape[1]
                        epochs = np.arange(combined_params.shape[0])  # Epochs on the x-axis

                        # Create a figure with subplots for each parameter
                        fig, axes = plt.subplots(nrows=num_params, ncols=1, figsize=(10, 2 * num_params))
                        fig.suptitle(f"{state_name} Parameter Trace Plots", fontsize=14)

                        # Plot each parameter
                        for i, ax in enumerate(axes):
                            ax.plot(epochs, combined_params[:, i], linewidth=0.7)
                            ax.set_ylabel(param_headers[i], fontsize=8)
                            ax.set_xlabel("Epoch", fontsize=8)
                            ax.tick_params(axis='both', which='major', labelsize=6)
                            ax.set_title(f"Trace for {param_headers[i]}", fontsize=8)

                        plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust layout to fit suptitle
                        trace_plot_file = os.path.join(output_dir, f"{state_name}_trace_plots.png")
                        plt.savefig(trace_plot_file, format='png')
                        plt.close(fig)
                        print(f"Trace plots saved as {trace_plot_file}")
                    except Exception as e:
                        print(f"Error generating trace plots for {state_name}: {e}")

                if os.path.exists(combined_params_file):
                    try:
                        # Load combined parameters
                        parLog = np.genfromtxt(combined_params_file, skip_header=1)
                        n = parLog.shape[1]  # Number of parameters

                        # Read the headers
                        header = np.genfromtxt(combined_params_file, max_rows=1, dtype=str)

                        # Dynamically set the figure size based on the number of parameters
                        fig_size = max(10, n * 2)  # Dynamic size based on parameter count
                        fig = plt.figure(figsize=(fig_size, fig_size))
                        ax = [plt.subplot(n, n, i + 1) for i in range(n ** 2)]
                        colors = cm.plasma(np.linspace(0, 1, 12))

                        for i in range(n):
                            for j in range(n):
                                if i == j:
                                    yy, xx = np.histogram(parLog[:, i], bins=30)
                                    xc = 0.5 * xx[:-1] + 0.5 * xx[1:]
                                    ax[i * n + j].bar(xc, yy / (xc[1] - xc[0]) / sum(yy),
                                                      width=xc[1] - xc[0], facecolor=colors[0], lw=0)
                                    ax[i * n + j].set_xlabel(header[i].replace('__FREE', ''), fontsize=8)
                                    ax[i * n + j].set_ylabel('Posterior', fontsize=8)
                                else:
                                    data1 = parLog[:, i]
                                    data2 = parLog[:, j]
                                    ax[i * n + j].hist2d(data2, data1, cmap=cm.plasma, bins=30)
                                    ax[i * n + j].set_xlabel(header[j].replace('__FREE', ''), fontsize=8)
                                    ax[i * n + j].set_ylabel(header[i].replace('__FREE', ''), fontsize=8)

                                # Set the font size for tick labels
                                ax[i * n + j].tick_params(axis='both', which='major', labelsize=6)

                        # Add some space between subplots
                        plt.subplots_adjust(wspace=0.4, hspace=0.4)

                        fig.tight_layout()
                        plt.suptitle(f"Correlation Density for {state_name}", y=1.02)  # Adjust the title position

                        # Save the correlation density plot as a .tiff file
                        correlation_density_file = os.path.join(output_dir, f"{state_name}_density.png")
                        plt.savefig(correlation_density_file, format='png')
                        plt.close(fig)  # Close the figure
                    except Exception as e:
                        print(f"Error generating correlation density plot for {state_name}: {e}")
        else:
            print(f"One or more files are missing for {state_name}, skipping...")
    else:
        print(f"Skipping {subdir} as it is not a matching state directory or is not a directory.")
