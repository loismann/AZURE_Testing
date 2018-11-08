import HKS_DeleteAzureResources as delete
import HKS_LaunchMultipleVM as launch_vm
import HKS_PrepDGP as  launch_sims





# Where are the Honeybee Files?
Local_Main_Directory = "/Users/paulferrer/Desktop/DGP_TestFiles"

# How Many Virtual Machines do you want?
vm_count = 5

#Master ON/OFF switch
Turn_On_All = True






#Delete any existing VM's
print("Looking for Existing Azure Resources...")
delete.main(Turn_On_All)

#Run the VM Creation Method (Number of VM, Type of VM, Run Yes/No? Default = No
print("Spinning Up Virtual Machines")
launch_vm.main(vm_count)

# Copy over files and run the simulations
launch_sims.main(Local_Main_Directory)