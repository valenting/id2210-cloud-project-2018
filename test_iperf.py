from functions import *

# Task 2.3
delete_instances()
r = create_instance(client(), PROJECT, "us-east1-b", "server")
wait_for_operation(r)

runCommand("server", "us-east1-b", "kill -SIGKILL $(pidof iperf) || true", True) # cleanup
time.sleep(30) # wait for iperf to be installed

ip = getExternalIP("server", "us-east1-b")
runCommand("server", "us-east1-b", "nohup iperf -s -p 2222 &> /tmp/iperf1.txt &", True)

os.system("iperf -c "+ip+" -p 2222")

runCommand("server", "us-east1-b", "kill -SIGINT $(pidof iperf) || true", True) # cleanup
runCommand("server", "us-east1-b", "cat /tmp/iperf1.txt", True)

runCommand("server", "us-east1-b", "nohup iperf -u -s -p 2222 &> /tmp/iperf1.txt &", True)
os.system("iperf -u -c "+ip+" -p 2222 -b 1000m")

runCommand("server", "us-east1-b", "kill -SIGINT $(pidof iperf) || true", True) # cleanup
runCommand("server", "us-east1-b", "cat /tmp/iperf1.txt", True)

delete_all_instances() # shutdown everything
