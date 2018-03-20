'''
    存储数据
'''
import psycopg2


class Storage(object):
    def __init__(self):
        self.db = psycopg2.connect(
            database='waibao',
            user='postgres',
            password='123456',
            host='127.0.0.1',
            port='5432')
        print('db connect success.')

    def upsert(self, data):
        print('\t保存成功')
