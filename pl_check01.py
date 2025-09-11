from curl_cffi import requests

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
params = {
    'page': '2',
}
response = requests.get(
    'https://www.leslibraires.fr/rayon/science-fiction-fantastique-fantasy/',
    params=params,
    # cookies=cookies,
    # headers=headers,
    impersonate='chrome120'
)
print(response.status_code)
print('24581817' in response.text)