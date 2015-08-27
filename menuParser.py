# -*- coding: utf8 -*-

__author__ = 'ryu_cz'
__version__ = '1.0.0'

from HTMLParser import HTMLParser
import re
import urllib2
import cookielib
import codecs

import codecs
import sys
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, CellStyle
from reportlab.lib.styles import *#getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus.flowables import Spacer

from reportlab.lib.colors import white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.fonts import tt2ps
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont  
pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
_baseFontName='Verdana'
_baseFontNameB = tt2ps(_baseFontName,1,0)
_baseFontNameI = tt2ps(_baseFontName,0,1)
_baseFontNameBI = tt2ps(_baseFontName,1,1)

def getMenuStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName=_baseFontName,
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='BodyText',
                                  parent=stylesheet['Normal'],
                                  spaceBefore=6)
                   )
    stylesheet.add(ParagraphStyle(name='Italic',
                                  parent=stylesheet['BodyText'],
                                  fontName = _baseFontNameI)
                   )

    stylesheet.add(ParagraphStyle(name='Heading1',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  spaceAfter=6),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  alignment=TA_CENTER,
                                  spaceAfter=6),
                   alias='title')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=14,
                                  leading=18,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h2')

    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=12,
                                  leading=14,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Heading4',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=10,
                                  leading=12,
                                  spaceBefore=10,
                                  spaceAfter=4),
                   alias='h4')

    stylesheet.add(ParagraphStyle(name='Heading5',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=9,
                                  leading=10.8,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h5')

    stylesheet.add(ParagraphStyle(name='Heading6',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=7,
                                  leading=8.4,
                                  spaceBefore=6,
                                  spaceAfter=2),
                   alias='h6')

    stylesheet.add(ParagraphStyle(name='Bullet',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  spaceBefore=3),
                   alias='bu')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceBefore=6,
                                  bulletFontName=_baseFontNameBI),
                   alias='df')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leading=8.8,
                                  firstLineIndent=0,
                                  leftIndent=36))

    return stylesheet


styleSheet = getMenuStyleSheet()


class DataProvider():
    def getData(self):
        '''
        Retuns list of one row data
        '''
        return []


class StyleProvider():    
    def getStyle(self, row):
        '''
        Returns list of style setting options
        @param row: row index
        @type row:
        '''
        return []


class Food(StyleProvider, DataProvider):
    '''
    Represents one menu item with price
    '''
    def __init__(self, description=None):
        self.description = unicode(description)
        self.price = ''
    
    def string(self, *args, **kwargs):
        return unicode('%s\t%s'%(unicode(self.description), unicode(self.price)))

    @classmethod
    def toCell(cls, txt):
        return Paragraph(txt,style=styleSheet["Normal"])

    def getData(self):
        ret = DataProvider.getData(self)
        ret.append(Food.toCell(self.description))
        ret.append(self.price)
        return ret
    
    def getStyle(self, row):
        ret = StyleProvider.getStyle(self, row)
        ret.append( ('ALIGN',(0,row),(0,row),'LEFT') )
        ret.append( ('ALIGN',(1,row),(1,row),'RIGHT') )
        ret.append( ('FONTNAME', (0,row), (-1,row), styleSheet['Normal'].fontName) )
        ret.append( ('FONTSIZE', (0,row), (-1,row), styleSheet['Normal'].fontSize) )
        return ret
        
class Day(StyleProvider, DataProvider):
    '''
    Represents one day of week menu
    '''
    def __init__(self, name=None):
        self.name = name
        self.soup = None
        self.foodList = []
        self.padding = ''
        
    def addFood(self, description):
        self.foodList.append(Food(description=description))
        
    def append(self, value='', tag=None):
        '''
        Adds one element into week menu
        @param value: value of elemwnt (tmi-group-name, tmi-name, tmi-price) unknown tags are passed into padding
        @param tag: tag of element
        '''
        if tag=='tmi-group-name':
            self.name = value
        elif tag=='tmi-name':
            if self.soup is None:
                self.soup = value
            else:
                self.addFood(description=value)
        elif tag=='tmi-price' and len(self.foodList)>0:
            self.foodList[-1].price = value
        else:
            self.padding += value
            
    def getData(self):
        ret = [[Paragraph('''<para align=left>%s</para>'''%self.name, styleSheet["Heading2"])], 
               [self.soup]]
        for i in range(len(self.foodList)):
            ret.append(self.foodList[i].getData())
        return ret
    
    def getStyle(self, row=0):
        ret = [('ALIGN',(0, 0),(-1, 0),'LEFT'),
               ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
               ('ALIGN',(0, 1),(-1, 1),'LEFT'),
               ('FONTNAME', (0,1), (-1,1), styleSheet['Normal'].fontName),
               ('FONTSIZE', (0,1), (-1,1), styleSheet['Normal'].fontSize)
               ]
        for i in range(len(self.foodList)):
            ret.extend(self.foodList[i].getStyle(row=2+i))
        return ret
    
    def string(self):
        fl = [f.string() for f in self.foodList]
        return unicode(u'%s:\nPolévka: %s%s'%(self.name, self.soup, '\n'.join(fl)))
    

# create a subclass and override the handler methods
class ColaParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.schedule = []
        self.tag = []

    def handle_starttag(self, tag, attributes):
        if tag != 'div':
            return
        if self.recording:
            self.recording += 1
        for name, value in attributes:
            if name == u'class':
                if value == u'tmi-groups':
                    if self.recording < 1:
                        self.recording = 1
                elif value == u'tmi-group-name':
                    self.schedule.append(Day())
            if self.recording:
                self.tag.append(value)


    def handle_endtag(self, tag):
        if tag == 'div' and self.recording:
            if len(self.tag):
                self.tag.pop()
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            elem = re.sub(r'\s+', ' ', data).lstrip().rstrip()
            if len(self.schedule)>0 and elem != u' ':
                self.schedule[-1].append(value=elem, tag=self.tag[-1])


class Menu(DataProvider):

    def __init__(self, title='Cola Transport'):
        self.rawData = None
        self.days = None
        self.title = title
        self.pageSize = A4
        self.tableColWidths = (17.5*cm, 1.5*cm)
        
    def gatherSrc(self, URL):
        # get menu pages text
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        request = urllib2.Request(URL)
        print("... Sending HTTP GET to %s" % URL)
        f = opener.open(request)
        encoding = f.headers.getparam('charset')
        txt = f.read().decode(encoding)
        f.close()
        opener.close()
        self.rawData = txt
        return self.rawData
    
    def parse(self, rawData=None): 
        if rawData is None:
            rawData = self.rawData
        parser = ColaParser()  
        parser.feed(rawData)
        self.days = parser.schedule
        return self.days
    
    def _prepareTitle(self):
        return Table(data=[[Paragraph('''<font color=white>%s</font>'''%self.title, styleSheet["Title"])]],
                     colWidths=sum(self.tableColWidths),
                     style=[('ALIGN',(0, 0),(-1, 0),'LEFT'),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkslateblue)]
                     )
    
    def getData(self):
        elements = []
        elements.append(self._prepareTitle())
        for i in range(len(self.days)):
            elements.append(Spacer(width=sum(self.tableColWidths), 
                                height=0.4*cm))
            elements.append(Table(self.days[i].getData(),
                               style=self.days[i].getStyle(),
                               colWidths=self.tableColWidths
                               )
                         )
        return elements
    
    def string(self):
        daysList = [ day.string() for day in self.days]
        return '%s\n%s'%(self.title, unicode('\n'.join(daysList)))


def parseParams():
    '''
    Returns tuple (url address, output file path)
    '''
    import sys, getopt, datetime as dt
    # Store input and output file names
    url = 'https://www.zomato.com/cs/brno/colatransport-turany-brno-jih/menu'
    outFile = './menu_%s.pdf'%(dt.datetime.now().date().isoformat())
     
    # Read command line args
    if len(sys.argv)>1:
        url = sys.argv[1]
    if len(sys.argv)>2:
        url = sys.argv[2]
#     myopts, args = getopt.getopt(sys.argv[1:],"i:o:")
#      
#     ###############################
#     # o == option
#     # a == argument passed to the o
#     ###############################
#     for o, a in myopts:
#         if o == '-i':
#             url=a
#         elif o == '-o':
#             outFile=a
#         else:
#             print("Usage: %s -i input -o output" % sys.argv[0])
    return url, outFile

def toPDF(menu, outFile):
    print("... Creating PDF %s"%outFile)
    doc = SimpleDocTemplate(outFile, 
                            pagesize=menu.pageSize, 
                            leftMargin=inch*0.25,
                            rightMargin=inch*0.25, 
                            bottomMargin=inch*0.25, 
                            topMargin=inch*0.25)
    doc.build(menu.getData())
    return

def main():
    URL, outFile = parseParams()
    colaMenu = Menu()
    colaMenu.gatherSrc(URL)
    colaMenu.parse()
    print colaMenu.string()
    toPDF(colaMenu, outFile)
    
if __name__ == "__main__":
    main()
    