import HKS_DeleteAzureResources as delete
import HKS_LaunchMultipleVM as launch_vm
from HELPERS.HELPER_Login_Info import Login
import HKS_PrepDGP as launch_sims
import time

#Initialize Login Class
login = Login()



# Where are the Honeybee Files?
Local_Main_Directory = login.Local_Main_Directory

# Where is the code stored? (This is needed to point to the Local_IP_Address file)
Local_Repo_Directory = login.Local_Repo_Directory

# Where are the HDR files going to be copied back to the local computeR?
Local_HDR_Directory = login.Local_HDR_Directory

# How Many Virtual Machines do you want?
vm_count = 100

#Master ON/OFF switch
Turn_On_All = True




if __name__ == "__main__":

    print("Starting Timer...")
    start_time = time.time()

    #Delete any existing VM's
    print("Looking for Existing Azure Resources...")
    delete.main(Local_Repo_Directory)

    #Run the VM Creation Method (Number of VM, Type of VM, Run Yes/No? Default = No
    print("Spinning Up Virtual Machines")
    start_time_vm = time.time()
    launch_vm.main(vm_count)
    elapsed_time_vm = int(time.time() - start_time_vm)

    # Copy over files and run the simulations
    start_time_calc = time.time()
    print("Copying Basefiles and Launching Main Calculations")
    launch_sims.main(Local_Main_Directory,Local_HDR_Directory)
    elapsed_time_calc = int(time.time() - start_time_calc)

    # Delete Resources
    start_time_delete = time.time()
    print("Closing Out Job and Deleting Resources...")
    delete.main(Local_Repo_Directory)
    elapsed_time_delete = int(time.time() - start_time_delete)


    total_elapsed_time = int(time.time() - start_time)
    print("Time to Create VMs:" + str(elapsed_time_vm))
    print("Time to Run Calcs:" + str(elapsed_time_calc))
    print("Time to Delete VMs:" + str(elapsed_time_delete))
    print("Total Time Elapsed:" + str(total_elapsed_time))
