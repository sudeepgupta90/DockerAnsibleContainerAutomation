import docker

#client= docker.from_env()
#client.containers.run("ubuntu:16.04", "echo hello world")
# save container id's

# use low level api to map container ip's and hostname


from jinja2 import Template
template= """{% for host in hosts -%}{{host.name}} ansible_host={{host.ipaddress}} ansible_user=root \n{% endfor -%}"""

t= Template(template)
#t= Template("""Hellow World! """)
x=[{"name":"x", "ipaddress":123}, {"name":"y", "ipaddress":1234}]
print (t.render(hosts=x))


