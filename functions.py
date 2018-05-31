import os.path
import os
import uuid
from google.cloud import storage
import time
import threading

import os
import googleapiclient.discovery
from google.oauth2 import service_account
import time

from io import StringIO
import paramiko

import socket

testcases = [
  { "location": "us-east1", "storage_class": "REGIONAL"},
  { "location": "europe-west1", "storage_class": "REGIONAL"},
  { "location": "australia-southeast1", "storage_class": "REGIONAL"},
  { "location": "eu", "storage_class": "MULTI_REGIONAL"},
  { "location": "us", "storage_class": "MULTI_REGIONAL"},
]

def sClient():
  if os.path.isfile("service_account_credentials.json"):
    storage_client = storage.Client.from_service_account_json('service_account_credentials.json')
  elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    storage_client = storage.Client()
  else:
    raise RuntimeError('No credentials file or ENV var found')
  return storage_client

def delete_all():
  storage_client = sClient()
  buckets = list(storage_client.list_buckets())
  for b in buckets:
    b.delete(True) # delete buckets and uploaded files as well
  print("Deleted buckets:", buckets)

def create_all():
  storage_client = sClient()
  for test in testcases:
    bucket_name = "vt18-g3-" + test["location"] + "-" + test["storage_class"]
    bucket = storage_client.bucket(bucket_name.lower()) # name must be lowercase
    # location and class can't be changed after creating the bucket, so we set them first
    bucket.location = test["location"]
    bucket.storage_class = test["storage_class"]
    bucket.create()
    print('Bucket {} created.'.format(bucket.name))

def generate_file(size = 100*1024*1024):
  unique_filename = str(uuid.uuid4()) + ".blob"
  with open(unique_filename, 'wb') as fout:
    fout.write(os.urandom(size))
  return unique_filename

def upload_blob(bucket_name, source_file_name, destination_blob_name):
  """Uploads a file to the bucket."""
  storage_client = sClient()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)

  startTime = time.time()
  blob.upload_from_filename(source_file_name)
  duration = time.time() - startTime
  # print('File {} uploaded to {}.'.format(
  #     source_file_name,
  #     destination_blob_name))
  return duration

def delete_blob(bucket_name, blob_name):
  """Deletes a blob from the bucket."""
  storage_client = sClient()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(blob_name)
  blob.delete()
  print('Blob {} deleted.'.format(blob_name))

def download_blob(bucket_name, source_blob_name, destination_file_name):
  """Downloads a blob from the bucket."""
  storage_client = sClient()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(source_blob_name)

  startTime = time.time()
  blob.download_to_filename(destination_file_name)
  duration = time.time() - startTime
  # print('Blob {} downloaded to {}.'.format(
  #       source_blob_name,
  #       destination_file_name))
  return duration

def up_down_file(bucket_name):
  newfile = generate_file()
  file_size = os.stat(newfile)
  timeU = upload_blob(bucket_name, newfile, newfile)
  timeD = download_blob(bucket_name, newfile, newfile + ".download")
  os.remove(newfile)
  os.remove(newfile + ".download")
  return (timeU, timeD)

def up_file(bucket_name, index, files, timesU):
  timeU = upload_blob(bucket_name, files[index], files[index])
  timesU[index] = timeU

def down_file(bucket_name, index, files, timesD):
  timeD = download_blob(bucket_name, files[index], files[index] + ".download")
  timesD[index] = timeD

def waitForThreads():
  main_thread = threading.currentThread()
  for t in threading.enumerate():
    if t is not main_thread:
      t.join()

def up_down_file_parallel(bucket_name, threadCount):
  files = []
  resultsU = [None] * threadCount
  resultsD = [None] * threadCount

  for i in range(threadCount):
    files.append(generate_file())

  startTime = time.time()
  for i in range(threadCount):
    t = threading.Thread(target=up_file, args=(bucket_name, i, files, resultsU))
    t.start()
  waitForThreads()
  duration = time.time() - startTime

  print("Upload speed (bucket: %s, %d threads): %.2f MBps" % (bucket_name, threadCount, threadCount * 100  / duration))

  startTime = time.time()
  for i in range(threadCount):
    t = threading.Thread(target=down_file, args=(bucket_name, i, files, resultsD))
    t.start()
  waitForThreads()
  duration = time.time() - startTime
  print("Download speed (bucket: %s, %d threads): %.2f MBps" % (bucket_name, threadCount, threadCount * 100 / duration))

  for f in files:
    os.remove(f)
    os.remove(f + ".download")


def bench_up_down():
  storage_client = sClient()
  buckets = list(storage_client.list_buckets())
  for b in buckets:
    up_down_file_parallel(b.name, 1)
    up_down_file_parallel(b.name, 2)
    up_down_file_parallel(b.name, 4)

# COMPUTE

def sshKey():
    if os.path.isfile("paramiko_rsa"):
        return paramiko.RSAKey.from_private_key_file("paramiko_rsa")
    else:
        key = paramiko.RSAKey.generate(4096)
        key.write_private_key_file("paramiko_rsa")
        return key

def client():
  if os.path.isfile("service_account_credentials.json"):
    credentials = service_account.Credentials.from_service_account_file('service_account_credentials.json')
    compute_client = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
  elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    compute_client = googleapiclient.discovery.build('compute', 'v1')
  else:
    raise RuntimeError('No credentials file or ENV var found')
  return compute_client

PROJECT = "id2210-vt18-group3"
ZONE = "us-east1-b"
USER = "valentin_gosu"

def wait_for_operation(operation):
    compute = client()
    print('Waiting for operation to finish...')
    zone = operation["zone"].split("/")[-1]
    while True:
        result = compute.zoneOperations().get(
            project=PROJECT,
            zone=zone,
            operation=operation["name"]).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)

def list_instances(zone=ZONE):
  compute = client()
  result = compute.instances().list(project=PROJECT, zone=zone).execute()
  instances = []
  if "items" in result:
    for inst in result["items"]:
      instances.append(inst["name"])
  return instances


ALL_ZONES = [
  "us-east1-b",
  "us-east1-c",
  "us-east1-d",
  "us-east4-c",
  "us-east4-b",
  "us-east4-a",
  "us-central1-c",
  "us-central1-a",
  "us-central1-f",
  "us-central1-b",
  "us-west1-b",
  "us-west1-c",
  "us-west1-a",
  "europe-west4-a",
  "europe-west4-b",
  "europe-west4-c",
  "europe-west1-b",
  "europe-west1-d",
  "europe-west1-c",
  "europe-west3-b",
  "europe-west3-c",
  "europe-west3-a",
  "europe-west2-c",
  "europe-west2-b",
  "europe-west2-a",
  "asia-east1-b",
  "asia-east1-a",
  "asia-east1-c",
  "asia-southeast1-b",
  "asia-southeast1-a",
  "asia-southeast1-c",
  "asia-northeast1-b",
  "asia-northeast1-c",
  "asia-northeast1-a",
  "asia-south1-c",
  "asia-south1-b",
  "asia-south1-a",
  "australia-southeast1-b",
  "australia-southeast1-c",
  "australia-southeast1-a",
  "southamerica-east1-b",
  "southamerica-east1-c",
  "southamerica-east1-a",
  "northamerica-northeast1-a",
  "northamerica-northeast1-b",
  "northamerica-northeast1-c",
]

def delete_all_instances():
  compute = client()
  operations = []
  for zone in ALL_ZONES:
    instances = list_instances(zone)
    for inst in instances:
      r = compute.instances().delete(project=PROJECT, zone=zone, instance=inst).execute()
      operations.append(r)
  for op in operations:
    wait_for_operation(op)

def delete_instances(zone=ZONE):
  compute = client()
  instances = list_instances(zone)
  operations = []
  for inst in instances:
    r = compute.instances().delete(project=PROJECT, zone=zone, instance=inst).execute()
    operations.append(r)
  for op in operations:
    wait_for_operation(op)

def create_instance(compute, project, zone, name):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='debian-cloud', family='debian-8').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    ssd_disk_type = "projects/%s/zones/%s/diskTypes/local-ssd" % (project, zone)

    startup_script = open('startup_script.sh', 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"
    key = sshKey()
    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                "type":"PERSISTENT",
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            },
            {
               "type":"SCRATCH",
               "initializeParams":{
                  "diskType": ssd_disk_type
               },
               "autoDelete": True,
               "interface": "SCSI",
               'boot': False,
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],
        # "canIpForward": True,
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                "https://www.googleapis.com/auth/devstorage.full_control",
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            "kind": "compute#metadata",
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'ssh-keys',
                "value": USER + ":ssh-rsa " + key.get_base64() + " " + USER + "@paramiko"
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


def getExternalIP(name, zone=ZONE):
    # Code from https://stackoverflow.com/a/19871956
    def findkeys(node, kv):
        if isinstance(node, list):
            for i in node:
                for x in findkeys(i, kv):
                   yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in findkeys(j, kv):
                    yield x

    compute = client()
    result = compute.instances().list(project=PROJECT, zone=zone).execute()
    instances = []
    if "items" in result:
        for inst in result["items"]:
          if inst["name"] == name:
            instances = list(findkeys(inst, 'natIP'))
    return instances[0] # will throw if no IPs found. Should not happen

gSSHSessions = {}

def getSSHSession(name, zone):
    if (name, zone) in gSSHSessions:
        ssh = gSSHSessions[(name, zone)]
    else:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        extIP = getExternalIP(name, zone)
        key = sshKey()
        ssh.connect(extIP, username="valentin_gosu", pkey=key)
        gSSHSessions[(name, zone)] = ssh
    return ssh


def runCommand(name, zone, command, display=False, displayCommand=True):
    if displayCommand:
      print("%s$ %s" % (name, command))
    ssh = getSSHSession(name, zone)
    stdin , stdout, stderr = ssh.exec_command(command)

    output = ""

    s = stdout.read().decode("utf-8")
    if (len(s) > 0):
        output = s
    s = stderr.read().decode("utf-8")
    if (len(s) > 0):
        output += "--- STDERR ---"
        output += s
        output += "--------------"
    if display and len(output) > 0:
      print(output)
    return output.strip()

def pushFile(name, zone, fileName):
    s = getSSHSession(name, zone)
    sftp = s.open_sftp()
    sftp.put(fileName, fileName)
    sftp.close()

def test_connectivity():
    # test TCP
    runCommand("instance-name-1", ZONE, "nc -l -p 2222 &> /tmp/out &", True)
    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    s.connect((getExternalIP("instance-name-1", ZONE), 2222))
    s.send(b"this is a TCP test")
    s.close()
    runCommand("instance-name-1", ZONE, "cat /tmp/out", True)

    # test UDP
    runCommand("instance-name-1", ZONE, "nc -l -u -p 2222 &> /tmp/out &", True)
    s = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((getExternalIP("instance-name-1", ZONE), 2222))
    s.send(b"this is a UDP test")
    s.close()
    runCommand("instance-name-1", ZONE, "cat /tmp/out", True)
