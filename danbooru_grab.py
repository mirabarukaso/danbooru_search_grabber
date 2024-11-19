import os
import sys 
import requests
from bs4 import BeautifulSoup
import time

# base [DO NOT CHANGE]
base_url = 'https://danbooru.donmai.us/posts?page=[REPLACE_PAGE_INDEX]&tags=[REPLACE_TAGS]'

# save_patch [Change to what you want]
save_patch = 'f:\\danbooru_grabbing\\'

# my_tags for SearchDownload tags [Change to what you want]
# only 2 tags
my_tags = 'furry+fox_girl'

# page limit
start_page = 1
end_page = 1001

# HIGHEST priority: blacklist [Set to EMPTY if not needed] Any condition
my_blacklist = []
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
    # Sleep for 3 second so we don't DDOS Danbooru too much
    time.sleep(3)  
        
    req = None
    retries = 1
    success = False
    while not success and retries < rt_times:
        try:
            req = requests.get(url)    
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
                original_img = 'https://danbooru.donmai.us' + str(src)
                print('====== ' + str(count) + ' @ page ' + str(page) + '/' + str(end_page))      
                #print(item)  
                #print(src)
                #print(original_img)
                #print(tags)
                if True is any(x in tags for x in my_blacklist):
                    print("Bypass Black List")
                    print(tags)
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
    if str(url).__contains__('danbooru.donmai.us') is False:
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
    
    items = data.find_all("li", id='post-option-download')
    img_url = items[0].find('a').get('href')
    img_filename = items[0].find('a').get('download')
    #print(img_url)    
    #print(img_filename)    
    
    success, img_req = RequestWithRetires(img_url, retrie_times)
    if False == success:
        print('*** Image Download Failed!!!')
    elif 200 == img_req.status_code:
        img_save = os.path.join(save_patch, img_filename)
        with open(img_save, 'wb') as saveFile:
            saveFile.write(img_req.content)    
    
        items = data.find_all("section", class_='image-container note-container')
        tags = items[0].get('data-tags')
        #print(tags)
        tags_replaced = str(tags).replace(' ', ',')
        print(tags_replaced)
        tag_filename_all = str(img_filename).split('.')        
        tag_filename_all[len(tag_filename_all) - 1] = 'txt'
        tag_filename = tag_filename_all[0]
        for index in range(1, len(tag_filename_all)):
            tag_filename = tag_filename + '.' + tag_filename_all[index]
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
