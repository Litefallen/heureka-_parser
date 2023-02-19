from requests_html import HTMLSession
from itertools import count
import csv
import os
from datetime import datetime
session = HTMLSession()
smartphones = []
dicti = {}
c_p = count(1)
url = 'https://mobilni-telefony.heureka.cz/f:1651:387362;1666:101069/?f=1'
s = session.get(url)
s.html.render(sleep=1)

breadcrumbs = [crumbs.text.replace(' ', '_') for crumbs in s.html.find(
    '.c-breadcrumbs__list li')]


def price_clean(price):
    return int(''.join(i for i in price if i.isdigit()))


def price_abomination_check(prices, coeff):
    return True if sorted(prices)[0] < sorted(prices)[1] * coeff else False


while True:
    url = f'https://mobilni-telefony.heureka.cz/f:1651:387362;1666:101069/?f={next(c_p)}'
    s = session.get(url)
    if not (s.html.find('.c-product__title a')):
        break
    smartphones.extend(s.html.find(
        '.l-products .c-product__title a'))
    print('Scrapping products from the next page..')
links = (i.attrs['href'] for i in smartphones if 'exit' not in i.attrs['href'])
print('Getting product data..')
for i in links:
    s = session.get(i)
    name = s.html.xpath(
        '//*[@id="__next"]/div/main/div[1]/div[2]/h1', first=True).text
    price_link_dict = {price_clean(i.text): i.attrs['href'] for i in s.html.find(
        'section.c-offer .c-offer__price a')}
    if name in dicti.keys():
        dicti[name].update(price_link_dict)
        continue
    dicti[name] = price_link_dict
cur_time = datetime.now().strftime('%d%m%y_%H%M%S')
with open(f'{breadcrumbs[-1]}({cur_time}).csv', 'w') as file:

    print('Exporting date to csv file..')
    wrtr = csv.DictWriter(
        file, fieldnames=['Name', 'Min_price', 'Link', 'Price_abomination'])
    wrtr.writeheader()
    for i in dicti:
        wrtr.writerow({'Name': i, 'Min_price': min(
            dicti[i]), 'Link': dicti[i][min(dicti[i])], 'Price_abomination': price_abomination_check(dicti[i], .6)})
    print(
        f"Your csv file is stored in: {os.path.abspath(f'{breadcrumbs[-1]}({cur_time}).csv')}")