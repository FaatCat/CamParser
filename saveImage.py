from StringIO import StringIO
import requests
from PIL import Image
from bs4 import BeautifulSoup

DCS_IP = "192.168.0.9"
userauth = ('admin', 'Chaos123')

imgurl = "http://"+DCS_IP+"/image/jpeg.cgi"
img = requests.get(imgurl, auth=userauth)
i = Image.open(StringIO(img.content))
i.save("snapshot.png")