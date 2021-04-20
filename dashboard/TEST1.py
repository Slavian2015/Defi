import sys, os
import subprocess
import threading
import time


def output_reader(proc, file):
    while True:
        byte = proc.stdout.read(1)
        if byte:
            sys.stdout.buffer.write(byte)
            sys.stdout.flush()
            file.buffer.write(byte)
        else:
            break
#
#
# # command = "python /usr/local/WB/dashboard/TEST2.py -p"  # the shell command
# output = str(subprocess.Popen("python /usr/local/WB/dashboard/TEST2.py -p",
#                               shell=True,
#                               stdout=subprocess.PIPE,
#                               stderr=subprocess.STDOUT).communicate()[0])
#
# print("output :", output)
# print("error :", error)


import subprocess, signal, os

pidid = 0


def startlogging():
    pid = subprocess.Popen(["python", "/usr/local/WB/dashboard/TEST2.py"]).pid
    pidid = str(pid)
    print('pidid :', pidid)


if __name__ == '__main__':
    startlogging()
    print('FINISH')
    time.sleep(12)
    os.kill(int(pidid), signal.SIGKILL)
    print("Process Successfully terminated")


# with subprocess.Popen(["python", '/usr/local/WB/dashboard/TEST2.py'],
#                       stdout=subprocess.PIPE,
#                       stderr=subprocess.PIPE) as proc1, \
#         open('/usr/local/WB/data/my_logs/TEST2.txt', 'w') as file1:
#     t1 = threading.Thread(target=output_reader, args=(proc1))
#
#     t1.start()
#     print("t1 :", t1)
#     print("proc1 :", proc1)
#     t1.join()
# print('FINISH')


"""
==========================================
"""
# from multiprocessing import Process
#
#
# def func1():
#     print('func1: starting')
#     for i in range(100000000):
#         pass
#     print('func1: finishing')
#
#
# def func2():
#     print('func2: starting')
#     for i in range(100000000):
#         pass
#     print('func2: finishing')
#
#
# if __name__ == '__main__':
#     print('START')
#     p1 = Process(target=func1)
#     p1.start()
#     p2 = Process(target=func2)
#     p2.start()
#     p1.join()
#     p2.join()
#     print('FINISH')

"""
==========================================
"""
# import asyncio, time
#
# async def say_after(delay, what):
#     await asyncio.sleep(delay)
#     print(what)
#
# async def main():
#
#     task1 = asyncio.create_task(
#         say_after(4, 'hello'))
#
#     task2 = asyncio.create_task(
#         say_after(3, 'world'))
#
#     print(f"started at {time.strftime('%X')}")
#
#     # Wait until both tasks are completed (should take
#     # around 2 seconds.)
#     await task1
#     await task2
#
#     print(f"finished at {time.strftime('%X')}")
#
#
# asyncio.run(main())