from bs4 import BeautifulSoup as bs
import requests
import re

class RequestException:
    pass

class IntegrityError:
    pass

#@shared_task(name='tasks.check_susiso_notices')
def check_ssu_notices():
    url = 'http://smartsw.ssu.ac.kr'
    url_noti = 'http://smartsw.ssu.ac.kr/rb/?c=2/38'
    try:
        r = requests.get(url_noti)
    except RequestException:
        return
    date = re.compile(r"\d{4}.\d{2}.\d{2}")  # date pattern YYYY.MM.DD
    soup = bs(r.text, 'html.parser')
    bbs = soup.find('div', {'id': 'bbslist'})
    titles = [noti.text for\
              noti in bbs.find_all('span', {'class': 'subject'})]
    dates = [re.search(date, tr.text).group()\
             for tr in bbs.find_all('div', {'class': 'info'})]
    links = [url+re.search(r'/rb.*\d{4}', tr.get('onclick')).group()\
             for tr in bbs.find_all('div', {'class': 'list'})]
    ids = [re.search(r'uid=(\d{4})', tr.get('onclick')).groups()[0]\
           for tr in bbs.find_all('div', {'class': 'list'})]

    items = list(zip(titles, dates, links, ids))
    for title, date, link, post_id in items:
        try:
            post, created = Post.objects.get_or_create(
                post_id=post_id,
                type=Post.SUSISO_NOTICE,
                date=date)

            if created:
                post.title = title
                post.url = link
                post.type = Post.SUSISO_NOTICE
                post.new_post = True
                post.save()
        except IntegrityError:
            pass