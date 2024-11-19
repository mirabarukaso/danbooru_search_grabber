# Usage
A simple script

## Modify the download file path
Change to your local directory    
```
save_patch = 'f:\\danbooru_grabbing\\'    
```

## Search keywords
Only supports 2 keywords    
```
[Key1]+[key2]
my_tags = 'furry+veemon'
```

## Parameters
### No parameters - search for download mode    
```
python.exe danbooru_grab.py
```

### 1 parameter - Single url download mode
```
python.exe danbooru_grab.py https://danbooru.donmai.us/posts/6800322
```

## Filters
All filters can be left empty.    

| Name | Priority | Logic | Description |
| --- | --- | --- | --- |
|`my_blacklist`| Hightest | Any | The image will be ignored if `ANY tag in this list` appear in image tags. |
|`my_abs_filters`| High | Absolute | After the previous condition is satisfied, if the image tags does `NOT match all terms in this list`, the image is ignored. |
|`my_any_filters`| Normal | Any | After the previous condition is satisfied, the image will be `downloaded` if the image tags is a `match for one or more` of the conditions in this list. |
