from flask import Flask, render_template_string, request
import requests
import xml.etree.ElementTree as ET
import feedparser
from datetime import date, timedelta

app = Flask(__name__)

KEYWORDS = ['entrepreneurship', 'innovation', 'incubator', 'accelerator']
DAYS_BACK = 14
COUNTRY_CODE = 'IE'
BASE_URL = 'https://ted.europa.eu/TED/rss/Export.do'

HTML_TEMPLATE = """
<!doctype html>
<title>TED Tender Scraper</title>
<h2>Irish Tenders Search (TED)</h2>
<form method="post">
  <button type="submit">Search TED for Keywords</button>
</form>
{% if results %}
  <h3>Results</h3>
  {% for keyword, entries in results.items() %}
    <h4>Keyword: {{ keyword }}</h4>
    {% if entries %}
      <ul>
      {% for entry in entries %}
        <li><strong>{{ entry['title'] }}</strong><br>
        📅 {{ entry['published'] }}<br>
        🔗 <a href="{{ entry['link'] }}" target="_blank">View Notice</a><br>
        📝 {{ entry['summary'][:300] }}...</li>
      {% endfor %}
      </ul>
    {% else %}
      <p>No results found.</p>
    {% endif %}
  {% endfor %}
{% endif %}
"""

def search_ted_for_keyword(keyword):
    start_date = date.today() - timedelta(days=DAYS_BACK)
    end_date = date.today()
    params = {
        'action': 'search',
        'locale': 'en',
        'Country': COUNTRY_CODE,
        'Keyword': keyword,
        'StartDate': start_date.strftime('%d-%m-%Y'),
        'EndDate': end_date.strftime('%d-%m-%Y'),
        'Type_Contract': 'Works,Supplies,Services',
        'TEDLang': 'EN',
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.content

def parse_feed(feed_data):
    parsed = feedparser.parse(feed_data)
    entries = []

    for entry in parsed.entries:
        entries.append({
            'title': entry.title,
            'link': entry.link,
            'summary': entry.summary,
            'published': entry.published
        })

    return entries

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        for keyword in KEYWORDS:
            try:
                feed = search_ted_for_keyword(keyword)
                entries = parse_feed(feed)
                results[keyword] = entries
            except Exception as e:
                results[keyword] = [{
                    'title': 'Error',
                    'summary': str(e),
                    'link': '#',
                    'published': ''
                }]
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
