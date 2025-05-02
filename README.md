# Instagram Manager
A Python script to manage Instagram posts using the instagrapi library. Features include retrieving post counts, uploading and downloading posts, deleting posts, and uploading posts from local files with captions

# Features
- Retrieve the total number of posts for an Instagram account
- Delete all posts, a specific post, or a range of posts
- Upload a single post with an image or video and a caption
- Download all posts, a specific post, or a range of posts with captions
- Upload posts from local files with corresponding captions

# Usage
```
git clone https://github.com/Justice-Reaper/instagram-manager.git
cd instagram-manager
pip install instagrapi
python instagramManager.py -u <username> -p <password> -f <function>
```

# Help Panel
If the script is used incorrectly, an error message will appear, and the help panel will be displayed

```
# python instagramManager.py -h
[*] Usage: instagramManager.py -u <USER> -p <PASSWORD> -f <FUNCTION>

Options:
  -h, --help             Show this help menu
  -u, --user             Instagram username
  -p, --password         Instagram password
  -f, --function         Function to execute

Functions:
  getPosts               Get the number of posts (no parameters)
  removePosts            Delete posts (all, post_id, range_lower range_upper)
  uploadPost             Upload a post (image_path description)
  downloadPosts          Download posts (all, post_id, range_lower range_upper)
  uploadFromFiles        Upload posts from files (all, post_id, range_lower range_upper)
```
# Post Count Retrieval
Retrieve the number of posts for the specified Instagram account using the `getPosts` function

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f getPosts
```

# Post Deletion
Delete all posts with the `removePosts all` command

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f removePosts all
```

Delete a specific post by providing its ID with `removePosts <post_id>`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f removePosts 0
```

Delete a range of posts by specifying the lower and upper bounds with `removePosts <range_lower> <range_upper>`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f removePosts 0 2
```

# Post Upload
Upload a single post with an image or video and a caption using the `uploadPost` function

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f uploadPost image.jpg 'testing'
```

# Post Download
Download all posts with the `downloadPosts all` command, saving images/videos to `posts/images/` and captions to `posts/descriptions.txt`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f downloadPosts all
```

Download a specific post by providing its ID with `downloadPosts <post_id>`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f downloadPosts 0
```

Download a range of posts by specifying the lower and upper bounds with `downloadPosts <range_lower> <range_upper>`

```
#  python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f downloadPosts 0 2
```

# Upload from Files
Upload posts from local files using the `uploadFromFiles` function. Expects images/videos in `posts/images/` and captions in `posts/descriptions.txt`

Upload all posts with `uploadFromFiles all`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f uploadFromFiles all
```

Upload a specific post by providing its ID with `uploadFromFiles <post_id>`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f uploadFromFiles 0
```

Upload a range of posts by specifying the lower and upper bounds with `uploadFromFiles <range_lower> <range_upper>`

```
# python instagramManager.py -u 'pentestingacademy2' -p 'Ser.ab.20021' -f uploadFromFiles 0 2
```
