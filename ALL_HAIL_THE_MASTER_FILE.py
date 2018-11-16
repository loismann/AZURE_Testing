import HKS_DeleteAzureResources as delete
import HKS_LaunchMultipleVM as launch_vm
import HKS_PrepDGP as launch_sims





# Where are the Honeybee Files?
Local_Main_Directory = r"C:\Users\pferrer\Desktop\test"
# Local_Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"

# Where is the code stored? (This is needed to point to the Local_IP_Address file)
# Local_Repo_Directory = "/Users/paulferrer/PycharmProjects/Azure_Testing/AZURE_Testing/HELPERS/"
Local_Repo_Directory = r"C:\Users\pferrer\PycharmProjects\AZURE_Testing"

# Where are the HDR files going to be copied back to the local computeR?
Local_HDR_Directory = r"C:\Users\pferrer\Desktop\TEST_CopiedHDRfiles"

# How Many Virtual Machines do you want?
vm_count = 50

#Master ON/OFF switch
Turn_On_All = True




if __name__ == "__main__":

    # # #Delete any existing VM's
    print("Looking for Existing Azure Resources...")
    delete.main(Local_Repo_Directory)
    # # #
    # # # #Run the VM Creation Method (Number of VM, Type of VM, Run Yes/No? Default = No
    print("Spinning Up Virtual Machines")
    launch_vm.main(vm_count)

    # Copy over files and run the simulations
    launch_sims.main(Local_Main_Directory,Local_HDR_Directory)