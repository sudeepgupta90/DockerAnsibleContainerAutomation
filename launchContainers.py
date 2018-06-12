import docker

client= docker.from_env()

# use low level api to map container ip's and hostname


# from jinja2 import Template
# template= """{% for host in hosts -%}{{host.name}} ansible_host={{host.ipaddress}} ansible_user=root \n{% endfor -%}"""

# t= Template(template)
# #t= Template("""Hellow World! """)
# x=[{"name":"x", "ipaddress":123}, {"name":"y", "ipaddress":1234}]
# print (t.render(hosts=x))


# //TODO kill only those containers which are on the network ansible.test
#check running containers and kill them all 
for container in client.containers.list(all=True, filters={"name": r"[ansiblehost|thost]\d*"}):
    print (container, "\t", "killed")
    container.remove(force=True)
print ("cleaned up all containers...")


#launch containers
def launchHosts(nhosts):
    for i in range(1, nhosts+1):
        hostname= "thost"+str(i)
        client.containers.run(image="sudeepgupta90/ubuntuhost:v1", detach=True, hostname= hostname, name=hostname, network="ansible.test")
    print (str(nhosts) + " ubuntu host containers have been launched")

def launchAnsibleHost(mountDirectory):
    client.containers.run(image="sudeepgupta90/dockeransible:v1", detach=True, tty=True,hostname="ansiblehost", name="ansiblehost", network="ansible.test")
    print ("Ansible host is launched...")

def containerFactory(hosts=4, mountDirectory=""):
    #launch both containers
    launchHosts(hosts)
    launchAnsibleHost(mountDirectory)    
    print ("Host machines and Ansible Container has been launched!")

#check existing Network by the same name and remove
network= client.networks.list(names=["ansible.test"])
if len(network) == 0:
    client.networks.create(name="ansible.test", driver="bridge")
    print ("network ansible created")
elif len(network) == 1:
    network[0].remove()
    print ("cleaned up ansible network!")
    client.networks.create(name="ansible.test", driver="bridge")
    print ("network ansible created")
elif networkCheck > 1:
    print ("too many networks present here...kill them manually?!")

# containerFactory()
