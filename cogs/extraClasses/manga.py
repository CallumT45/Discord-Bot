import io
import requests
from PIL import Image
from urllib.request import Request, urlopen
import bs4


class MangaDL():

    def get_URL(self, manga, chapter, page):
        URL = "http://www.mangareader.net"
        url = URL + '/' + manga + '/' + chapter + '/' + page
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        myimgs = soup.findAll("img")
        myimgs = [img for img in myimgs if img.has_attr(
            'alt') and "Page" in img['alt']]
        return 'https:' + myimgs[0]['src']

    def get_img(self, imgURL):
        req = Request(imgURL, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        im = io.BytesIO(webpage)
        img = Image.open(im)
        try:
            rgb = Image.new('RGB', img.size, (255, 255, 255))
            rgb.paste(img, mask=img.split()[3])
            return rgb
        except:
            return img
