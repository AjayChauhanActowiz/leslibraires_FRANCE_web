from curl_cffi import requests
from lxml import html

cookies = {
    '_pk_id.4.fcd7': 'f565319f3a48eb7f.1757392617.',
    '_pk_ses.4.fcd7': '1',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    # 'cookie': '_pk_id.4.fcd7=f565319f3a48eb7f.1757392617.; _pk_ses.4.fcd7=1',
}
def xpath_value(tree,xpath_string,if_not_present=None,join_by=None,replace_something=[],return_all=False):
   try:
       check_xpath = tree.xpath(xpath_string)
       if len(check_xpath)==0:
           raise Exception
       if join_by:
           # print(check_xpath)
           return join_by.join(check_xpath)
       if replace_something:
           return check_xpath[0].strip().replace(replace_something[0],replace_something[1])
       if return_all:
           return check_xpath
       return check_xpath[0].strip()
   except:
       return if_not_present
response = requests.get(
    'https://www.leslibraires.fr/livre/24546866-beaute-sarah-pinborough-bragelonne',
    # cookies=cookies,
    # headers=headers,
    impersonate='chrome120'
)
print(response.status_code)
tree = html.fromstring(response.text)
rows_count = len(xpath_value(tree,'//div[@class="product-features__body"]//table//tr',return_all=True))
features_dic = {}
for row in range(1,rows_count+1):
    value = xpath_value(tree,f'(//div[@class="product-features__body"]//table//tr)[{row}]/td/text()')
    value = xpath_value(tree,f'(//div[@class="product-features__body"]//table//tr)[{row}]/td/a/text()') if not value else value
    features_dic[xpath_value(tree,f'(//div[@class="product-features__body"]//table//tr)[{row}]/th/text()')] = value
print(features_dic)