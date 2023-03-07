import gettext
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

search_query = "New Arrivals in smart"

a_links = []
a_names = []
a_price = []
a_images=[]


f_links = []
f_names = []
f_price = []
f_images=[]



def flipkart():

    f_search = search_query.replace(" ","%20")
    flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    f_req = requests.get(flipkart_url)
    f_content = BeautifulSoup(f_req.content, 'html.parser')
    f_content_str = str(f_content)

    start_link = 'https://www.flipkart.com'

    if '_2kHMtA' in f_content_str:
        data = f_content.find_all('div',{'class' : '_2kHMtA'})
        

        for item in data:
                
            rest_link = item.find('a',attrs={'class' : '_1fQZEK'} )
            rest_link=(rest_link.get('href'))
            f_links.append(start_link+rest_link)

            product_name = item.find('div',attrs={'class' : '_4rR01T'})
            f_names.append(product_name.text)
            
            product_price=item.find('div',attrs={'class' : '_30jeq3 _1_WHN1'})
            f_price.append(product_price.string)

            product_imge=item.find('img', attrs={'class' : '_396cs4'})
            f_images.append(product_imge.get('src'))

            

            

    elif '_4ddWXP' in f_content_str:
        data = f_content.find_all('div',{'class' : '_4ddWXP'})
        

        for item in data:
                
            rest_link = item.find('a',attrs={'class' : 's1Q9rs'} )
            rest_link=(rest_link.get('href'))
            f_links.append(start_link+rest_link)

            product_name = item.find('a',attrs={'class' : 's1Q9rs'})
            product_name= product_name.get('title')
            f_names.append(product_name)
            
            product_price=item.find('div',attrs={'class' : '_30jeq3'})
            f_price.append(product_price.string)

            product_imge=item.find('img', attrs={'class' : '_396cs4'})
            f_images.append(product_imge.get('src'))

            
def amazon():
    a_search = search_query.replace(" ","+")
    amazon_url = f"https://www.amazon.in/s?k={a_search}&ref=nb_sb_noss_1"
    a_req = requests.get(amazon_url, headers=headers)
    a_content = BeautifulSoup(a_req.content, 'html.parser')
    


    start_link = 'https://www.amazon.in'

    
    if a_content.find_all('div', {'class' : 'sg-row'}):

        data = a_content.find_all('div',{'class' : 'sg-row'})

        for item in data:

            if item.find('div',{'class' : "a-row a-spacing-micro"}):
                continue
            else:
                try:
                    rest_link = item.find('a',attrs = { 'class' : "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
                    rest_link = (rest_link.get('href'))
                    a_links.append(start_link+rest_link)

                    product_name = item.find('span',{'class' : 'a-size-medium a-color-base a-text-normal'})
                    a_names.append(product_name.text)
                    

                    product_price = item.find('span',{'class' : 'a-offscreen'})
                    a_price.append(product_price.text)


            
                    

                    product_image = item.find('img',{'class' : 's-image'})  
                    a_images.append(product_image.get('src'))
                except AttributeError:
                    continue

flipkart()
amazon()

amazon_products = list(zip(a_names,a_price,a_links,a_images))
flipkart_products = list(zip(f_names,f_price,f_links,f_images))

print(flipkart_products[0])