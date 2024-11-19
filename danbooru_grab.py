import os
import requests
from bs4 import BeautifulSoup
import time

# base [DO NOT CHANGE]
base_url = 'https://danbooru.donmai.us/posts?page=[REPLACE_PAGE_INDEX]&tags=[REPLACE_TAGS]'

# save_patch [Change to what you want]
save_patch = 'f:\\danbooru_grabbing\\'

# my_tags Search tags [Change to what you want]
my_tags = 'furry+veemon'

# page limit
start_page = 1
end_page = 1001

def SaveImage(url, tags):
    print ('Load Image ' + url)
    req = requests.get(url)    
    req.encoding = req.apparent_encoding
    
    if req.status_code == 200:
        data = BeautifulSoup(req.text,"html.parser")
        
        if not data:
            print('Image not found')
            return
        
        items = data.find_all("li", id='post-option-download')
        img_url = items[0].find('a').get('href')
        img_filename = items[0].find('a').get('download')
        print(img_url)    
        print(img_filename)    
        
        img_requests = requests.get(img_url)
        img_save = os.path.join(save_patch, img_filename)
        with open(img_save, 'wb') as saveFile:
            saveFile.write(img_requests.content)
        
        tags_replaced = str(tags).replace(' ', ',')
        tags_save = os.path.join(save_patch, img_filename+'.txt')
        with open(tags_save, 'wb') as saveFile:
            saveFile.write(bytes(tags_replaced, 'utf-8'))
            
        print('Image ang Tags saved!')

# Loop through start_page to end_page
for page in range(start_page, end_page):
    url = base_url.replace('[REPLACE_PAGE_INDEX]', str(page)).replace('[REPLACE_TAGS]', my_tags)
    
    print ('********\nloading ' + url)
    # Fetch url
    req = requests.get(url)    
    req.encoding = req.apparent_encoding
    
    # 200
    if req.status_code == 200:
        data = BeautifulSoup(req.text,"html.parser")
                
        # Break the loop if the data is empty (no more tags to fetch)
        if not data:
            print(f'No more data found at page {page}. Stopping.', flush=True)
            break
        #print(data)
        
        items = data.find_all("article")                
        count = 1
        for item in items:            
            tags = item.find("img").get("title")
            src = item.find("a").get("href")
            original_img = 'https://danbooru.donmai.us' + str(src)
            print('====== ' + str(count))      
            #print(item)  
            #print(src)
            print(original_img)
            print(tags)
            SaveImage(original_img, tags)
            count = count + 1
            
            # Sleep for 1 second so we don't DDOS Danbooru too much
            time.sleep(1)                    
        
        # Break the loop if the items is empty (no more tags to fetch)
        if 1 == count:
            print(f'No more data found at page {page}. Stopping.', flush=True)
            break

