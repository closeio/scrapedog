import collections
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


def get_all_parents(el):
    # starting with root
    parents = []
    while el.parent:
        el = el.parent
        parents.insert(0, el)
    return parents

def get_common_parents(a, b):
    # from root down to nearest
    parents_a = get_all_parents(a)
    parents_b = get_all_parents(b)
    common = []
    for a, b in zip(parents_a, parents_b):
        if a == b:
            common.append(a)
    return common

def closest_common_parent(a, b):
    return get_common_parents(a, b)[-1]

def dist_to_common_parent(a, b):
    # find the distance from a to the common parent of a,b
    parent = closest_common_parent(a, b)
    return dist_to_parent(a, parent)

def dist_to_parent(el, parent):
    dist = 0
    while el.parent != parent:
        el = el.parent
        dist += 1
    return dist

def group_by_common_parent(els):
    return
    common_parents = collections.defaultdict(set)
    for a in els:
        for b in els:
            common_parents[closest_common_parent(a, b)].add(a)
            common_parents[closest_common_parent(a, b)].add(b)
    return common_parents


class ContactMixin():

    def find_emails(self):
        email_re = re.compile('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.\-0-9a-zA-Z]*.[a-zA-Z]+')
        email_tags = self.soup.find_all(text=email_re)
        emails = [unicode(x.string) for x in email_tags] or []
        return (emails, email_tags)

    def find_phones(self):
        # get list of all phone numbers found anywhere in page (kept in their original format)
        phones_found = phonenumbers.PhoneNumberMatcher(self.text_only, 'US')
        phones = [x.raw_string for x in phones_found]

        # now find tags those phone numbers are in
        def find_phones(tag):
            for phone in phones:
                if string.find(tag, phone) != -1:
                    return True
        phone_tags = self.soup.find_all(text=find_phones)
        return (phones, phone_tags)

    def find_urls(self):
        url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        url_tags = self.soup.find_all(text=url_re)
        urls = [unicode(x.string) for x in url_tags] or []
        return (urls, url_tags)

    def rings_of_closeness(self, keyable_tag, interesting_tags, max_items_considered = 50):
        tags_matrix = {}

        # O(n^2)
        for i_tag_x, tag_x in enumerate(interesting_tags):
            for i_tag_y, tag_y in enumerate(interesting_tags):
                tags_matrix[(i_tag_x, i_tag_y)] = dist_to_common_parent(tag_x, tag_y)

        L = tags_matrix.values()
        """
        print tags_matrix
        print len(L)
        print len(interesting_tags)
        print dict([(x, L.count(x)) for x in L])
        """

        """
        returns = {0:[tag1, tag2], 3:[tag3, tag4, tag5], 7: [tag6]}
        """

    def build_contact(self, parent, list_interesting_children):
        pass

    def get_contact_content(self):


        emails, email_tags = self.find_emails()
        phones, phone_tags = self.find_phones()
        urls, url_tags = self.find_urls()
        interesting_tags = list(set(email_tags + phone_tags))

        self.rings_of_closeness(interesting_tags[0], interesting_tags)

        # find common parent between phones/emails
        #for x in get_all_parents(email_tags[1]):

        # group each interesting tag by common parent
        # the same tag can appear in multiple common parents (like their grandparents)
        contacts = group_by_common_parent(interesting_tags)
        #print contacts

        return {
            'contacts': contacts or [],
            'emails': emails,
            'email_tags': [unicode(x.parent) for x in email_tags] or [],
            'phones': phones,
            'phone_tags': [unicode(x.parent) for x in phone_tags] or [],
            'urls': urls,
            'url_tags': [unicode(x.parent) for x in url_tags] or [],
            'interesting_tags': [unicode(x.parent) for x in interesting_tags] or [],
        }



class ScrapeDog(BasicMixin, ContactMixin):

    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        self.request = requests.get(self.url)
        self.orig_soup = BeautifulSoup(self.request.text)

        # store version of "cleaned up" soup
        self.soup = self.orig_soup
        for tag in self.soup.findAll('script'): # remove <script>s
            tag.extract()

        self.text_only = self.soup.get_text()

    def get_content(self):
        content = self.get_basic_content()
        contacts = self.get_contact_content()
        content.update(contacts)
        return content

