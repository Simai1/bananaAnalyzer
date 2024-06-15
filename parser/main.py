from Parser import Parser
from time import sleep


def loop(sleep_time):
    while True:
        parser = Parser()
        stats = parser.parse()
        parser.write_file(stats)
        parser.analyze()
        sleep(sleep_time)


if __name__ == '__main__':
    sleep_time = 60 * 30
    loop(sleep_time=sleep_time)
