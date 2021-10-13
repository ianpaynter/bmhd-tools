import numpy as np
from time import sleep
import psutil

print(psutil.cpu_times())
print(psutil.virtual_memory())
print(psutil.net_io_counters())

#
# def myFuncOne():
#
#     print(psutil.cpu_percent())
#     memHog = np.arange(0, 1000000)
#     memJog = np.arange(0, 100)
#     print(psutil.cpu_percent())
#
#
# def myFuncTwo():
#
#     sleep(10)
#     sleep(2)
#     print(psutil.cpu_percent())
#
#
# def main():
#
#     myFuncOne()
#     myFuncOne()
#     myFuncTwo()
#
# if __name__ == "__main__":
#
#     main()