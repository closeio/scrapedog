from scraper import *

fh = open('templates/test.html')
html = fh.read()
scraper = ScrapeDog(page=html)

soup = scraper.soup

body = soup.html.body
contact2 = soup.find('div', id='contact2')
email2 = contact2.p
div_wrap = soup.find('div', id='wrap')

assert str(email2.string) == 'email:onlyone@justemail.com'

email2_parents = get_all_parents(email2)
assert len(email2_parents) == 5
assert email2_parents[-1] == email2.parent

footer_email = soup.find('p', id='footer')
assert str(footer_email.string) == 'footer: site@webmaster.com'

assert len(get_common_parents(email2, footer_email)) == 3

assert email2 == closest_common_parent(email2, email2)

assert len(get_common_parents(contact2, email2)) == 5

assert body == closest_common_parent(email2, footer_email)

assert contact2 == closest_common_parent(email2, contact2)

phone_tags = soup.find_all('li')
assert div_wrap == closest_common_parent(phone_tags[0], phone_tags[2])

phone_tags_by_common_parent = group_by_common_parent(phone_tags)
assert len(phone_tags_by_common_parent[div_wrap]) == 4

email_tags = soup.find_all('p', {'class':'email'}) + soup.find_all('a', {'class':'email'})
assert len(email_tags) == 7

assert body == closest_common_parent(footer_email, email_tags[4])

email_tags_by_common_parent = group_by_common_parent(email_tags)
assert len(email_tags_by_common_parent[body]) == 7

interesting_tags = list(set(email_tags + phone_tags))
interesting_tags_by_common_parent = group_by_common_parent(interesting_tags)
for k,v in interesting_tags_by_common_parent.iteritems():
    print k.name, k.get('id'), len(v)



if 0:
    print type(x),
    if hasattr(x,'name'):
        print x.name, x.get('id')
    else:
        print '*',str(x),'*'



print 'All good'

