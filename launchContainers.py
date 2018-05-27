import docker

client= docker.from_env()
client.containers.run("ubuntu:16.04", "echo hello world")
