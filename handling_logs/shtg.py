# import sh

# def tail_F(some_file):
#     while True:
#         try:
#             for line in sh.tail("-f", some_file, _iter=True):
#                 yield line
#         except sh.ErrorReturnCode_1:
#             yield None

# tail_F("/var/log/syslog")

# from threading import Thread
# import time

# def runA():
#     while True:
#         print('A\n')
#         time.sleep(1)

# def runB():
#         print('B\n')

# if __name__ == "__main__":
#     t1 = Thread(target = runA)
#     t2 = Thread(target = runB)
#     t1.setDaemon(True)
#     t2.setDaemon(True)
#     t1.start()
#     t2.start()
#     while True:
#         pass

# import threading, queue, subprocess

# tailq = queue.Queue(maxsize=10) # buffer at most 100 lines

# def tail_forever():
#     p = subprocess.Popen(['tail','-F',"-n", "1", "/var/log/syslog"], stdout=subprocess.PIPE)
#     while 1:
#         line = p.stdout.readline()
#         tailq.put(line)
#         if not line:
#             break

# x = threading.Thread(target=tail_forever)
# x.start()

# print(tailq.get()) # blocks
# print(tailq.get_nowait()) 