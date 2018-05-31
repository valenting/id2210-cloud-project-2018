from functions import *

INSTANCE = "instance-name-1"
REPEATCOUNT = 5

create_all() # creates all storage buckets

# # #
delete_instances()
r = create_instance(client(), PROJECT, ZONE, INSTANCE)
wait_for_operation(r)


# Mount all of the buckets as local filesystems
storage_client = sClient()
buckets = list(storage_client.list_buckets())
for b in buckets:
  runCommand(INSTANCE, ZONE, "mkdir mount-"+b.name)
  runCommand(INSTANCE, ZONE, "gcsfuse "+b.name+" mount-"+b.name)

pushFile(INSTANCE, ZONE, "generate_file.py")
pushFile(INSTANCE, ZONE, "read_file.py")

def avg_op_speed(instance, zone, bucket_name, script, file_count, repeat_count):
  avg = 0.0
  for r in range(repeat_count):
      commands = ""
      for i in range(file_count):
        fname = str(uuid.uuid4()) + ".blob"
        commands += "python "+script+" "+bucket_name+"/"+fname+" &\n"
      commands += "wait"

      startTime = time.time()
      runCommand(instance, zone, commands, False, False)
      duration = time.time() - startTime

      avg += 100*file_count / duration
  return avg/repeat_count


def bench(instance, zone, bucket_name, file_count):
  avg = avg_op_speed(instance, zone, bucket_name, "generate_file.py", file_count, REPEATCOUNT)
  print("Write speed (bucket: %s parralel_count:%d): %.2f MBps" % (bucket_name, file_count, avg))
  avg = avg_op_speed(instance, zone, bucket_name, "read_file.py", file_count, REPEATCOUNT)
  print("Read speed (bucket: %s parralel_count:%d): %.2f MBps" % (bucket_name, file_count, avg))

# Benchmark access to the buckets
for b in buckets:
  bench(INSTANCE, ZONE, "mount-"+b.name, 1)
  bench(INSTANCE, ZONE, "mount-"+b.name, 2)
  bench(INSTANCE, ZONE, "mount-"+b.name, 4)

# Unmount the buckets
for b in buckets:
  runCommand(INSTANCE, ZONE, "sudo umount mount-"+b.name)
  runCommand(INSTANCE, ZONE, "rmdir mount-"+b.name)

# Bench the local disk
bench(INSTANCE, ZONE, ".", 1)
bench(INSTANCE, ZONE, ".", 2)
bench(INSTANCE, ZONE, ".", 4)

# Bench the local SSD
runCommand(INSTANCE, ZONE, "mkdir ssd")
runCommand(INSTANCE, ZONE, "sudo mkfs.ext4 -F /dev/sdb")
runCommand(INSTANCE, ZONE, "sudo mount /dev/sdb ssd")
runCommand(INSTANCE, ZONE, "sudo chmod a+w ssd")

bench(INSTANCE, ZONE, "ssd", 1)
bench(INSTANCE, ZONE, "ssd", 2)
bench(INSTANCE, ZONE, "ssd", 4)

runCommand(INSTANCE, ZONE, "sudo umount ssd")

# cleanup
delete_instances() # shutdown everything

delete_all() # deletes all storage buckets