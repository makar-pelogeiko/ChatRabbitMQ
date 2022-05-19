import argparse
import chat

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "address",
        help="int number of menu item 0 - get info about graph; 1 - create 2 cycles graph and "
        "save it to .DOT --data key is necessary",
        type=str,
    )
    args = parser.parse_args()
    return args


def main():
    pass

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = get_args()
    main(args)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
