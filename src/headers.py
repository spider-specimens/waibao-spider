''' 
    headers
'''
import numpy as np


class Headers(object):
    headers = [{
        'User-Agent':
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        'Referer':
        'https://pro.lagou.com/project/'
    }, {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
        'Referer':
        'https://pro.lagou.com/project/'
    }, {
        'User-Agent':
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
        'Referer':
        'https://pro.lagou.com/project/'
    }]

    def getHeader(self):
        return self.headers[np.random.randint(0, len(self.headers))]
