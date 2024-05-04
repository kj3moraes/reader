import json
import os
import re
import urllib.request
from datetime import datetime
from html import unescape
from typing import Optional
from urllib.parse import urlparse, urljoin

import html2text
import requests
from bs4 import BeautifulSoup
import bs4
from tqdm import tqdm

class Post:
    def __init__(self, data):
        self.id = data["id"]
        self.publication_id = data["publication_id"]
        self.type = data["type"]
        self.slug = data["slug"]
        self.post_date = data["post_date"]
        self.canonical_url = data["canonical_url"]
        self.previous_post_slug = data["previous_post_slug"]
        self.next_post_slug = data["next_post_slug"]
        self.cover_image = data["cover_image"]
        self.description = data["description"]
        self.wordcount = data["wordcount"]
        self.title = data["title"]
        self.body_html = data["body_html"]

    def to_markdown(self, with_title=True):
        title = f"# {self.title}\n\n" if with_title else ""
        body = html2text.html2text(unescape(self.body_html))
        return title + body

    def to_text(self, with_title=True):
        title = f"{self.title}\n\n" if with_title else ""
        body = html2text.html2text(unescape(self.body_html))
        return title + body

    def to_html(self, with_title=True):
        title = f"<h1>{self.title}</h1>\n\n" if with_title else ""
        return title + self.body_html

    def to_json(self):
        return json.dumps(self.__dict__, indent=2)

    def write_to_file(self, path, format):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            if format == "html":
                f.write(self.to_html(with_title=True))
            elif format == "md":
                f.write(self.to_markdown(with_title=True))
            elif format == "txt":
                f.write(self.to_text(with_title=True))
            else:
                raise ValueError(f"Unknown format: {format}")

def convert_datetime(datetime_str):
    dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    return dt.strftime("%Y%m%d_%H%M%S")

def extract_slug(url):
    return urlparse(url).path.split("/")[-1]

def make_path(post, output_folder, format):
    slug = extract_slug(post.canonical_url)
    return os.path.join(output_folder, f"{convert_datetime(post.post_date)}_{slug}.{format}")

def find_script_content(html):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", text=re.compile(r"window\._preloads"))
    if script:
        return script.string
    return None

def extract_json_string(script_content):
    match = re.search(r'JSON.parse\("(.+?)"\)', script_content)
    if match:
        return match.group(1)
    return None

class Extractor:
    def __init__(self, session=None):
        self.session = session or requests.Session()

    def extract_post(self, page_url):
        response = self.session.get(page_url)
        response.raise_for_status()
        print(f"\n\n\n\n{page_url}\n\n\n\n")
        print(response.text)
        # script_content = find_script_content(response.text)
        # if not script_content:
        #     raise ValueError("Script content not found")
        # json_string = extract_json_string(script_content)
        # if not json_string:
        #     raise ValueError("JSON string not found")
        # raw_json = json.loads(f'"{json_string}"')
        # post_data = raw_json["post"]
        post_data = "adas"
        return Post(post_data)

    def get_all_posts_urls(self, pub_url, date_filter=None):
        sitemap_url = urljoin(pub_url, "sitemap.xml")
        response = self.session.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, features="lxml")
        urls = []
        for url_tag in soup.find_all("url"):
            url_str: str
            url_str = url_tag.loc.text 
            if "/p/" in url_str: 
                urls.append(url_str)
        return urls

    def extract_all_posts(self, urls):
        urls = urls[:1]
        for url in tqdm(urls, unit="post", desc="Downloading posts"):
            try:
                yield self.extract_post(url)
            except Exception as e:
                print(f"Error downloading post {url}: {e}")

def download_posts(extractor, output_folder, format, pub_url=None, post_url=None, dry_run=False, verbose=False, before_date=None, after_date=None):
    if post_url:
        if verbose:
            print(f"Downloading post {post_url}")
        if not dry_run:
            post = extractor.extract_post(post_url)
            path = make_path(post, output_folder, format)
            if verbose:
                print(f"Writing post to file {path}")
            post.write_to_file(path, format)
    else:
        date_filter = None
        if before_date or after_date:
            def date_filter(date_str):
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                if before_date and date >= before_date:
                    return False
                if after_date and date <= after_date:
                    return False
                return True

        urls = extractor.get_all_posts_urls(pub_url, date_filter)
        if verbose:
            print(f"Found {len(urls)} posts")
        if dry_run:
            print(f"Found {len(urls)} posts")
            print("Dry run, exiting...")
            return

        for post in extractor.extract_all_posts(urls):
            path = make_path(post, output_folder, format)
            if verbose:
                print(f"Writing post to file {path}")
            if not dry_run:
                post.write_to_file(path, format)