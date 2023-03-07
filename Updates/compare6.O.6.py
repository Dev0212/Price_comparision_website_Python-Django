import requests 
from bs4 import BeautifulSoup
import requests
import re




headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36", 
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

flipkart_products=[]




def ignore_text_after_bracket(text):
    bracket_index = text.find("(")
    if bracket_index != -1:
        text = text[:bracket_index]
    return text



def flipkart(search_query = search_query):

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

            flipkart_products = list(zip(f_names,f_price,f_links,f_images))


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

            

    
flipkart()
flipkart_products = list(zip(f_names,f_price,f_links,f_images))

for i in range(3):
     for j in range(3):
          

        f_str_r = flipkart_products[i][0]
        f_str = f_str_r.replace(',','')


        def amazon(search_query = f_str):
            a_search = search_query.replace(" ","+")
            amazon_url = f"https://www.amazon.in/s?k={a_search}&ref=nb_sb_noss_1"
        
            a_req = requests.get(amazon_url, headers=headers)
            a_content = BeautifulSoup(a_req.content, 'html.parser')
            


            start_link = 'https://www.amazon.in'

            
            if a_content.find_all('div', {'class' : 'sg-row'}):

                data = a_content.find_all('div',{'class' : 'sg-row'})

                for item in data:
                    price_element = item.find('span', {'class': 'a-price'})
                    if price_element is not None and price_element.get_text().strip() != '':

                        sponsored_label = item.select_one('span[data-component-type="s-sponsored-label-marker"]')
                        if sponsored_label is not None:
                            continue
                        else:

                            if item.find('div',{'class' : "a-row a-spacing-micro"}):
                                continue
                            else:
                                try:
                                    product_image = item.find('img',{'class' : 's-image'})  
                                    a_images.append(product_image.get('src'))

                                    rest_link = item.find('a',attrs = { 'class' : "a-link-normal s-no-outline"})
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

        def jaccard_similarity(text1, text2):
            text1 = text1.lower()
            text2 = text2.lower()
            text1 = re.sub(r'[\(\)-]', '', text1)
            text2 = re.sub(r'[\(\)-]', ' ', text2)
            
            if all(char in set(text1) for char in text2) or all(char in set(text2) for char in text1):
                
                return True
            else:
                return False

                    

        flipkart()
        amazon()



        amazon_products = list(zip(a_names,a_price,a_links,a_images))
        flipkart_products = list(zip(f_names,f_price,f_links,f_images))
        # jaccard_similarity(f_str,amazon_products[j][0])

        similarity = jaccard_similarity(f_str,amazon_products[j][0])

        if similarity:
                        c_name.append(flipkart_products[i][0])
                        c_image.append(flipkart_products[i][3])
                        c_links_a.append(amazon_products[j][2])
                        c_links_f.append(flipkart_products[i][2])
                        c_price_a.append(amazon_products[j][1])
                        c_price_f.append(flipkart_products[i][1])



c_products = list(zip(c_name,c_price_a,c_price_f,c_links_a,c_links_f,c_image))

a_links = []
a_names = []
a_price = []
a_images=[]
a_features = []

amazon(search_query=search_query)

amazon_products = list(zip(a_names,a_price,a_links,a_images))


if len(c_products)>=2:
    print(c_products[0])
    print("------------------------------------------------------------------")
    print(c_products[1])
    print("------------------------------------------------------------------")
    print("------------------------------------------------------------------")

print(amazon_products[0])
print("----------------------------------------------------------------------")
print(amazon_products[1])

