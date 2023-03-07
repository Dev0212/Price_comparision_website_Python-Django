import gettext
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

search_query = input("Enter the product name:: ")

a_links = []
a_names = []
a_price = []
a_images=[]
a_features = []

f_links = []
f_names = []
f_price = []
f_images=[]
f_features = []


c_image = []
c_name = []
c_price_a = []
c_price_f = []
c_links_a = []
c_links_f = []

similar = False

def ignore_text_after_bracket(text):
    bracket_index = text.find("(")
    if bracket_index != -1:
        text = text[:bracket_index]
    return text

def jaccard_similarity(text1, text2):
    result = 0
    text1 = ignore_text_after_bracket(text1)
    text2 = ignore_text_after_bracket(text2)
    text1 = text1.lower()
    text2 = text2.lower()
    text1_words = set(text1.split())
    text2_words = set(text2.split())
    common_words = text1_words.intersection(text2_words)
    unique_words = text1_words.union(text2_words)
    similarity = len(common_words) / len(unique_words)
    similar = similarity * 100
    if similar >= 50.00:
        if text1 in text2 or text2 in text1:
            return True
        else:
            print('not similar')
            

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

a_len=(len(a_names))
f_len=(len(f_names))

amazon_products = list(zip(a_names,a_price,a_links,a_images))
flipkart_products = list(zip(f_names,f_price,f_links,f_images))

if a_len >= 3 and f_len >= 3:

    for i in range(5):
        for j in range(5):
            similarity = jaccard_similarity(flipkart_products[i][0],amazon_products[j][0])
            if similarity:
                print("similar")
                
                c_name.append(flipkart_products[i][0])
                c_image.append(flipkart_products[i][3])
                c_links_a.append(amazon_products[j][2])
                c_links_f.append(flipkart_products[i][2])
                c_price_a.append(amazon_products[j][1])
                c_price_f.append(flipkart_products[i][1])


    c_products = list(zip(c_name,c_price_a,c_price_f,c_links_a,c_links_f,c_image))
    
print(c_products.count)
#c_products = comparable products

#This will print the whole product with it's name,price,link & image as well 
#print(amazon_products[0])

#This will print whatever you specify [0][0] = name of the first product [0][1] = price according to a_names,a_price,a_links,a_images
#

for i in range(5):
    amazon_products[i]
    print("-----------------------------------------------------------------------------------")




