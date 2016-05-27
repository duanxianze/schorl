import os
import sys

dir = "/home/gao/ss"
for f in os.listdir(dir):
    cur_dir = os.path.join(dir, f)
    if os.path.isfile(cur_dir):
        log_dir = os.path.join(dir, 'logs', f)
        print('y')
        os.system('nohup sslocal -c {0} > {1} &'.format(cur_dir, log_dir))
    else:
        print('n')
    print('---')
