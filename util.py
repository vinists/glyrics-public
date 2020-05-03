import requests
from bs4 import BeautifulSoup
from unicodedata import normalize
from string import digits, ascii_uppercase
from random import choice




def rndstring(size=6, chars=ascii_uppercase + digits):
        return ''.join(choice(chars) for _ in range(size))



# Composer is going to return in a tuple the lyrics, url(genius.com) and the title

class composer:
    def __init__(self, artist, song):
        self.artist = artist
        self.song = song

    

    def asciifix(self, word):
            return normalize("NFD", word).encode("ascii", "ignore").decode("utf-8")

    def charRemover(self, name):
        for char in ["'", "?", "!", ".", ",", "’", "(", ")", ":", "&", "/"]:
            if(char in name):
                if(char == "&"):
                    name = name.replace(name[name.index(char)], "and")
                if(char == "/"):
                    name = name.replace(name[name.index(char)], "-")
                try:
                    name = name.replace(name[name.index(char)], "")
                except Exception:
                    print("Exception at charRemover")
                    continue
        if("  " in name):
            return self.asciifix(name.replace("  ", " "))
        else:
            return self.asciifix(name)


    def nameChecker(self, name, type):
        val = [pos for pos, char in enumerate(name) if char == '-']
        if(type == 'url'):
            if val:
                for let in val:
                    if(name[let+1] == ' ' and name[let-1] == ' '):
                        return self.charRemover(name[:let-1].lower().replace(' ', '-'))
                    else:
                        return self.charRemover(name.lower().replace(' ', '-'))
            else:
                return self.charRemover(name.lower().replace(' ', '-'))
        elif(type == 'text'):
            if val:
                for let in val:
                    if(name[let+1] == ' ' and name[let-1] == ' '):
                        return name[:let-1]
                    else:
                        return name
            else:
                return name


    def geniusGrab(self, artist, song):
        try:
            url = f'https://genius.com/{artist}-{song}-lyrics'
            request = requests.get(url)
            
            if request.status_code != 404:
                soup = BeautifulSoup(request.text, 'lxml').find('div', class_='lyrics').get_text()
                return soup.replace('\n', '<br>'), url
            
            else:
                return None
        except requests.exceptions.RequestException:
            pass
    
    def returner(self):
        return self.geniusGrab(self.nameChecker(self.artist, 'url'),
                    self.nameChecker(self.song, 'url')), f"{self.nameChecker(self.song, 'text')} - {self.artist}"


