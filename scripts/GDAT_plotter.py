import pandas as pd
import matplotlib.pyplot as plt

# --- file paths ---
#exp_file = "/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/exp_files/Alabama_flu.exp"
exp_file = "/Users/elymiller/Desktop/Current_Research/2025_NAU_FLU/exp_files/US_cases.exp"
#gdat_file = "/Users/elymiller/Desktop/covid_model_test/Alabama/Results/Alabama_gen70ind11/2025_09_23__16_51_08/Alabama_gen70ind11_Alabama_flu.gdat"  
gdat_file = "/Users/elymiller/Desktop/Current_Research/2025_NAU_FLU/USA_results/USA/Results/USA_gen28ind3/2026_01_16__12_11_30/USA_gen28ind3_US_cases.gdat"  

##exp_check = "/Users/elymiller/Desktop/covid_model_test/confirm_alabama.exp"

# --- load EXP data ---
with open(exp_file, "r") as f:
    header = f.readline().strip().lstrip("#").split()
exp = pd.read_csv(exp_file, delim_whitespace=True, comment="#", names=header)

#with open(exp_check, "r") as f:
   # header = f.readline().strip().lstrip("#").split()
#check = pd.read_csv(exp_check, delim_whitespace=True, comment="#", names=header)

# --- load GDAT data ---
with open(gdat_file, "r") as f:
    gheader = f.readline().strip().lstrip("#").split()
gdat = pd.read_csv(gdat_file, delim_whitespace=True, comment="#", names=gheader)

# --- align series (weeks) ---
weeks_exp = exp["time"]
h_exp = exp["H_weekly"]  
#weeks_check = check["time"]
#h_check = check["H_weekly"] 
weeks_mod = gdat["time"]
h_mod = gdat["H_weekly"] 


# --- plot ---
plt.figure(figsize=(8,5))
plt.scatter(weeks_exp, h_exp, marker="+", label="EXP data (CDC weekly)", color="red")
#plt.scatter(weeks_check, h_check, marker="+", label="Future EXP data (CDC weekly)", color="green")
plt.plot(weeks_mod, h_mod, "-", label="Model (H_obs)", color="black")

plt.xlabel("Week")
plt.ylabel("Weekly hospitalizations")
plt.title("New Model Check (Alabama)")
plt.legend()
plt.tight_layout()
#plt.savefig("/Users/l-biosci-posnerlab/Desktop/2025_NAU_FLU/current_job/DE_checks/alabama_DE.png", dpi=500)
plt.savefig("/Users/elymiller/Desktop/Current_Research/2025_NAU_FLU/USA_results/USA_DE.png", dpi=500)
