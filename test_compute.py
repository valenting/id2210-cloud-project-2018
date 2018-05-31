from functions import *

# Task 2.3
delete_instances()
r = create_instance(client(), PROJECT, "us-east1-b", "instance-name-1")
wait_for_operation(r)

test_connectivity()

delete_instances() # shutdown everything
