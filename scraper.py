import re
import requests
import phonenumbers
import string

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
        email_re = re.compile('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.\-0-9a-zA-Z]*.[a-zA-Z]+')
        url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

        # get list of all phone numbers found anywhere in page (kept in their original format)
        phones_found = phonenumbers.PhoneNumberMatcher(self.text_only, 'US')
        phones = [x.raw_string for x in phones_found]

        # now find tags those phone numbers are in
        def find_phones(tag):
            for phone in phones:
                if string.find(tag, phone) != -1:
                    return True
        phone_tags = self.soup.find_all(text=find_phones)

        # emails
        email_tags = self.soup.find_all(text=email_re)
        emails = [unicode(x.string) for x in email_tags] or []

        return {
            'contacts': [],
            'emails': emails,
            'email_tags': [unicode(x.parent) for x in email_tags] or [],
            'phones': phones,
            'phone_tags': [unicode(x.parent) for x in phone_tags] or [],
        }



class ScrapeDog(BasicMixin, ContactMixin):

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        self.request = requests.get(self.url)
        self.soup = BeautifulSoup(self.request.text)
        self.text_only = self.soup.get_text()

    def get_content(self):
        content = self.get_basic_content()
        contacts = self.get_contact_content()
        content.update(contacts)
        return content

