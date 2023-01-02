import re
import requests
from bs4 import BeautifulSoup

URL = "https://sourcesup.renater.fr/scm/viewvc.php/rec/2019-CONVECS/REC/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
for link in soup.find_all('a', href=True):
    print(link['href'])
    if 'name' in link:
        print(link['name'])
    m = re.search(r"/(\w+)\.rec", link["href"])
    if m is not None:
        print(m.group(1))
        name = m.group(1)
        URL = f"https://sourcesup.renater.fr/scm/viewvc.php/rec/2019-CONVECS/REC/{name}.rec?revision=3&view=co"

        page = requests.get(URL)
        print(page.content)
        f = open(f"rec/{name}.rec", "wb")
        f.write(page.content)
        f.close()
