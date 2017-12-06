from flask import Flask, render_template, url_for, jsonify, request as r, g, send_from_directory
from requests import session
import re
import time
import os
app = Flask(__name__)

orderMap = {1 : "21", 2 : "21", 3 : "17", 4 : "17", 5 : "16", 6 : "14", 7 : "16", 8 : "18", 9 : "20",
            10 : "17", 11 : "17", 12 : "17", 13 : "19", 14 : "15", 15 : "19", 16 : "16", 17 : "17",
            18 : "19", 19 : "17", 20 : "20"}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

# app.add_url_rule('/favicon.ico',
#                  redirect_to=url_for('static', filename='img/favicon.ico'))

@app.before_request
def before_request():
    if r.endpoint == 'root' or r.endpoint == 'static' or r.endpoint == 'help' or r.endpoint == 'favicon':
        pass
    else:
        g.cookies = getCookies(r.form.get('cstring'))


@app.route('/')
def root():
    return render_template('main.html', name='keduRight', js=url_for('static', filename='js/v.js'))


@app.route('/help')
def help():
    return render_template('help.html', title='도움!', img1=url_for('static', filename='img/capcha.JPG'),
                           img2=url_for('static', filename='img/console.png'),
                           img3=url_for('static', filename='img/cookie.JPG'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/getID', methods=['POST'])
def getID():
    c = g.cookies
    print(c)
    pid = '' # users pid

    with session() as s:
        res = s.post('http://keducenter.co.kr/lms/class/student/page.php?p=cl_lecture', headers=headers, cookies=c)
        pid = re.compile('p_id=([\w\d]+)&').search(res.text).groups()[0]
        # res = s.post(makeCursor(pid), cookies=c)  # cursor setting
        # res = s.post('http://keducenter.co.kr/lms/plugin/player/player.php?wr_page=1', cookies=c)
    return jsonify(pid=pid)

@app.route('/process', methods=['POST'])
def process():
    c = g.cookies
    pid = r.form.get('pid')
    order = r.form.get('order')
    pages = orderMap.get(int(order))
    cursor = makeCursor(pid, order)

    wrid = '' # personal id per order

    with session() as s:
        res = s.post(cursor, headers=headers, cookies=c) # ping order cursor
        res = s.post('http://keducenter.co.kr/lms/plugin/player/player.php?wr_page=1', headers=headers, cookies=c)
        wrid = re.compile('"wr_id" value="([\w\d]+)"').search(res.text).groups()[0]

        urls = getProcessUrl(pid, order, pages, wrid)  # get all pages in this order

        reslist = list()
        for u in urls: # first update
            reslist.append(s.post(u, headers=headers, cookies=c))
            time.sleep(0.1)

        post(s, reslist, 3, c)

        # for k, v in orderMap.items():
        #     s.post(makeCursor(pid, k), headers=headers, cookies=c) # new order cursor setting
        #     urls = getProcessUrl(pid, k, v, wrid) # get all pages in this order
        #     reslist = [s.post(u, headers=headers, cookies=c) for u in urls] # first update, can be {"result":"studied"} or {"result":"1"}
        #     done = [s.post(u.url, headers=headers, cookies=c) for u in reslist if 'studied' not in u.text] # if return {"result":"1"}, second update.
        #
        #     [print(d) for d in done]
    return jsonify(order=order)



def makeCursor(pid, order=1):
    cursor = 'http://keducenter.co.kr/lms/plugin/player/index.php?p_id='+ pid +'&s_id=aaaa&wr_order='+ str(order) +'&wr_page=1'
    return cursor


def getProcessUrl(pid, order, page, wrid):
    url = list()
    for p in range(int(page)):
        url.append('http://keducenter.co.kr/lms/plugin/player/update.php?p_id='+pid+'&s_id=aaaa&wr_order='+str(order)+'&wr_page='+str(p+1)+'&wr_id='+wrid+'&_='+str(int(time.time())))
    return url


def getCookies(cstring):
    cstring = cstring.replace('\"', '').replace(' ', '').split(';')
    return dict([x.split('=') for x in cstring])


def post(s, reslist, times, c):
    if times < 1:
        return False

    res2 = list()
    for u in reslist:
        if 'studied' not in u.text:
            res2.append(s.post(u.url, headers=headers, cookies=c))
            time.sleep(0.1)

    return post(s, res2, times-1, c)


if __name__ == '__main__':
    app.run(debug=True)