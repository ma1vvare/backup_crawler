import subprocess
import time

start = time.time()
for i in range(0,30,8):
    subprocess.call(["python","muti_download.py",str(i),str(i+8)])
    time.sleep(60)
end = time.time()
print 'totoal use ',end - start,'s'
