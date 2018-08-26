# DockerAnsibleContainerAutomation

This project aims to remove the entry barrier to developing for Ansible and allows you to create a network of docker containers with pre-configured hosts lookup and passwordless ssh login to jumpstart your development of Ansible codes.

The python script does the following:-

  - create a subnet on docker "bridge" network
  - launch containers on the new subnet
  - the containers have been pre-built with a ssh key, so it allows passwordless login
  - the subnet allows the docker containers with automatic host lookups, and communication is open on all ports within the subnet
  - deploy your ansible playbooks/roles in "ansible" directory
    - a hosts file is automatically generated in the directory where the python script is placed. copy it to ansible directory
    - you then login to the ansiblehost container for which the command is generated as well, and begin developing with ansible

The script takes as arguments two command line options:
  -- setup (int) number of host container you want to launch
  -- cleanup will perform cleanup

To use the script, first place the script in some folder where you want to develop with ansible. The script automatically creates a folder named “ansible” for you to start developing later when you setup.
