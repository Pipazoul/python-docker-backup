import docker
import os
import time
import json

## General conf
backupFolder = "./backup"


dockerClient = docker.from_env()
containers = dockerClient.containers.list()


volumesToBackup = []

# clear function
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# check if backup folder exists
if not os.path.exists(backupFolder):
    os.makedirs(backupFolder)
    

print("Listing containers")
for container in containers:    
    # add volume to backup list {name: container_name, path: volume_path}
    for volume in container.attrs['Mounts']:
        # check folder size
        # check if volume is a bind mount
        if volume['Type'] != "bind":
            print("Skipping bind mount " + volume['Source'])
        else:
            print("Adding volume " + volume['Source'] + " to backup list")
            # get folder size
            folderSize = os.path.getsize(volume['Source'])
            print("Folder size: " + str(folderSize) + " bytes")
            volumesToBackup.append({'name': container.name, 'path': volume['Source'], 'containerId': container.id, 'size': folderSize})
time.sleep(1)
clear()
print("--------------------")
print("##Volumes to backup##")
folderSize = 0
for volume in volumesToBackup:
    print(volume['name'] + " - " + volume['path'] + "\n")
    # add folder size
    folderSize += volume['size']
print("--------------------")
print("Total size: " + str(folderSize) + " bytes")
# convert bytes to human readable format
print("Total size: " + str(round(folderSize / 1024 / 1024, 2)) + " MB")
# convert to GB
print("Total size: " + str(round(folderSize / 1024 / 1024 / 1024, 2)) + " GB")

# ask user to confirm backup
confirm = input("Do you want to continue? [y/n]")
# if user confirm backup
if confirm == "y":
    # get date and time (dd-mm-yy-time) and add it to backup folder name
    currentDateTime = time.strftime("%d-%m-%y-%H-%M")
    backupFolder = backupFolder + "/" + currentDateTime
    for volume in volumesToBackup:
        clear()
        # stop container
        print("Stopping container " + volume['name'])
        dockerClient.containers.get(volume['containerId']).stop()
        # create backup folder if not exists
        if not os.path.exists(backupFolder + "/" + volume['name']):
            os.makedirs(backupFolder + "/" + volume['name'])
        # create tar.gz file use --directory= to set the root folder
        os.system("tar -czf " + backupFolder + "/" + volume['name'] + "/" + volume['name'] + ".tar.gz " + volume['path'])
        print("Backup done for " + volume['name'])
        # start container
        print("Starting container " + volume['name'])
        dockerClient.containers.get(volume['containerId']).start()
    # save volumes to backup into a json file
    json.dump(volumesToBackup, open(backupFolder + "/volumes.json", "w"))

else:
    print("Backup canceled")



    
    
    