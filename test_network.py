from functions import *

endpoints = [
  "us-east1-b",
  "us-east1-c",
  "us-east4-a",
  "europe-west4-a",
  "australia-southeast1-b",
]

delete_all_instances()

# Task 2.3
operations = []
r1 = create_instance(client(), PROJECT, "us-east1-b", "server")
operations.append(r1)

for e in endpoints:
  r2 = create_instance(client(), PROJECT, e, e)
  operations.append(r2)

for op in operations:
  wait_for_operation(op)

ip = getExternalIP("server", "us-east1-b")

time.sleep(30) # wait for iperf to be installed

# test TCP
runCommand("server", "us-east1-b", "nohup iperf -s -p 2222 &> /tmp/iperf1.txt &", True)
for e in endpoints:
  runCommand(e, e, "iperf -c " + ip + " -p 2222", True)
runCommand("server", "us-east1-b", "kill -SIGKILL $(pidof iperf) || true", True) # cleanup

# test UDP
runCommand("server", "us-east1-b", "nohup iperf -u -s -p 2222 &> /tmp/iperf1.txt &", True)
for e in endpoints:
  runCommand(e, e, "iperf -u -c " + ip + " -p 2222 -b 5000m", True)
runCommand("server", "us-east1-b", "kill -SIGKILL $(pidof iperf) || true", True)

delete_all_instances() # shutdown everything
