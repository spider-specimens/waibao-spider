from dakun import DakunSpider

spider = DakunSpider()

# res = spider.fetch_list('kaifa', 1)

# result = spider.parse_list_data(res)

res = spider.fetch_detail('https://pro.lagou.com/project/6762.html')

result = spider.parse_detail_data(res)

print(result)
