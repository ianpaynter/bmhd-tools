import numpy as np
from time import sleep


def my_func_one():

    mem_hog = np.arange(0, 1000000)
    mem_jog = np.arange(0, 100)


def my_func_two():

    sleep(1)
    sleep(2)


def main():

    my_func_one()
    my_func_one()
    my_func_two()


if __name__ == "__main__":

    main()
