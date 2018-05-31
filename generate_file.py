import uuid
import os
import sys

def generate_file(path, size = 100):
  chunk = ""
  for i in range(256):
    chunk += chr(i)
  buff = ""
  for i in range(4*1024):
    buff += chunk

  with open(path, 'wb') as fout:
    for i in range(size):
      fout.write(buff)


generate_file(sys.argv[1])