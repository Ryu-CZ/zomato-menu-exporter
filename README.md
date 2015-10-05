# Zomato menu exporter
This python script exports online menu of your favorite restaurant on www.zomato.com into PDF.

### Version
1.0.2

### Installation
```{r, engine='bash'}
pip install -r requirements.txt
```

### Usage
Run this script in terminal where you can provide optional parameters:
```{r, engine='bash'}
python menuParser.py <url> <pdfOutputFile>  
```
Default parameters values:
  - url = 'https://www.zomato.com/cs/brno/colatransport-turany-brno-jih/menu'
  - outFile = './menu_%s.pdf'%(dt.datetime.now().date().isoformat())

License
----
GNU General Public License v2.0
