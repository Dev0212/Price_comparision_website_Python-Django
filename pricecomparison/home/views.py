from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
import gettext
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as signin
from .models import Contact
from .forms import UserUpdateForm,ProfileUpdateForm
import warnings
from urllib3.exceptions import InsecureRequestWarning
from .models import sp_product

warnings.filterwarnings('ignore', category=InsecureRequestWarning)
# from .forms import ProfileForm

# Create your views here.

def index(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "Latest Arrivals in Smart"

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

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    
    
    products = sp_product.objects.all()
    
    context={
        'fproduct':flipkart_products,
        'aproduct':amazon_products,
        'product':products,
        
    }
    
    
    
    return render(request,"index.html",context)
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request,'You logged Out')
    return redirect('/')
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pwd']

        user = authenticate(username= username , password = password)

        if user is not None:
            # signin(request,user)
            auth.login(request,user)
            messages.info(request,"You logged in")
            return render(request, 'index.html')
        else:
            messages.error(request, "Bad credentials")
            return redirect('login')
    return render(request, 'login.html')
def register(request): 
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        email_condition = "^[a-z]+[\._]?[a-z 0-9]+[@]\w+[.]\w{2,3}$"
        password = request.POST['pwd']
        r_password = request.POST['r_pwd']

        if User.objects.filter(username = username):
            messages.error(request, "User already exists! Please try any other username")
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists! Please try to signin")
        if re.search(email_condition,email):
            pass
        else:
            messages.error(request,"Enter a valid Email")
            return redirect('register')
        if password!=r_password:
            messages.error(request, "Passwords dosn't match!")
            return redirect('register')
        if len(username)>10:
            messages.error(request, 'username must be under 10 characters')
        if not username.isalnum():
            messages.error(request, 'username should only contain 0-9,A-Z,a-z')

            return redirect('register')
            

        myuser = User.objects.create_user(username, email, password)
        

        myuser.save()
        messages.info(request, "you're Account has been successfully created")    
        return redirect('login')
    return render(request, 'registration.html')

@login_required(login_url='login')
def profile(request):
    # if request.method == 'POST':
    #     form = ProfileForm(request.POST, instance=request.user.profile)
    #     if form.is_valid():
    #         form.save()
    #         username = request.user.username
    #         messages.info(request, f'{username}, Your profile is updated.')
    #         return redirect('/')
    # else:
    #     form = ProfileForm(instance=request.user.profile)
    # context = {'form':form}
    # return render(request, 'profile.html', context)
    return render(request,'profile.html')

def about(request):
    return render(request,'about.html')
def product(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "Latest Headphones"
    search_query_a = "Latest Laptops"

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

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_search = search_query_a.replace(" ","+")
        amazon_url = f"https://www.amazon.in/s?k={a_search}&ref=nb_sb_noss_1"
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    context={
        'ftamazon':amazon_products,
        'ftflipkart':flipkart_products
    }
    return render(request,'products.html',context)
def contact(request):
    if request.method=="POST":
        contact=Contact()
        name=request.POST.get('name')
        email=request.POST.get('email')
        number=request.POST.get('number')
        subject=request.POST.get('subject')
        msg=request.POST.get('msg')
        contact.name=name
        contact.email=email
        contact.number=number
        contact.subject=subject
        contact.message=msg
        contact.save()   
        if "contactFormSubmit" in request.POST:
            messages.info(request,"Form submitted successfully!")
    return render(request,'contact.html')
def search(request):
    # context={}
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = request.POST.get('search')

    a_links = []
    a_names = []
    a_price = []
    a_images=[]
   

    f_links = []
    f_names = []
    f_price = []
    f_images=[]
    


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
    
        sim_p1 = ignore_text_after_bracket(text1)
        sim_p2 = ignore_text_after_bracket(text2)
        sim_p1 = sim_p1.lower()
        sim_p2 = sim_p2.lower()
        sim_p1_words = set(sim_p1.split())
        sim_p2_words = set(sim_p2.split())
        common_words = sim_p1_words.intersection(sim_p2_words)
        unique_words = sim_p1_words.union(sim_p2_words)
        similarity = len(common_words) / len(unique_words)
        similar = similarity * 100
        if similar >= 70.00:
            text1 = text1.lower()
            text2 = text2.lower()
            text1 = re.sub(r'[\(\)-]', '', text1)
            text2 = re.sub(r'[\(\)-]', ' ', text2)
            if all(char in set(text1) for char in text2) or all(char in set(text2) for char in text1):
                            
                    return True
            else:
                    return False            

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
        f_content = BeautifulSoup(f_req.content, 'html.parser')
        f_content_str = str(f_content)

        start_link = 'https://www.flipkart.com'

        if '_2kHMtA' in f_content_str:
            data = f_content.find_all('div',{'class' : '_2kHMtA'})
            

            for item in data:
                price_element = item.find('div', {'class': '_30jeq3 _1_WHN1'})
                if price_element is not None and price_element.get_text().strip() != '':
                    
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

                            
                            except AttributeError:
                                continue

    flipkart()
    amazon()

    a_len=(len(a_names))
    f_len=(len(f_names))

    amazon_products = list(zip(a_names,a_price,a_links,a_images))
    flipkart_products = list(zip(f_names,f_price,f_links,f_images))
  

    al=len(amazon_products)
    fl=len(flipkart_products)


    if fl != 0 and al > fl:
        r = fl
    elif al != 0 and fl > al:
        r = al

        for i in range(r):
            for j in range(r):
                similarity = jaccard_similarity(flipkart_products[i][0],amazon_products[j][0])
                if similarity:
                    
                    c_name.append(flipkart_products[i][0])
                    c_image.append(flipkart_products[i][3])
                    c_links_a.append(amazon_products[j][2])
                    c_links_f.append(flipkart_products[i][2])
                    c_price_a.append(amazon_products[j][1])
                    c_price_f.append(flipkart_products[i][1])
                
                    


        c_products = list(zip(c_name,c_price_a,c_price_f,c_links_a,c_links_f,c_image))
        context={
            'cproduct':c_products,
            'searchAmazon':amazon_products,
            'searchFlipkart':flipkart_products
        }
    
        return render(request,'search.html',context)
    return render(request,'Prnotfound.html')

def smartwatch(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "smartwatches"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

    context={
        'samazon':amazon_products,
        'sflipkart':flipkart_products
    }

    return render(request,'smartwatch.html',context)

def camera(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "Camera"

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

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    context={
        'camazon':amazon_products,
        'cflipkart':flipkart_products
    }
    return render(request,'camera.html',context)
def headphone(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "Headphones"

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

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    
    context={
        'hamazon':amazon_products,
        'hflipkart':flipkart_products
    }

    return render(request,'headphone.html',context)

def smartphone(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "smartphones"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    context={
        'spamazon':amazon_products,
        'spflipkart':flipkart_products
    }

    return render(request,'smartphone.html',context)

def television(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "television"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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
    context={
        'tvamazon':amazon_products,
        'tvflipkart':flipkart_products
                }
    return render(request,'television.html',context)
def speaker(request):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "speaker"

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

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

    context={
        'spamazon':amazon_products,
        'spflipkart':flipkart_products
    }

    return render(request,'speaker.html',context)

def offsmartphone(request):
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "discount smartphones"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

    context={
        'offphoneflipkart':flipkart_products,
        'offphoneamazon':amazon_products
    }

    return render(request,'offsmartphone.html',context)
def offsmartwatch(request):
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "discount smartwatch"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

    context={
        'offsmartwatchf':flipkart_products,
        'offsmartwatcha':amazon_products
    }

    return render(request,'offsmartwatch.html',context)
def offheadphone(request):
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-63aaf194-68ee9a2b5dafd17f598c3c66"}

    search_query = "discount headphones"

    a_links = []
    a_names = []
    a_price = []
    a_images=[]


    f_links = []
    f_names = []
    f_price = []
    f_images=[]



    # c_image = []
    # c_name = []
    # c_price_a = []
    # c_price_f = []
    # c_links_a = []
    # c_links_f = []

    # similar = False

    # def ignore_text_after_bracket(text):
    #     bracket_index = text.find("(")
    #     if bracket_index != -1:
    #         text = text[:bracket_index]
    #     return text

    # def jaccard_similarity(text1, text2):
    #     result = 0
    #     text1 = ignore_text_after_bracket(text1)
    #     text2 = ignore_text_after_bracket(text2)
    #     text1 = text1.lower()
    #     text2 = text2.lower()
    #     text1_words = set(text1.split())
    #     text2_words = set(text2.split())
    #     common_words = text1_words.intersection(text2_words)
    #     unique_words = text1_words.union(text2_words)
    #     similarity = len(common_words) / len(unique_words)
    #     similar = similarity * 100
    #     if similar >= 50.00:
    #         if text1 in text2 or text2 in text1:
    #             return True
    #         else:
    #             print('not similar')
                

    def flipkart():

        f_search = search_query.replace(" ","%20")
        flipkart_url = f"https://www.flipkart.com/search?q={f_search}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

        f_req = requests.get(flipkart_url,verify=False,timeout=10)
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
        a_req = requests.get(amazon_url, headers=headers,verify=False,timeout=10)
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

    context={
        'offheadphonef':flipkart_products,
        'offheadphonea':amazon_products
    }

    return render(request,'offheadphone.html',context)


def wishlist(request):
    return render(request,'wishlist.html')

# def spon(request):
#     sponser_products = sponser_products.objects.all()
#     sponser = {'products' : sponser_products}
#     return render(request, 'index.html', context)

# def profile_update(request):
#     if request.method == 'POST':
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(
#             request.POST, instance=request.user.profile)
#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             return redirect('profile.html')
#         else:
#             u_form = UserUpdateForm(instance=request.user)
#             p_form = ProfileUpdateForm(instance=request.user.profile)

#         context = {
#             'u_form': u_form,
#             'p_form': p_form,
#         }
#     return render(request,'profile_update.html',context)