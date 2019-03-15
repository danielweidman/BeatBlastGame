"""Simple example showing how to get gamepad events."""

from __future__ import print_function


from inputs import get_gamepad


def main():
    """Just print out some event infomation when the gamepad is used."""
    while 1:
        events = get_gamepad()
        for event in events:
            if event.state == 255 and event.code == "ABS_Z":
                print("hit left trigger")
            elif event.state == 255 and event.code == "ABS_RZ":
                print("hit right trigger")



if __name__ == "__main__":
    main()