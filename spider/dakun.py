'''
    大鲲 爬虫
'''
import requests
from headers import Headers
from bs4 import BeautifulSoup
import time
import re

headers = Headers()


class DakunSpider(object):

    # 请求列表数据
    def fetch_list(self, type=None, page=1):
        url = 'https://pro.lagou.com/project'

        if type:
            url += '/%s' % type

        url += '/%d' % page

        return requests.get(url, headers=headers.getHeader())

    # 解析列表数据
    def parse_list_data(self, res):
        _result = []

        soup = BeautifulSoup(res.text,
                             'html5lib').find(id='project_list').find_all('li')

        for item in soup:
            link = item.find('a')

            if not link:
                continue

            status = link.find('span', class_='recruiting')
            title = link.find('h3')
            price = link.find('span', class_='range')
            categories = link.find_all('span', class_='category_tag')

            if price:
                price = self.parse_price(price.text)

            for index in range(len(categories)):
                categories[index] = categories[index].text

            _result.append({
                'detail_url': link.get('href'),
                'status': status.text if status else '',
                'title': title.text if title else '',
                'min_price': price[0],
                'max_price': price[1],
                'categories': categories,
            })

        return _result

    # 请求详情界面
    def fetch_detail(self, url):
        return requests.get(url, headers=headers.getHeader())

    # 解析详情
    def parse_detail_data(self, res):
        if not res.text:
            return None

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
                _price = self.parse_price(m.group(1))
                _result['min_price'] = _price[0]
                _result['max_price'] = _price[1]

        # project desc
        desc = soup.find('div', class_='project_txt')
        if desc:
            _result['desc'] = desc.text.strip()

        base_info = soup.select('ul.baseInfo li span')

        # categories
        _result['categories'] = [base_info[1].text.split('/')[0]]
        for item in soup.select('div.category_list .category_tag'):
            _result['categories'].append(item.text)

        # company name
        _result['company_name'] = base_info[3].text

        # publish time
        _result['publish_time'] = int(
            time.mktime(time.strptime(base_info[5].text, '%Y-%m-%d %H:%M:%S'))
            * 1000)

        # project date
        daterange = soup.select_one(
            '.project_panel div:nth-of-type(2) .short_val')
        if daterange:
            daterange = self.parse_time(daterange.text)
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

    # 解析价格
    def parse_price(self, text):
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
    def parse_time(self, text):
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
