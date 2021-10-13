import numpy as np
from time import sleep

@profile
def myFuncOne():

    memHog = np.arange(0, 1000000)
    memJog = np.arange(0, 100)

@profile
def myFuncTwo():

    sleep(10)
    sleep(2)

@profile
def main():

    myFuncOne()
    myFuncOne()
    myFuncTwo()

if __name__ == "__main__":

    main()