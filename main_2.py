import argparse
from chat_2 import *
from commander import Commander


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "address",
        nargs='?',
        default="localhost",
        help="address of rabbitMQ server (default: localhost)",
    )
    parser.add_argument(
        "start_channel",
        nargs='?',
        default="default_channel",
        help="channel to start chatting (default: default_channel)",
    )
    args = parser.parse_args()
    return args


def main(address, start_channel):
    chat = Chat(host_str=address, default_channel=start_channel)

    cmdr = Commander()

    action_dict = dict()
    action_dict[cmdr.CMD_help] = cmdr.help
    action_dict[cmdr.CMD_exit] = cmdr.exit_cmdr
    action_dict[cmdr.CMD_send] = chat.send_msg
    action_dict[cmdr.CMD_switch] = chat.switch_channel
    action_dict[cmdr.CMD_subscribed] = chat.get_channel_lst

    cmdr.set_actions(action_dict)
    print("Welcome to chat with rabbitMQ")
    print(f"(type {cmdr.com_symbol}{cmdr.CMD_help} to see help)")
    cmdr.input_loop()

    print("try end")
    chat.dispose()


if __name__ == '__main__':
    args = get_args()
    main(args.address, args.start_channel)
