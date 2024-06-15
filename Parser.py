import csv
import datetime
import json
import os
from pathlib import Path
from config import bananas as cnfg_bananas

import requests
import pandas as pd
import matplotlib.pyplot as plt
from time import sleep, time


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
    bananas = cnfg_bananas

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
        if not os.path.exists('./csv'):
            output_dir = Path('./csv')
            output_dir.mkdir(parents=True, exist_ok=True)
        if not os.path.exists('./csv/stats.csv'):
            with open('./csv/stats.csv', 'w', encoding='cp1251', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Название', 'id', 'Цена покупки', 'Цена продажи', 'Дата'])
        with open('./csv/stats.csv', 'a', encoding='cp1251', newline='') as file:
            writer = csv.writer(file)
            for item in stats:
                writer.writerow(item.values())

    @timer
    def analyze(self):
        if not os.path.exists('./csv/stats.csv'):
            return -1
        else:
            df = pd.read_csv('./csv/stats.csv', encoding='cp1251')
            df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y %H:%M:%S')

            repeated_names = df['Название'].value_counts()
            repeated_names = repeated_names[repeated_names > 1].index.tolist()

            for name in repeated_names:
                subset = df[df['Название'] == name]
                plt.figure(figsize=(10, 6))

                plt.plot(subset['Дата'], subset['Цена покупки'], label='Цена покупки', color='blue', marker='o')

                plt.plot(subset['Дата'], subset['Цена продажи'], label='Цена продажи', color='red', marker='o')

                plt.title(f'Цены для {name}')
                plt.xlabel('Дата')
                plt.ylabel('Цена')
                plt.legend()
                plt.grid(True)
                plt.xticks(rotation=45)

                filename = f'./graphs/{name}.jpg'
                if not os.path.exists('./graphs'):
                    output_dir = Path('./graphs')
                    output_dir.mkdir(parents=True, exist_ok=True)
                plt.savefig(filename, format='jpg')

                plt.close()
