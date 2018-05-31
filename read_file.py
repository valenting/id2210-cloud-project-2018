import uuid
import os
import sys

def read_file(path):
  with open(path, 'rb') as file:
    buff = file.read(1024*1024)

read_file(sys.argv[1])