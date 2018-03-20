'''
    大鲲 爬虫
'''
import requests
from headers import Headers
from bs4 import BeautifulSoup
import time
import re
import numpy as np
from storage import Storage

headers = Headers()
storage = Storage()


class DakunSpider(object):

    # 获取列表数据
    def fetch_list(self, _type, page):
        url = 'https://pro.lagou.com/project/%s/%d' % (_type, page)

        res = requests.get(url, headers=headers.getHeader())

        _result = []

        soup = BeautifulSoup(res.text,
                             'html5lib').find(id='project_list').find_all('li')

        for item in soup:
            link = item.find('a')

            if not link:
                continue

            _result.append(link.get('href'))

        return _result

    # 获取详情数据
    def fetch_detail(self, url):
        res = requests.get(url, headers=headers.getHeader())

        _result = {
            'target': 1,
            'target_url': res.url,
        }

        soup = BeautifulSoup(res.text, 'html5lib')

        for script in soup.find_all('script', {'src': False}):
            if not script:
                continue

            # target_id
            m = re.compile('global.projectId = "(.*)";').search(script.text)
            if m:
                _result['target_id'] = m.group(1)
            else:
                continue

            # project name
            m = re.compile('global.projectName = "(.*)";').search(script.text)
            if m:
                _result['name'] = m.group(1)

            # project status
            m = re.compile('global.status = "(.*)";').search(script.text)
            if m:
                _result['status'] = m.group(1)

            # project relation
            m = re.compile('global.relation = "(.*)" \?').search(script.text)
            if m:
                _result['relation'] = int(m.group(1))

            # project price
            m = re.compile('global.projectPrice = "(.*)";').search(script.text)
            if m:
                _price = self._parse_price(m.group(1))
                _result['min_price'] = _price[0]
                _result['max_price'] = _price[1]

        # project desc
        desc = soup.find('div', class_='project_txt')
        if desc:
            _result['desc'] = desc.text.strip()

        base_info = soup.select('ul.baseInfo li span')

        # categories
        _result['categories'] = [
            self._find_base_info_value(base_info, '基本信息').split('/')[0]
        ]
        for item in soup.select('div.category_list .category_tag'):
            _result['categories'].append(item.text)

        # company name
        _result['company_name'] = self._find_base_info_value(base_info, '公司名称')

        # publish time
        _result['publish_time'] = int(
            time.mktime(
                time.strptime(
                    self._find_base_info_value(base_info, '发布时间'),
                    '%Y-%m-%d %H:%M:%S')) * 1000)

        # project date
        daterange = soup.select_one(
            '.project_panel div:nth-of-type(2) .short_val')
        if daterange:
            daterange = self._parse_time(daterange.text)
            keys = [
                'max_date_value', 'max_date_unit', 'min_date_value',
                'min_date_unit'
            ]
            for index in range(len(daterange)):
                _result[keys[index]] = daterange[index]

        # stat info
        stat = soup.select('.bottom_data strong')
        keys = ['recommend_num', 'apply_num', 'visit_num']
        for index in range(len(stat)):
            _result[keys[index]] = int(stat[index].text)

        return _result

    # 获取所有数据
    def run(self):
        for t in ['kaifa', 'sheji', 'shichang', 'chanpin']:
            page = 1

            while (1):
                time.sleep(np.random.rand() * 2)
                print('开始请求列表数据，条件（type = %s, page = %d）' % (t, page))

                _list = self.fetch_list(t, page)

                print('列表请求成功，共%d条，开始请求详情' % (len(_list)))

                for detail_url in _list:
                    time.sleep(np.random.rand() * 2)

                    print('\t开始请求详情url: %s' % (detail_url))
                    detail = self.fetch_detail(detail_url)
                    print('\t请求成功，开始保存')

                    storage.upsert(detail)

                if (len(_list) % 9 == 0):
                    page = page + 1
                else:
                    page = 1
                    break

    # 解析价格
    def _parse_price(self, text):
        _result = [0, 0]

        if text:

            _match = re.match(r'(.*)元以上', text, re.M | re.I)

            if _match:
                _result[0] = _match.group(1)

            _match = re.match(r'(.*)元以下', text, re.M | re.I)

            if _match:
                _result[1] = _match.group(1)

            _match = re.match(r'(.*)-(.*)元', text, re.M | re.I)

            if _match:
                _result[0] = _match.group(1)
                _result[1] = _match.group(2)

        for index in range(len(_result)):
            _result[index] = float(_result[index])

        return _result

    # 解析开发时间
    def _parse_time(self, text):
        _result = [0, 0, 0, 0]

        if text:

            m = re.match(r'小于(.*)周', text, re.M | re.I)
            if m:
                _result[0] = m.group(1)
                _result[1] = 1

            m = re.match(r'(.*)-(.*)周', text, re.M | re.I)
            if m:
                _result[0] = m.group(1)
                _result[2] = m.group(2)
                _result[1] = _result[3] = 1

            m = re.match(r'(.*)-(.*)个月', text, re.M | re.I)
            if m:
                _result[0] = m.group(1)
                _result[2] = m.group(2)
                _result[1] = _result[3] = 2

            m = re.match(r'(.*)个月以上', text, re.M | re.I)
            if m:
                _result[3] = 2

        return _result

    # 提取基本信息
    def _find_base_info_value(self, base_info, title):
        for index in range(len(base_info)):
            if title in base_info[index].text:
                return base_info[index + 1].text

        return ''