import sys
import json
import time
import os
import subprocess
import gdb
import yaml
import re

FILE_PATH = "./config/lock.yaml"
FAULT_TYPE = ['cpu', 'io', 'mem', 'lock', 'slow_sql']
SQL_PARSER = "exec_simple_query"
LOCK_ACQUIRE = "lock.c:771"

lock_step = 0
lock_bp = None

class LockBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super(LockBreakpoint, self).__init__(LOCK_ACQUIRE, gdb.BP_BREAKPOINT)

    def stop(self):
        global lock_step
        frame = gdb.selected_frame()
        locktag = frame.read_var('locktag')
        locktag_field2 = locktag['locktag_field2']
        if lock_step == 1:
            lock_step = 2
            return False
        elif lock_step == 2:
            time.sleep(duration/1000)
            lock_step = 0
            return False
        if locktag_field2 == relation_id:
            print(locktag_field2)
            gdb.parse_and_eval('lockmode=8')
            lock_step = 1
        return False



def inject() -> bool:
    if fault_type == "cpu" or fault_type == "io" or fault_type == "mem":
        gdb.execute(f"print (int)dlclose((long long unsigned)dlopen(\"{path}/inject.so\", 2))")
        return True
    elif fault_type == "slow_sql":
        time.sleep(duration/1000)
        return False
    elif fault_type == "lock":
        global lock_bp
        if lock_bp:
            lock_bp.delete()
        lock_bp = LockBreakpoint()
        return False
        

class FilterBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super(FilterBreakpoint, self).__init__(SQL_PARSER, gdb.BP_BREAKPOINT)

    def stop(self):
        # TODO meet condition
        arg = gdb.parse_and_eval("query_string")
        cur_sql = arg.string()
        if re.search(sql_filter, cur_sql):
            print(sql_filter, cur_sql)
            return inject()
        return False

if __name__ == "__main__":
    with open(FILE_PATH, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    fault_type = data['type']
    args = data['args']
    ip = data['client']['ip']
    port = data['client']['port']
    duration = data['duration']
    sql_filter = data['filter']
    pid = data['pid']
    path = data['process_path']
    print(pid)

    if fault_type not in FAULT_TYPE:
        print("Invalid fault type")
        exit()
    
    if fault_type == "cpu":
        os.system("cp inject-template/cpu-template cpu.cpp")
        os.system(f"sed -i \"s/int TARGET_CPU_USAGE/int TARGET_CPU_USAGE={args['cpu_usage']}/g\" cpu.cpp")
        os.system(f"sed -i \"s/int DURATION/int DURATION={duration}/g\" cpu.cpp")
        os.system(f"sed -i \"s/int RAMP_UP_TIME/int RAMP_UP_TIME={args['rise_time']}/g\" cpu.cpp")
        os.system("g++ -shared -o inject.so -fPIC cpu.cpp")
        # 将注入的动态库拷贝到数据库进程所能访问的路径下
        os.system(f"cp inject.so {path}")
        os.system("rm cpu.cpp inject.so")
    elif fault_type == "io":
        os.system("cp inject-template/io-template io.c")
        os.system(f"sed -i \"s/int delta_ms/int delta_ms={duration}/g\" io.c")
        os.system("clang -std=gnu99 -ggdb -D_GNU_SOURCE -shared -o inject.so -fPIC io.c")
        os.system(f"cp inject.so {path}")
        os.system("rm io.c inject.so")
    elif fault_type == "mem":
        os.system("cp inject-template/mem-template mem.c")
        os.system(f"sed -i \"s/int TARGET_MEMORY/int TARGET_MEMORY={args['size']}/g\" mem.c")
        os.system(f"sed -i \"s/int DURATION/int DURATION={duration}/g\" mem.c")
        os.system(f"sed -i \"s/int RAMP_UP_TIME/int RAMP_UP_TIME={args['rise_time']}/g\" mem.c")
        os.system("clang std=gnu99 -ggdb -D_GNU_SOURCE -shared -o inject.so -fPIC mem.c")
        os.system(f"cp inject.so {path}")
        os.system("rm mem.c inject.so")
    elif fault_type == "lock":
        relation_id = args['relation_id']

    # TODO
    # 根据ip和port找pid
    gdb.execute(f"attach {pid}")
    if sql_filter == "no":
        if fault_type == "cpu" or fault_type == "io" or fault_type == "mem":
            gdb.execute(f"print (int)dlclose((long long unsigned)dlopen(\"{path}/inject.so\", 2))")
    else:
        bp = FilterBreakpoint()
        gdb.execute("c")
    gdb.execute("detach")





