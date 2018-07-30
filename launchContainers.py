import docker
import argparse
import os

client= docker.from_env()

# //TODO kill only those containers which are on the network ansible.test
#check running containers and kill them all 
def killHostContainers():
    for container in client.containers.list(all=True, filters={"name": r"[ansiblehost|host]\d*"}):
        print (container, "\t", "killed")
        container.remove(force=True)
    print ("cleaned up all containers...")

#launch host containers
def launchHosts(nhosts):
    for i in range(1, nhosts+1):
        hostname= "host"+str(i)
        client.containers.run(image="sudeepgupta90/ubuntuhost", detach=True, hostname= hostname, name=hostname, network="ansible.test")
    print (str(nhosts) + " ubuntu host containers have been launched")

#launch ansible host
def launchAnsibleHost(mountDirectory):
    client.containers.run(image="sudeepgupta90/dockeransible", detach=True, tty=True,hostname="ansiblehost", name="ansiblehost", network="ansible.test", volumes={mountDirectory:{"bind":"/mnt"}} )
    print ("ansible host is launched...")

#creates ansible hosts file in the code directory itself
def createAnsibleHostsFile():
    from jinja2 import Template
    ll_client= docker.APIClient(base_url="unix:///var/run/docker.sock ")
    
    template= """{% for host in hosts -%}{{host.name}} ansible_host={{host.ipaddress}} ansible_user=root \n{% endfor -%}"""
    t= Template(template)
    container_li=[]
    for container in ll_client.containers(filters={"name": r"host\d+"}):
        container_dict= {"name":container["Names"][0].split("/")[-1], "ipaddress":container["NetworkSettings"]["Networks"]["ansible.test"]["IPAddress"]}
        container_li.append(container_dict)
    with open("hosts", "w") as f:
        f.write(t.render(hosts=container_li))
    print ("\nhosts file for Ansible has been generated!")

#factory function which launches all the hosts
def containerFactory(hosts, mountDirectory):
    print ("connecting to docker hub for latest image...")
    for image in ["sudeepgupta90/dockeransible", "sudeepgupta90/ubuntuhost"]:
        client.images.pull(image)
    #launch both containers
    print ("launching host containers...")
    launchHosts(hosts)
    launchAnsibleHost(mountDirectory)    
    print ("host containers and ansible container have been launched!")
    createAnsibleHostsFile()

#setup network essentials for the docker continaer hosts
def setNetwork():
    network= client.networks.list(names=["ansible.test"])
    if len(network) == 0:
        client.networks.create(name="ansible.test", driver="bridge")
        print ("network ansible.test created")
    elif len(network) == 1:
        network[0].remove()
        print ("cleaned up pre-existing ansible network...")
        client.networks.create(name="ansible.test", driver="bridge")
        print ("network ansible created")
    elif networkCheck > 1:
        print ("too many networks present here...kill them manually?!")

#perform cleanup
def cleanup():
    killHostContainers()
    
    print ("host and ansible containers removed from memory")
    
    try:
        network= client.networks.list(names=["ansible.test"])
        network[0].remove()
        print ("network removed!")
    except:
        print ("network does not exists, or cleaned up already!")

    print ("remove residuals from directory manually \n")


#test codes
if __name__ == "__main__":

    parser= argparse.ArgumentParser(description="launch Ansible host containers...")
    parser.add_argument('--setup', action="store", dest="setup", type=int, help="number of hosts to setup")
    parser.add_argument('--clean', action="store_true", dest="cleanup",default=False, help="clean up all existing hosts and network")

    results = parser.parse_args()

    if results.setup:
        print ("\npreparing setup...\n")
        killHostContainers()
        setNetwork()
       
        #creates ansible directory in current working directory, place your ansible code here
        path= os.getcwd()
        ansible_path=path+"/ansible"
        if "ansible" not in os.listdir():
            os.mkdir(ansible_path)
        
        hosts=results.setup
        containerFactory(hosts=hosts, mountDirectory=ansible_path)
        
        print ("\n\nlogin to ansible host use the command: \n\n \t docker exec -it ansiblehost /bin/ash")
        print ("\ncd to /mnt to find your ansible configuration plays/roles inside the container \n\n")
    elif cleanup:
        print ("\npreparing cleanup of existing containers and networks...\n")
        cleanup()
