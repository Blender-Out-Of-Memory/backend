from time import sleep
from typing import Callable

def wait(callback: Callable):
    sleep(2)
    callback()