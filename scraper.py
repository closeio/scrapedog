import sys
import itertools
import collections
import re
import requests
import phonenumbers
import string
from lib.map import GoogleMap

from bs4 import BeautifulSoup, NavigableString


class BasicMixin():
    def get_basic_content(self):
        meta_tags = []
        meta_tags_bs = self.soup.find_all('meta')
        for meta in meta_tags_bs:
            meta_tags.append(meta.attrs)

        return {
            'url': self.url,
            'title': self.soup.title.string if self.soup.title else '',
            'headers': self.request.headers if self.request else [],
            'meta_tags': meta_tags,
        }

parents_cache = {}
def get_all_parents(el):
    # from root down to parent of el
    if parents_cache.get(el):
        return parents_cache.get(el)
    els = list(reversed(list(el.parents)))
    parents_cache[el] = els
    return els

def get_all_children(el):
    # remove blanks
    lst = []
    for el in el.children:
        if hasattr(el, 'name'):
            lst.append(el)
    return lst

def root_to_el(el):
    els = get_all_parents(el)
    els.append(el)
    return els

common_parents_cache = {}
def get_common_parents(a, b):
    print 'get_common_parents', print_el(a), print_el(b)
    if common_parents_cache.get((a, b)):
        return common_parents_cache.get((a, b))

    # from root down to nearest common element -- could be one of a or b
    parents_a = root_to_el(a)
    parents_b = root_to_el(b)
    common = []
    for a, b in zip(parents_a, parents_b):
        if a == b:
            common.append(a)
    common_parents_cache[(a,b)] = common
    common_parents_cache[(b,a)] = common
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

def print_el(el):
    if hasattr(el, 'get'):
        if el.get('id'):
            return '<%s#%s: %s>' % (el.name, el.get('id'), el.string)
        else:
            return '<%s: %s>' % (el.name, el.string)
    else:
        return '<%s>' % str(el)

def group_by_common_parent(els):
    common_parents = collections.defaultdict(set)
    for a in els:
        for b in els:
            if a == b:
                continue
            parent = closest_common_parent(a, b)
            common_parents[parent].add(a)
            common_parents[parent].add(b)
    return common_parents


class ContactMixin():

    def find_emails(self, parent=None):
        # find email addresses as an element's text or in an a.href
        parent = parent or self.soup
        email_re = re.compile('[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.\-0-9a-zA-Z]*.[a-zA-Z]+')
        email_tags = parent.find_all(text=email_re) + parent.find_all('a', href=email_re)
        emails = [email_re.findall(unicode(x.get('href')[len('mailto:'):] if hasattr(x, 'href') else x.string)) for x in email_tags] or []
        emails = list(itertools.chain(*emails)) # flatten array
        return (emails, email_tags)

    def find_urls(self, parent=None):
        # find full urls as an element's text or in an a.href
        parent = parent or self.soup
        url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        url_tags = parent.find_all(text=url_re) + parent.find_all('a', href=url_re)
        url_tags = [x for x in url_tags if x != self.soup.contents[0]] # throw out root tag
        urls = [url_re.findall(unicode(x.get('href') if hasattr(x, 'href') else x.string)) for x in url_tags] or []
        urls = list(itertools.chain(*urls)) # flatten array
        return (urls, url_tags)

    def find_phones(self, parent=None):
        parent = parent or self.soup
        # get list of all phone numbers found anywhere in page (kept in their original format)
        phones_found = phonenumbers.PhoneNumberMatcher(parent.get_text(), 'US')
        phones = [x.raw_string for x in phones_found]

        # now find tags those phone numbers are in
        def find_phones(tag):
            for phone in phones:
                if string.find(tag, phone) != -1:
                    return True
        phone_tags = parent.find_all(text=find_phones)
        return (phones, phone_tags)

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
        returns = {0:[tag1, tag2], 3:[tag3, tag4, tag5], 7: [tag6]}

    def find_addresses(self):
        citystate_re = re.compile('(.*)([a-zA-Z]{2}),?\s+([0-9]{5})')
        address_re = re.compile('([0-9]{1,5})\s+(.*),?\s+(.*)')
        gm = GoogleMap()
        address = []
        full_address = {}
        full_address['soup'] = []
        full_address['fulladdress'] = []
        def test(soup, depth):
            if hasattr(soup, 'children'):
                for children in soup.children:
                    test(children, depth + 1)
            elif soup.string.strip(' \n\t'):
                address_temp = address_re.match(soup.string.strip(' \n\t'))
                if address_temp and len(address_temp.groups()):
                    print type(gm.check_address(soup.string))
                    if gm.check_address(soup.string):
                        full_address['soup'].append(soup)
                        full_address['fulladdress'].append(gm.check_address(soup.string))
                    else:
                        address.append(soup)

        test(self.soup.find('html'), 0)
        
        def combine_address(soup):
            str = ''
            if hasattr(soup, 'children'):
                for children in soup.children:
                    str += combine_address(children)
            else:
                str += soup
                
            return str
        
        def combine_siblings(soup):
            found = False
            addy = combine_address(soup)
            
            if hasattr(soup, 'next_siblings') and soup.next_siblings:
                for sibling in soup.next_siblings:
                    addy += sibling.string
                    if gm.check_address(addy):
                        full_address['soup'].append(soup)
                        full_address['fulladdress'].append(gm.check_address(addy))
                        found = True
                        break
            return found
                
        for soup in address:
            addy = combine_address(soup.parent)
            if gm.check_address(addy):
                full_address['soup'].append(soup)
                full_address['fulladdress'].append(gm.check_address(addy))
            else:
                addy = combine_address(soup)
                if gm.check_address(addy):
                    full_address['soup'].append(soup.parent.parent)
                    full_address['fulladdress'].append(gm.check_address(addy))
                else:
                    if not combine_siblings(soup):
                        if not combine_siblings(soup.parent):
                            combine_siblings(soup.parent.parent)
            
        
        return full_address

    def build_contact(self, parent, list_interesting_children=None):
        emails, email_tags = self.find_emails(parent)
        phones, phone_tags = self.find_phones(parent)
        urls, url_tags = self.find_urls(parent)
        return {
            'emails': emails,
            'email_tags': [unicode(x.parent) for x in email_tags] or [],
            'phones': phones,
            'phone_tags': [unicode(x.parent) for x in phone_tags] or [],
            'urls': urls,
            'url_tags': [unicode(x.parent) for x in url_tags] or [],
        }
               
    def get_contact_content(self):

        emails, email_tags = self.find_emails()
        phones, phone_tags = self.find_phones()
        urls, url_tags = self.find_urls()
        interesting_tags = list(set(email_tags + phone_tags + url_tags))
        address = self.find_addresses()

        print len(interesting_tags), 'interesting tags'

        #if interesting_tags:
        #self.rings_of_closeness(interesting_tags[0], interesting_tags)

        root = []
        group = sorted(group_by_common_parent(interesting_tags).iteritems())

        print len(group), 'group'


        for parent, children in group:
            """
            print ''
            print ''
            print print_el(parent), len(children)
            """
            contacts = []
            for contact in get_all_children(parent):
                contact = self.build_contact(contact, children)
                contacts.append(contact)
            root.append({print_el(parent): contacts})

        return {
            'root': root or [],
        }
#            'interesting_tags': [unicode(x.parent) for x in interesting_tags] or [],
        return {
            'emails': emails,
            'email_tags': [unicode(x.parent) for x in email_tags] or [],
            'phones': phones,
            'phone_tags': [unicode(x.parent) for x in phone_tags] or [],
            'urls': urls,
            'url_tags': [unicode(x.parent) for x in url_tags] or [],
            'address' : address['fulladdress']
        }



class ScrapeDog(BasicMixin, ContactMixin):

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page', '')
        self.url = kwargs.pop('url', '')
        self.request = None
        if not self.page:
            self.request = requests.get(self.url)
            self.page = self.request.text.strip()
        self.orig_soup = BeautifulSoup(self.page)

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

