"""wallabag input processor"""
try:
    from html2text import HTML2Text
    from urllib.parse import urljoin as j
    import json
    import requests
except ImportError as e:
    print(
        f'Failed to import required module: {e}\n'
        'Do you need to run pip install -r requirements.txt?')
    exit()

from logger import Logger


class Wallabag(object):
    """wallabag processor"""

    def __init__(self, config, log=None):
        self.url = config.url
        self.log = log if log else Logger(debug=True)
        self.username = config.username
        self.password = config.password
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        auth_url = j(self.url, 'oauth/v2/token')
        auth_data = {'username': self.username,
                     'password': self.password,
                     'client_id': self.client_id,
                     'client_secret': self.client_secret,
                     'grant_type': 'password'}
        login = requests.post(auth_url, data=auth_data, timeout=60)
        token = json.loads(login.content)
        self.log.write(f'wallabag username: {self.username}')
        self.log.write(f'wallabag token: {token}')
        self.access_token = token['access_token']

    def get_items(self, tag):
        """retrieve URLs and content from Wallabag repository"""
        entries_url = j(
            self.url, 'api/entries.json?'
            f'tags={tag}&sort=created&order=asc&page=1&perPage=500&since=0&detail=full')
        headers = {"Authorization": f"Bearer {self.access_token}"}
        entries_request = requests.get(
            entries_url, headers=headers, timeout=60)
        entries_response = json.loads(entries_request.content)
        entries = entries_response['_embedded']['items']
        h = HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        all_entries = []
        for entry in entries:
            title = entry['title']
            text = h.handle(entry['content'])
            url = h.handle(entry['url'])
            this_entry = (title, text, url)
            all_entries.append(this_entry)
        return all_entries
