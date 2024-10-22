import traceback


def dumpException(e):
    print("EXEPTION", e)
    traceback.print_tb(e.__traceback__)