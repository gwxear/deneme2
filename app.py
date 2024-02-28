from flask import Flask, render_template, request, redirect, url_for
import requests
import re

app = Flask(__name__)

def add_http_prefix(url):
    if not re.match(r'https?://', url):
        return 'http://' + url
    return url

def seo_analysis(url):
    result = {
        'url': url,
        'title': None,
        'meta_description': None,
        'image_alt_texts': None,
        'h1_headings': None,
        'robots_txt': None
    }

    try:
        url = add_http_prefix(url)  # http:// eklenmiş URL'i kullan
        response = requests.get(url)

        # Title
        if '<title>' in response.text:
            title_start_index = response.text.find('<title>') + len('<title>')
            title_end_index = response.text.find('</title>')
            result['title'] = response.text[title_start_index:title_end_index].strip()[:60]
            result['title_check'] = '✅' if len(result['title']) <= 60 else '❌'

        # Meta Description
        meta_description_pattern = re.compile(r'<meta\s+name\s*=\s*["\']description["\']\s+content\s*=\s*["\'](.+?)["\']\s*/?>', re.IGNORECASE)
        match = meta_description_pattern.search(response.text)
        if match:
            result['meta_description'] = match.group(1)[:150]
            result['meta_description_check'] = '✅' if len(result['meta_description']) <= 150 else '❌'

        # Image Alt Texts
        image_alt_texts_pattern = re.compile(r'<img[^>]*alt\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
        image_alt_texts = image_alt_texts_pattern.findall(response.text)
        result['image_alt_texts'] = image_alt_texts if image_alt_texts else ['No Image Alt Texts Found']
        result['image_alt_texts_check'] = '✅' if image_alt_texts else '❌'

        # H1 Headings
        h1_headings_pattern = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE)
        h1_headings = h1_headings_pattern.findall(response.text)
        h1_headings = [' '.join(heading.strip().split())[:100] for heading in h1_headings if heading.strip()]
        result['h1_headings'] = h1_headings if h1_headings else ['No H1 Headings Found']
        result['h1_headings_check'] = '✅' if h1_headings else '❌'

        # Robots.txt
        robots_txt_url = url.rstrip('/') + '/robots.txt'
        robots_response = requests.get(robots_txt_url)
        result['robots_txt'] = robots_response.text if robots_response.status_code == 200 else 'Not Found'
        result['robots_txt_check'] = '✅' if robots_response.status_code == 200 else '❌'

    except Exception as e:
        result['error'] = str(e)

    return result

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('analyze', url=url))
    return render_template('seo.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        url = request.form['url']
        return redirect(url_for('analyze', url=url))
    
    url = request.args.get('url', '')
    result = seo_analysis(url)
    return render_template('seo.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
