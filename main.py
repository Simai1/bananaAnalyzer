import csv
import datetime
import json
import os
import requests
import pandas as pd
from time import sleep, time
from config import bananas


def timer(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        name = func.__name__
        func_res = func(*args, **kwargs)
        if func_res == -2:
            print(f'[INFO] function {name} not completed. Try again...')
            wrapper(*args, **kwargs)
        else:
            print(f'[INFO] function {name} completed: {time() - t1} sec.')
        return func_res

    return wrapper


class Parser:
    url = 'https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid='
    bananas = dict()

    def __init__(self, bananas):
        self.bananas = bananas

    @timer
    def parse(self):
        stats = []
        i = 0
        for k, v in self.bananas.items():
            i += 1
            url = self.url + str(v)
            try:
                res = requests.get(url)
            except Exception as ex:
                return ex
            json_res = json.loads(res.text)
            if json_res['success'] == 104:
                return -2
            if json_res['success'] == 1:
                sell_orders = json_res['sell_order_graph']
                buy_orders = json_res['buy_order_graph']
                sell_orders_arr = []
                sell_orders_counter = 0
                buy_orders_arr = []
                buy_orders_counter = 0
                for item in sell_orders:
                    sell_orders_arr.append(item[0])
                    sell_orders_counter += item[1]
                    if sell_orders_counter >= 100:
                        break
                for item in buy_orders:
                    buy_orders_arr.append(item[0])
                    buy_orders_counter += item[1]
                    if buy_orders_counter >= 100:
                        break
                sell_orders_medium_cost = sum(sell_orders_arr) / len(sell_orders_arr)
                buy_orders_medium_cost = sum(buy_orders_arr) / len(buy_orders_arr)
                stats.append({
                    'name': k,
                    'item_id': v,
                    'sell_orders_medium_cost': sell_orders_medium_cost,
                    'buy_orders_medium_cost': buy_orders_medium_cost,
                    'date': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                })
            else:
                return -1
            print(f'[INFO] parser iteration {i}')
            sleep(5)
        return stats

    @timer
    def write_file(self, stats):
        if not os.path.exists('./stats.csv'):
            with open('stats.csv', 'w', encoding='cp1251', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Название', 'id', 'Цена покупки', 'Цена продажи', 'Дата'])
        with open('stats.csv', 'a', encoding='cp1251', newline='') as file:
            writer = csv.writer(file)
            for item in stats:
                writer.writerow(item.values())

    @timer
    def analyze(self):
        if not os.path.exists('./stats.csv'):
            return -1
        else:
            df = pd.read_csv('stats.csv', encoding='cp1251')
            print(df.head())


if __name__ == '__main__':
    parser = Parser(bananas=bananas)
    stats = parser.parse()
    parser.write_file(stats)
    parser.analyze()
