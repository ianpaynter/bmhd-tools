import numpy as np
from time import sleep


def my_func_one():#<> Func. Total time: 0.0s, % of main: 0.03

    mem_hog = np.arange(0, 1000000)#<> Line Total time: 0.0s, % of func.: 99.49, % of main: 0.02
    mem_jog = np.arange(0, 100)#<> Line Total time: 0.0s, % of func.: 0.51, % of main: 0.0


def my_func_two():#<> Func. Total time: 3.02s, % of main: 49.97

    sleep(1)#<> Line Total time: 1.01s, % of func.: 33.53, % of main: 16.76
    sleep(2)#<> Line Total time: 2.01s, % of func.: 66.47, % of main: 33.22


def main():#<> Func. Total time: 3.03s

    my_func_one()#<> Line Total time: 0.0s, % of main: 0.03
    my_func_one()#<> Line Total time: 0.0s, % of main: 0.03
    my_func_two()#<> Line Total time: 3.02s, % of main: 99.93


if __name__ == "__main__":

    main()
