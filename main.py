from config import bananas
from Parser import Parser

if __name__ == '__main__':
    parser = Parser(bananas=bananas)
    stats = parser.parse()
    parser.write_file(stats)
    parser.analyze()
