import argparse
from instagrapi import Client
from instagrapi.exceptions import ClientError, LoginRequired, TwoFactorRequired
import os
import re
from pathlib import Path
import shutil
import logging
import getpass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        pass

    def add_arguments(self, actions):
        pass

def clear_directory(path):
    try:
        if os.path.exists(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'[*] Error deleting {file_path}: {e}')
        return True
    except Exception as e:
        print(f'[*] Error clearing directory {path}: {e}')
        return False

def login_instagram(username, password):
    try:
        cl = Client()
        cl.delay_range = [1, 3]
        logger.info(f"Attempting login with username: {username}")
        try:
            if cl.login(username, password):
                logger.info("Login successful without 2FA")
                return cl
        except TwoFactorRequired:
            print("[*] Two-factor authentication required")
            verification_code = input("[*] Enter the 2FA code from your authenticator app: ")
            try:
                if cl.login(username, password, verification_code=verification_code):
                    logger.info("Login successful with 2FA")
                    return cl
                else:
                    logger.error("Login failed with 2FA")
                    return None
            except ClientError as e:
                print(f'[*] Error logging in with 2FA: {e}')
                return None
        logger.error("Login failed")
        return None
    except ClientError as e:
        print(f'[*] Error logging in: {e}')
        return None
    except Exception as e:
        print(f'[*] Unexpected error logging in: {e}')
        return None

def get_posts_count(client, username):
    try:
        user = client.user_info_by_username(username)
        post_count = user.media_count
        print(f"[*] The account @{username} has {post_count} posts")
        return post_count
    except ClientError as e:
        print(f'[*] Error getting post count: {e}')
        return None

def upload_post(client, image_path, caption):
    try:
        if not os.path.exists(image_path):
            print(f'[*] The file {image_path} does not exist')
            return None
        media = client.photo_upload(image_path, caption)
        print(f"[*] Post uploaded successfully: {media.pk}")
        return media
    except ClientError as e:
        print(f'[*] Error uploading post: {e}')
        return None

def remove_posts(client, post_id, range_lower=None, range_upper=None):
    try:
        if isinstance(post_id, str) and post_id.lower() == "all":
            user_id = client.user_id_from_username(client.username)
            medias = client.user_medias(user_id)
            if not medias:
                print("[*] No posts to delete")
                return 0
            deleted_count = 0
            for media in medias:
                client.media_delete(media.pk)
                print(f"[*] Post {media.pk} deleted")
                deleted_count += 1
            print(f"[*] Deleted all posts ({deleted_count} in total)")
            return deleted_count
        if range_lower is None and range_upper is None:
            range_lower = post_id
            range_upper = post_id
        elif range_lower is not None and range_upper is not None:
            pass
        else:
            print("[*] Must specify both range limits or none")
            return 0
        user_id = client.user_id_from_username(client.username)
        medias = client.user_medias(user_id, amount=range_upper + 1)
        if not medias:
            print("[*] No posts to delete")
            return 0
        range_lower = max(0, range_lower)
        range_upper = min(len(medias) - 1, range_upper)
        deleted_count = 0
        for i in range(range_lower, range_upper + 1):
            media = medias[i]
            client.media_delete(media.pk)
            print(f"[*] Post {media.pk} deleted (index {i})")
            deleted_count += 1
        print(f"[*] Deleted {deleted_count} posts")
        return deleted_count
    except ClientError as e:
        print(f'[*] Error deleting posts: {e}')
        return 0

def download_posts(client, username, post_id, range_lower=None, range_upper=None):
    try:
        posts_dir = Path("posts")
        images_dir = posts_dir / "images"
        desc_file = posts_dir / "descriptions.txt"
        images_dir.mkdir(parents=True, exist_ok=True)
        if not clear_directory(images_dir):
            print("[*] Error clearing image directory")
            return 0
        else:
            print("[*] Previous image directory deleted")
        if desc_file.exists():
            try:
                desc_file.unlink()
                print("[*] Previous descriptions.txt file deleted")
            except Exception as e:
                print(f'[*] Error deleting descriptions.txt: {e}')
                return 0
        if isinstance(post_id, str) and post_id.lower() == "all":
            user_id = client.user_id_from_username(username)
            medias = client.user_medias(user_id)
            if not medias:
                print("[*] No posts to download")
                return 0
            downloaded_count = 0
            descriptions = []
            for i, media in enumerate(medias):
                try:
                    if media.media_type == 1:
                        extension = ".jpg"
                        media_content = client.photo_download(media.pk)
                    elif media.media_type == 2 and media.product_type == "feed":
                        extension = ".mp4"
                        media_content = client.video_download(media.pk)
                    else:
                        print(f"[*] Unsupported media type for post {i}")
                        continue
                    file_path = images_dir / f"{i}{extension}"
                    if isinstance(media_content, Path):
                        media_content.replace(file_path)
                    else:
                        with open(file_path, 'wb') as f:
                            f.write(media_content.getbuffer() if hasattr(media_content,
                                                                         'getbuffer') else media_content.read())
                    description = media.caption_text if media.caption_text else "No description"
                    descriptions.append(f'"POST {i}" : "{description}"\n\n')
                    downloaded_count += 1
                    print(f"[*] Post {i} downloaded successfully")
                except Exception as e:
                    print(f'[*] Error downloading post {i}: {str(e)}')
                    continue
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.writelines(descriptions)
            print(f"[*] Downloaded all posts ({downloaded_count} in total)")
            return downloaded_count
        if range_lower is None and range_upper is None:
            range_lower = post_id
            range_upper = post_id
        elif range_lower is not None and range_upper is not None:
            pass
        else:
            print("[*] Must specify both range limits or none")
            return 0
        user_id = client.user_id_from_username(username)
        medias = client.user_medias(user_id, amount=range_upper + 1)
        if not medias:
            print("[*] No posts to download")
            return 0
        range_lower = max(0, range_lower)
        range_upper = min(len(medias) - 1, range_upper)
        downloaded_count = 0
        descriptions = []
        for i in range(range_lower, range_upper + 1):
            media = medias[i]
            unique_id = i
            try:
                if media.media_type == 1:
                    extension = ".jpg"
                    media_content = client.photo_download(media.pk)
                elif media.media_type == 2 and media.product_type == "feed":
                    extension = ".mp4"
                    media_content = client.video_download(media.pk)
                else:
                    print(f"[*] Unsupported media type for post {unique_id}")
                    continue
                file_path = images_dir / f"{unique_id}{extension}"
                if isinstance(media_content, Path):
                    media_content.replace(file_path)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(
                            media_content.getbuffer() if hasattr(media_content, 'getbuffer') else media_content.read())
                description = media.caption_text if media.caption_text else "No description"
                descriptions.append(f'"POST {unique_id}" : "{description}"\n\n')
                downloaded_count += 1
                print(f"[*] Post {unique_id} downloaded successfully")
            except Exception as e:
                print(f'[*] Error downloading post {unique_id}: {str(e)}')
                continue
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.writelines(descriptions)
        print(f"[*] Downloaded {downloaded_count} posts (IDs from {range_lower} to {range_upper})")
        return downloaded_count
    except ClientError as e:
        print(f'[*] Error downloading posts: {e}')
        return 0
    except Exception as e:
        print(f'[*] Unexpected error: {e}')
        return 0

def upload_posts_from_files(client, post_id, range_lower=None, range_upper=None):
    try:
        images_dir = Path("posts/images")
        desc_file = Path("posts/descriptions.txt")
        if not images_dir.exists():
            print("[*] The image directory posts/images does not exist")
            return 0
        if not desc_file.exists():
            print("[*] The descriptions file posts/descriptions.txt does not exist")
            return 0
        with open(desc_file, 'r', encoding='utf-8') as f:
            descriptions_content = f.read()
        descriptions = {}
        pattern = r'"POST (\d+)" : "([^"]*)"'
        matches = re.findall(pattern, descriptions_content)
        for num, desc in matches:
            descriptions[int(num)] = desc
        if not descriptions:
            print("[*] No valid descriptions found in the file")
            return 0
        image_files = {}
        for ext in ['.jpg', '.jpeg', '.png', '.mp4']:
            for img in images_dir.glob(f'*{ext}'):
                try:
                    num = int(img.stem)
                    image_files[num] = img
                except ValueError:
                    continue
        if not image_files:
            print("[*] No images with valid numeric names found")
            return 0
        common_numbers = set(descriptions.keys()) & set(image_files.keys())
        if not common_numbers:
            print("[*] No matches between image and description numbers")
            return 0
        sorted_numbers = sorted(common_numbers, reverse=True)
        
        if isinstance(post_id, str) and post_id.lower() == "all":
            selected_numbers = sorted_numbers
        else:
            if range_lower is None and range_upper is None:
                range_lower = post_id
                range_upper = post_id
            elif range_lower is None or range_upper is None:
                print("[*] Must specify both range limits or none")
                return 0
            range_lower = max(0, range_lower)
            range_upper = min(max(sorted_numbers), range_upper)
            selected_numbers = [num for num in sorted_numbers if range_lower <= num <= range_upper]
        
        if not selected_numbers:
            print("[*] No posts in the specified range to upload")
            return 0
        
        uploaded_count = 0
        for num in selected_numbers:
            img_path = image_files[num]
            caption = descriptions[num]
            try:
                print(f"[*] Uploading post {num}")
                media = upload_post(client, str(img_path), caption)
                if media:
                    uploaded_count += 1
            except Exception as e:
                print(f'[*] Error uploading post {num}: {str(e)}')
                continue
        if isinstance(post_id, str) and post_id.lower() == "all":
            print(f"[*] Uploaded all posts ({uploaded_count} in total)")
        else:
            print(f"[*] Uploaded {uploaded_count} posts (IDs from {range_lower} to {range_upper})")
        return uploaded_count
    except Exception as e:
        print(f'[*] Unexpected error in upload_posts_from_files: {e}')
        return 0

def main():
    parser = argparse.ArgumentParser(
        formatter_class=CustomHelpFormatter,
        description=(
            "[*] Usage: instagramManager.py -u <USER> -p <PASSWORD> -f <FUNCTION>\n\n"
            "Options:\n"
            "  -h, --help             Show this help menu\n"
            "  -u, --user             Instagram username\n"
            "  -p, --password         Instagram password\n"
            "  -f, --function         Function to execute\n\n"
            "Functions:\n"
            "  getPosts               Get the number of posts (no parameters)\n"
            "  removePosts            Delete posts (all, post_id, range_lower range_upper)\n"
            "  uploadPost             Upload a post (image_path description)\n"
            "  downloadPosts          Download posts (all, post_id, range_lower range_upper)\n"
            "  uploadFromFiles        Upload posts from files (all, post_id, range_lower range_upper)"
        )
    )
    parser.add_argument("-u", "--user", required=True, help="Instagram username")
    parser.add_argument("-p", "--password", required=True, help="Instagram password")
    parser.add_argument("-f", "--function", required=True,
                        choices=["getPosts", "removePosts", "uploadPost", "downloadPosts", "uploadFromFiles"],
                        help="Function to execute (see above for details)")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()
    if args.function in ["removePosts", "downloadPosts", "uploadFromFiles"] and len(args.args) not in (1, 2):
        parser.error(f"{args.function} requires 1 or 2 arguments: all, post_id, range_lower range_upper")
    if args.function == "uploadPost" and len(args.args) != 2:
        parser.error("uploadPost requires two arguments: image_path and description")
    client = login_instagram(args.user, args.password)
    if not client:
        return
    if args.function == "getPosts":
        get_posts_count(client, args.user)
    elif args.function == "removePosts":
        try:
            if args.args[0].lower() == "all":
                remove_posts(client, "all")
            elif len(args.args) == 1:
                post_id = int(args.args[0])
                if post_id < 0:
                    print("[*] Post ID must be non-negative")
                    return
                remove_posts(client, post_id)
            else:
                range_lower = int(args.args[0])
                range_upper = int(args.args[1])
                if range_lower < 0 or range_upper < range_lower:
                    print(
                        "[*] Range limits must be non-negative and range_upper must be greater than or equal to range_lower")
                    return
                remove_posts(client, None, range_lower, range_upper)
        except ValueError:
            print("[*] Arguments must be 'all' or integers")
    elif args.function == "uploadPost":
        image_path = args.args[0]
        caption = args.args[1]
        upload_post(client, image_path, caption)
    elif args.function == "downloadPosts":
        try:
            if args.args[0].lower() == "all":
                download_posts(client, args.user, "all")
            elif len(args.args) == 1:
                post_id = int(args.args[0])
                if post_id < 0:
                    print("[*] Post ID must be non-negative")
                    return
                download_posts(client, args.user, post_id)
            else:
                range_lower = int(args.args[0])
                range_upper = int(args.args[1])
                if range_lower < 0 or range_upper < range_lower:
                    print(
                        "[*] Range limits must be non-negative and range_upper must be greater than or equal to range_lower")
                    return
                download_posts(client, args.user, None, range_lower, range_upper)
        except ValueError:
            print("[*] Arguments must be 'all' or integers")
    elif args.function == "uploadFromFiles":
        try:
            if args.args[0].lower() == "all":
                upload_posts_from_files(client, "all")
            elif len(args.args) == 1:
                post_id = int(args.args[0])
                if post_id < 0:
                    print("[*] Post ID must be non-negative")
                    return
                upload_posts_from_files(client, post_id)
            else:
                range_lower = int(args.args[0])
                range_upper = int(args.args[1])
                if range_lower < 0 or range_upper < range_lower:
                    print(
                        "[*] Range limits must be non-negative and range_upper must be greater than or equal to range_lower")
                    return
                upload_posts_from_files(client, None, range_lower, range_upper)
        except ValueError:
            print("[*] Arguments must be 'all' or integers")

if __name__ == "__main__":
    main()
