import os
import sys 
import requests
from bs4 import BeautifulSoup
import time

# base [DO NOT CHANGE]
base_url = 'https://e621.net/posts?page=[REPLACE_PAGE_INDEX]&tags=[REPLACE_TAGS]'

# save_patch [Change to what you want]
save_patch = 'f:\\e621_grabbing\\'

# my_tags for SearchDownload tags [Change to what you want]
# seems e621 supports more than 2 tags
my_tags = 'fox_girl'

# page limit
start_page = 1
end_page = 20

# HIGHEST priority: blacklist [Set to EMPTY if not needed] Any condition
my_blacklist = ['']
#my_blacklist = ['tattoo']

# Higher priority: custom filter [Set to EMPTY if not needed] Absolute condition
my_abs_filters = []
#my_abs_filters = ['1girl', 'furry_female']

# custom filter [Set to EMPTY if not needed] Any condition
my_any_filters = []
#my_any_filters = ['blue_hair', 'white_hair']

# retrie times for any reason http request failed
retrie_times = 5

def RequestWithRetires(url, rt_times):
    # Sleep for 3 second so we don't DDOS e621 too much
    time.sleep(3)  
        
    req = None
    retries = 1
    success = False
    dummy_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
    while not success and retries < rt_times:
        try:            
            req = requests.get(url, headers={'User-Agent': dummy_user_agent})    
            req.encoding = req.apparent_encoding
            success = True
        except Exception as e:
            print(e)
            print('Retire [' + str(retries) + '/' + str(retrie_times) + '] in 5 seconds')
            time.sleep(5)  
            retries += 1
            
    return (success, req)

def SearchDownload():
    # Loop through start_page to end_page
    for page in range(start_page, end_page):
        url = base_url.replace('[REPLACE_PAGE_INDEX]', str(page)).replace('[REPLACE_TAGS]', my_tags)        
        print ('Loading search page ' + url)
        
        # Fetch url
        success, req = RequestWithRetires(url, retrie_times)        
        if False == success:
            print('*** Loading Failed!!!')
            return
        
        # 200 Http Success
        if 200 == req.status_code:
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
                original_img = 'https://e621.net' + str(src)
                print('====== ' + str(count) + ' @ page ' + str(page) + '/' + str(end_page))      
                #print(item)  
                #print(src)
                #print(original_img)
                #print(tags)
                if True is any(x in tags for x in my_blacklist):
                    print("Bypass Black List")
                elif True is all(x in tags for x in my_abs_filters):
                    if 0 == len(my_any_filters):
                        SingleDownload(original_img)                          
                    elif True is any(x in tags for x in my_any_filters):
                        SingleDownload(original_img)                        
                    else:
                        print("Bypass Any")
                else:
                    print("Bypass Abs")
                count = count + 1                                  
            
            # Break the loop if the items is empty (no more tags to fetch)
            if 1 == count:
                print(f'No more data found at page {page}. Stopping.', flush=True)
                break
        else:
            print('http response ' + str(req.status_code))

def SingleDownload(url):
    if str(url).__contains__('e621.net') is False:
        print("Unknown url -> ", url)
        return

    print("Loading single page-> ", url)
        
    # Fetch url
    success, req = RequestWithRetires(url, retrie_times)
    if False == success:
        print('*** Page open Failed!!!')
    
    # 200 Http Success
    if 200 == req.status_code:
        data = BeautifulSoup(req.text,"html.parser")    
    #print(data)
    
    items = data.find_all("section", class_='blacklistable')
    #print(items)
    img_url = items[0].get('data-file-url')
    img_filename = str(items[0].get('data-md5')) + '.' + str(items[0].get('data-file-ext'))
    tags = items[0].get('data-tags')
    tag_filename = str(items[0].get('data-md5')) + '.txt'
    print('img_url = ' , img_url)    
    #print('img_filename = ', img_filename)    
    #print('tags = ', tags)    
    
    success, img_req = RequestWithRetires(img_url, retrie_times)
    if False == success:
        print('*** Image Download Failed!!!')
    elif 200 == img_req.status_code:
        img_save = os.path.join(save_patch, img_filename)
        with open(img_save, 'wb') as saveFile:
            saveFile.write(img_req.content)    
            
        tags_replaced = str(tags).replace(' ', ',')
        print(tags_replaced)
        tags_save = os.path.join(save_patch, tag_filename)
        with open(tags_save, 'wb') as saveFile:
            saveFile.write(bytes(tags_replaced, 'utf-8'))
            
        print('Image and Tags saved!')    
    else:
        print('*** Image Download Failed with Http code ' + str(img_req.status_code))

def main(): 
    argc = len(sys.argv)
    if 1 == argc:
        SearchDownload()
    elif 2 == argc:
        SingleDownload(sys.argv[1])
    else:
        print('unknown args: ')
        for v in sys.argv:
            print (v)

if __name__ == '__main__':
  main()        
