path='/Users/l-biosci-posnerlab/Documents/test_bills_model/results/'
#extract the folders in the path
import os
import numpy as np

folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
print(folders)

output_folder = '/adaptive_files/'
for i in range(len(folders)):
    os.makedirs(path+folders[i]+output_folder, exist_ok=True)
    data=np.loadtxt(path+folders[i]+'/Results/sorted_params_final.txt', skiprows=1, usecols=range(1, 13))
    print(folders[i])
    #find the index of the largest value in the first column
    max_index = np.argmax(data[:,0])
    mle_estimate = data[max_index,1:]
    #convert mle_estimate to a diagonal matrix
    mle_M = np.diag(mle_estimate)
    #save the matrix as a text file
    np.savetxt(path+folders[i]+'/adaptive_files/diffMatrix.txt', mle_M, fmt='%1.4f')
    #save the transpose of mle_estimate as a text file
    np.savetxt(path+folders[i]+'/adaptive_files/MLE_params.txt', mle_estimate, fmt='%1.4f')
    #save the diff value as a text file
    diff=0.01
    np.savetxt(path+folders[i]+'/adaptive_files/diff.txt', [diff], fmt='%1.4f')
