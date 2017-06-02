import re

'''
Convert web addresses into anchors

http://google.com to <a href='http://google.com'>google.com</a>
'''
class Linkify:

    _urlfinderregex = re.compile(r'http([^\.\s]+\.[^\.\s]*)+[^\.\s]{2,}')

    result = ''

    def __init__(self, text, maxLinkLength=500):
        if text != None and text != '':
            self.maxLinkLength = maxLinkLength
            self.result = self._urlfinderregex.sub(self.replaceWithLink, text)

    def replaceWithLink(self, matchobj):
        url = matchobj.group(0)
        text = str(url)

        '''
        if text.startswith('http://'):
            text = text.replace('http://', '', 1)
        elif text.startswith('https://'):
            text = text.replace('https://', '', 1)
        '''

        if text.startswith('www.'):
            text = text.replace('www.', '', 1)

        if len(text) > self.maxLinkLength:
            halflength = self.maxLinkLength / 2
            text = text[0:halflength] + '...' + text[len(text) - halflength:]

        return '<a href="' + url + '" target="_blank" rel="nofollow">' + text + '</a>'

    def getResult(self):
        return self.result
