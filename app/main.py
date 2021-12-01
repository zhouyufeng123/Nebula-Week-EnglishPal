#! /usr/bin/python3
# -*- coding: utf-8 -*-

###########################################################################
# Copyright 2019 (C) Hui Lan <hui.lan@cantab.net>
# Written permission must be obtained from the author for commercial uses.
###########################################################################
import pickle
import re

from WordFreq import WordFreq
from app.login import login_blue
from app.service import get_random_ads
from app.user import user_blue
from wordfreqCMD import youdao_link, sort_in_descending_order
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea, pickle_idea2
import os
import random, glob
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, abort, flash, get_flashed_messages
from difficulty import get_difficulty_level, text_difficulty_level, user_difficulty_level

app = Flask(__name__)
app.secret_key = 'lunch.time!'

path_prefix = 'D:/pycharm/englishpal/app/'
path_prefix = './'  # comment this line in deployment


def get_random_image(path):
    img_path = random.choice(glob.glob(os.path.join(path, '*.jpg')))
    return img_path[img_path.rfind('/static'):]


def total_number_of_essays():
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM article")
    rq.do()
    result = rq.get_results()
    return len(result)


def load_freq_history(path):
    d = {}
    if os.path.exists(path):
        # print('12323path exist! path is '+path)
        d = pickle_idea.load_record(path)
    return d

def within_range(x, y, r):
    return x > y and abs(x - y) <= r


def get_article_title(s):
    return s.split('\n')[0]


def get_article_body(s):
    lst = s.split('\n')
    lst.pop(0)  # remove the first line
    return '\n'.join(lst)


def get_today_article(user_word_list, articleID):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    if articleID == None:
        rq.instructions("SELECT * FROM article")
    else:
        rq.instructions('SELECT * FROM article WHERE article_id=%d' % (articleID))
    rq.do()
    result = rq.get_results()
    random.shuffle(result)

    # Choose article according to reader's level
    d1 = load_freq_history(path_prefix + 'static/frequency/frequency.p')
    d2 = load_freq_history(path_prefix + 'static/words_and_tests.p')
    d3 = get_difficulty_level(d1, d2)

    d = {}
    d_user = load_freq_history(user_word_list)
    # print("d_user"+str(d_user))
    user_level = user_difficulty_level(d_user,d3)  # more consideration as user's behaviour is dynamic. Time factor should be considered.
    random.shuffle(result)  # shuffle list
    d = random.choice(result)
    text_level = text_difficulty_level(d['text'], d3)
    if articleID == None:
        for reading in result:
            text_level = text_difficulty_level(reading['text'], d3)
            factor = random.gauss(0.8,
                                  0.1)  # a number drawn from Gaussian distribution with a mean of 0.8 and a stand deviation of 1
            if within_range(text_level, user_level, (8.0 - user_level) * factor):
                d = reading
                break

    s = '<div class="alert alert-success" role="alert">According to your word list, your level is <span class="badge bg-success">%4.2f</span>  and we have chosen an article with a difficulty level of <span class="badge bg-success">%4.2f</span> for you.</div>' % (
        user_level, text_level)
    s += '<p class="text-muted">Article added on: %s</p>' % (d['date'])
    s += '<div class="p-3 mb-2 bg-light text-dark">'
    article_title = get_article_title(d['text'])
    article_body = get_article_body(d['text'])
    s += '<p class="display-3">%s</p>' % (article_title)
    with open('static/frequency/frequency_%s.pickle' % session['username'], 'rb') as f:
        data = pickle.load(f)
        words = []
        for key in data.keys():
            words.append(key)  # 读取pickle中生词库，并存入words列表
    article = article_body
    lst = re.split('(\W+)', article)  # 将文章正文分割成一块块单词及符号
    for i in words:
        for j in lst:
            if i == j:
                lst = lst[0:lst.index(j) - 1] + ['<mark> ', j, '</mark>'] \
                      + lst[lst.index(j) + 2:]  # 当生词与文章词语相同时，在词汇前后加入高亮符号，并保证列表其他部分不变
    ls2 = [str(i) for i in lst]  # 将列表中的数字转换成字符串
    article = ' '.join(ls2)  # 列表拼接成字符串
    article1 = article.replace('\n', '<br/>')
    s += '<p class="lead">%s</p>' % article1
    s += '<p><small class="text-muted">%s</small></p>' % (d['source'])
    s += '<p><b>%s</b></p>' % (get_question_part(d['question']))
    s = s.replace('\n', '<br/>')
    s += '%s' % (get_answer_part(d['question']))
    s += '</div>'
    session['articleID'] = d['article_id']
    return s





def get_time():
    return datetime.now().strftime('%Y%m%d%H%M')  # upper to minutes


def get_question_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'QUESTION':
            result.append(line)
            flag = 1
        elif line == 'ANSWER':
            flag = 0
        elif flag == 1:
            result.append(line)
    return '\n'.join(result)


def get_answer_part(s):
    s = s.strip()
    result = []
    flag = 0
    for line in s.split('\n'):
        line = line.strip()
        if line == 'ANSWER':
            flag = 1
        elif flag == 1:
            result.append(line)
    # https://css-tricks.com/snippets/javascript/showhide-element/
    js = '''
<script type="text/javascript">

    function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }
</script>   
    '''
    html_code = js
    html_code += '\n'
    html_code += '<button onclick="toggle_visibility(\'answer\');">ANSWER</button>\n'
    html_code += '<div id="answer" style="display:none;">%s</div>\n' % ('\n'.join(result))
    return html_code


def get_flashed_messages_if_any():
    messages = get_flashed_messages()
    s = ''
    for message in messages:
        s += '<div class="alert alert-warning" role="alert">'
        s += f'Congratulations! {message}'
        s += '</div>'
    return s


# @app.route("/<username>/reset", methods=['GET', 'POST'])
# def user_reset(username):
#     if request.method == 'GET':
#         session['articleID'] = None
#         return redirect(url_for('userpage', username=username))
#     else:
#         return 'Under construction'


@app.route("/mark", methods=['GET', 'POST'])
def mark_word():
    if request.method == 'POST':
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, 1))
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')
        return redirect(url_for('mainpage'))
    else:
        return 'Under construction'


@app.route("/", methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()
        # save history 
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency/frequency.p')
        return render_template('mainpost.html', lst=lst)

    elif request.method == 'GET':  # when we load a html page
        random_ads = get_random_ads()
        number_of_essays = total_number_of_essays()
        d = load_freq_history(path_prefix + 'static/frequency/frequency.p')
        d_len = len(d)
        lst = sort_in_descending_order(pickle_idea.dict2lst(d))
        return render_template('mainget.html', random_ads=random_ads, number_of_essays=number_of_essays, d_len=d_len, lst=lst)





@app.route("/<username>/<word>/unfamiliar", methods=['GET', 'POST'])
def unfamiliar(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.unfamiliar(user_freq_record, word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('user.userpage', username=username))


@app.route("/<username>/<word>/familiar", methods=['GET', 'POST'])
def familiar(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea.familiar(user_freq_record, word)
    session['thisWord'] = word  # 1. put a word into session
    session['time'] = 1
    return redirect(url_for('user.userpage', username=username))


@app.route("/<username>/<word>/del", methods=['GET', 'POST'])
def deleteword(username, word):
    user_freq_record = path_prefix + 'static/frequency/' + 'frequency_%s.pickle' % (username)
    pickle_idea2.deleteRecord(user_freq_record, word)
    flash(f'<strong>{word}</strong> is no longer in your word list.')
    return redirect(url_for('user.userpage', username=username))


app.register_blueprint(login_blue)
app.register_blueprint(user_blue)

if __name__ == '__main__':
    app.run(debug=True)