from pymongo import MongoClient
from curl_cffi import requests
from lxml import html
from concurrent.futures import ThreadPoolExecutor

client = MongoClient("mongodb://localhost:27017/")
db = client["leslibraires_france_web"]
pl_collection = db["pl"]
pdp_collection = db["pdp"]

def fetch_data():
    documents = pl_collection.find({"status": "pending"},{"_id":0})
    return list(documents)

def update_data(product_url):
    pl_collection.update_one(
        {"product_url": product_url},  # filter
        {"$set": {"status": "done"}}  # update
    )
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
def pdp_detail(pl_doc):
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
    response = requests.get(
        pl_doc['product_url'],
        # cookies=cookies,
        # headers=headers,
        impersonate='chrome120'
    )
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        image_check = xpath_value(tree,'//div[@class="product-image"]/img/@src',return_all=True)
        image = ' | '.join([f'https:{img}' for img in image_check]) if image_check else None

        breadcrumb_check = xpath_value(tree, '//nav[@aria-label="breadcrumb"]//li[contains(@class, "breadcrumb-item")]/a/text()', return_all=True)
        breadcrumb = ' | '.join([b_c.strip() for b_c in breadcrumb_check]) if breadcrumb_check else None
        rows_count = len(xpath_value(tree, '//div[@class="product-features__body"]//table//tr', return_all=True))
        features_dic = {}
        for row in range(1, rows_count + 1):
            value = xpath_value(tree, f'(//div[@class="product-features__body"]//table//tr)[{row}]/td/text()')
            value = xpath_value(tree,f'(//div[@class="product-features__body"]//table//tr)[{row}]/td/a/text()') if not value else value
            features_dic[xpath_value(tree, f'(//div[@class="product-features__body"]//table//tr)[{row}]/th/text()')] = value
        docu = {
            'product_url': pl_doc['product_url'],
            'product_id': pl_doc['product_id'],
            'product_name': pl_doc['title'],
            'author': pl_doc['author'],
            'publisher': pl_doc['publisher'],
            'price': pl_doc['price'],
            'stock': pl_doc['stock'],
            'image': image,
            'breadcrumbs': breadcrumb,
            'description': xpath_value(tree,'//p[@itemprop="description"]//text()',join_by=' '),
            'translated_by': xpath_value(tree,'//p[@class="product-details__author"]/a[@itemprop="author"]/text()'),
            'vendor': xpath_value(tree,'//p[@class="card-shop__vendor"]/span/text()'),
            'specifications': " | ".join(f"{k}: {v}" for k, v in features_dic.items()) if features_dic else None,
            'EAN13': features_dic.get('EAN13',None),
            'ISBN': features_dic.get('ISBN',None),
            'publication_date': features_dic.get('Date de publication',None)
        }
        print(docu)
        pdp_collection.insert_one(docu)
        update_data(pl_doc['product_url'])

# doc = {
#   "product_url": "https://www.leslibraires.fr/livre/24546866-beaute-sarah-pinborough-bragelonne",
#   "product_id": "24546866",
#   "title": "Beauté",
#   "author": "Sarah Pinborough",
#   "publisher": "Bragelonne",
#   "price": "8,95 €",
#   "stock": "Précommande",
#   "image": "https://leslibraires.b-cdn.net/vjI8jMY4T_7uz2gqiQGyrxrKFE1NVjevmiOvelPBqbk/s:302:204/MTQ4MTA0MTY.webp",
#   "status": "pending"
# }
# document = fetch_data()
# for doc in document:
#     pdp_detail(doc)
document = fetch_data()
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(pdp_detail, document)