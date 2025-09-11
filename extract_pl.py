from curl_cffi import requests
from lxml import html
from pymongo import MongoClient
from streamlit import image

cookies = {
    '_pk_id.4.fcd7': 'f565319f3a48eb7f.1757392617.',
    '_pk_ses.4.fcd7': '1',
}
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.leslibraires.fr/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    # 'cookie': '_pk_id.4.fcd7=f565319f3a48eb7f.1757392617.; _pk_ses.4.fcd7=1',
}

client = MongoClient("mongodb://localhost:27017/")
db = client["leslibraires_france_web"]
collection = db["pl"]

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
def pl_extract():
    for page in range(1,11):
        params = {
            'page': str(page),
        }
        print('page:',page)
        response = requests.get(
            'https://www.leslibraires.fr/rayon/science-fiction-fantastique-fantasy/',
            params=params,
            # cookies=cookies,
            # headers=headers,
            impersonate='chrome120'
        )
        # with open(f'page_{str(page)}.html','w',encoding='utf-8') as f:
        #     f.write(response.text)
        print(response.status_code)
        if response.status_code:
            tree = html.fromstring(response.text)
            products = xpath_value(tree,'//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"]',return_all=True)
            if products:

                for p_index in range(1,len(products)+1):
                    url_check = xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//h3[@class="card-product__title"]/a[@class="stretched-link"]/@href')
                    url = f'https://www.leslibraires.fr{url_check}' if url_check else url_check

                    image_check = xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//picture[@class="card-product__media"]//img[@itemprop="image"]/@src')
                    image = f'https:{image_check}' if image_check else image_check

                    product_id = str(url.split('/')[-1].split('-')[0]) if url else None
                    if product_id:
                        response = requests.post(
                            'https://www.leslibraires.fr/product/thumbnail-offers/',
                            # cookies=cookies,
                            # headers=headers,
                            json=[product_id]
                        ).json()
                        price = xpath_value(html.fromstring(response[product_id]),'//div[@class="product-price"]/text()')
                        stock = xpath_value(html.fromstring(response[product_id]),'//div[@class="product-stock"]/text()')
                    else:
                        price = None
                        stock = None
                    doc = {
                        'product_url': url,
                        'product_id': product_id,
                        'title': xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//h3[@class="card-product__title"]/a[@class="stretched-link"]/text()'),
                        'author': xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//span[@itemprop="author"]/text()'),
                        'publisher': xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//span[@itemprop="publisher"]/text()'),
                        # 'price': xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//div[@class="product-price"]/text()'),
                        # 'stock': xpath_value(tree,f'(//div[@class="list-layout list-layout--card-product"]//article[@class="card-product"])[{p_index}]//div[@class="product-stock"]/text()'),
                        'price': price,
                        'stock': stock,
                        'image': image,
                        'status': 'pending'
                    }
                    print(doc)
                    collection.insert_one(doc)
            else:
                break
        else:
            break
pl_extract()