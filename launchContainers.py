import docker

client= docker.from_env()

# use low level api to map container ip's and hostname

# //TODO kill only those containers which are on the network ansible.test
#check running containers and kill them all 
def killHostContainers():
    for container in client.containers.list(all=True, filters={"name": r"[ansiblehost|host]\d*"}):
        print (container, "\t", "killed")
        container.remove(force=True)
    print ("cleaned up all containers...")

#launch containers
def launchHosts(nhosts):
    for i in range(1, nhosts+1):
        hostname= "host"+str(i)
        client.containers.run(image="sudeepgupta90/ubuntuhost:v1", detach=True, hostname= hostname, name=hostname, network="ansible.test")
    print (str(nhosts) + " ubuntu host containers have been launched")

def launchAnsibleHost(mountDirectory):
    client.containers.run(image="sudeepgupta90/dockeransible:v1", detach=True, tty=True,hostname="ansiblehost", name="ansiblehost", network="ansible.test", volumes={mountDirectory:{"bind":"/mnt"}} )
    print ("Ansible host is launched...")

def containerFactory(hosts, mountDirectory):
    #launch both containers
    print ("launching host machines...")
    launchHosts(hosts)
    launchAnsibleHost(mountDirectory)    
    print ("host machines and ansible container has been launched!")

#check existing Network by the same name and remove
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
    print ("hosts file for Ansible has been generated!")

def cleanup():
    killHostContainers()
    print ("host and ansible containers removed from memory")
    try:
        network= client.networks.list(names=["ansible.test"])
        network[0].remove()
        print ("network removed!")
    except:
        print ("network does not exists, or cleaned up already!")
#test codes
killHostContainers()
setNetwork()
containerFactory(hosts=10, mountDirectory="/home/sudeep_gupta/ansible")
createAnsibleHostsFile()

print ("\n login to ansible host use the command: \n\n \t docker exec -it ansiblehost /bin/ash")
print ("\n cd to /mnt to find your ansible configuration \n \n")
