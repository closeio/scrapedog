import re
import requests
import phonenumbers

from bs4 import BeautifulSoup

class BasicMixin():
    def get_basic_content(self):
        meta_tags = []
        meta_tags_bs = self.soup.find_all('meta')
        for meta in meta_tags_bs:
            meta_tags.append(meta.attrs)

        return {
            'url': self.url,
            'title': self.soup.title.string,
            'headers': self.request.headers,
            'meta_tags': meta_tags,
        }


class ContactMixin():
    def get_contact_content(self):

        # http://www.noah.org/wiki/RegEx_Python#email_regex_pattern
        email_re = re.compile('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+')
        url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        phonenumber_re = re.compile(phonenumbers.phonenumberutil._VALID_PHONE_NUMBER)

        phone_tags = self.soup.find_all(text=phonenumber_re)
        phones = [unicode(x) for x in phone_tags] or []

        email_tags = self.soup.find_all(text=email_re)
        emails = [unicode(x) for x in email_tags] or []

        return {
            'contacts': [],
            'emails': emails,
            'phone': phones,
        }



class ScrapeDog(BasicMixin, ContactMixin):

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        self.request = requests.get(self.url)
        self.soup = BeautifulSoup(self.request.text)

    def get_content(self):
        content = self.get_basic_content()
        contacts = self.get_contact_content()
        content.update(contacts)
        return content

