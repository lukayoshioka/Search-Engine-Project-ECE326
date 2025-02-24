import httplib2 
from beaker.middleware import SessionMiddleware
from bottle import app, route, redirect, run, post, error, static_file, request, template
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import sqlite3 as lite
from collections import defaultdict
import re
import difflib


#create global history dict
history = {}
session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}
app = SessionMiddleware(app(), session_opts)
curr_search = ""
page_number = 0

ID = "830509265504-iumkrjkloq5dgg6r7f43joqkoeqki5nj.apps.googleusercontent.com"
SECRET = "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"

mydb = lite.connect("database.db")
mycursor = mydb.cursor()



@route('/auth', method='GET')
def home():
    flow = flow_from_clientsecrets("client_secret.json", 
                                   scope='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
                                   redirect_uri='http://44.207.84.117.nip.io:8080/redirect')
    uri = flow.step1_get_authorize_url()
    redirect(str(uri))

@route('/redirect')
def redirect_page():
    code = request.query.get("code", "")
    scope = ['profile', 'email']
    flow = OAuth2WebServerFlow(ID, SECRET, scope=scope,
    redirect_uri="http://44.207.84.117.nip.io:8080/redirect")
    credentials = flow.step2_exchange(code)
    token = credentials.id_token["sub"]
    http = httplib2.Http()
    http = credentials.authorize(http)
    # Get user email
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']
    session = request.environ.get('beaker.session')
    session['email'] = user_email
    session['picture'] = user_document['picture']
    session['name'] = user_document['name']
    session.save()
    redirect('/')

@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session.delete()
    redirect('/')
#set up route for assets
@route('/static/assets/<filename>')
def static(filename):
    return static_file(filename, root='./views/static/assets')

#set up route to css folder in static
@route('/static/css/<filename>')
def static(filename):
    return static_file(filename, root='./views/static/css')

#Query Page
@route('/')
def front():
    session = request.environ.get('beaker.session')
    email = ""
    picture = ""
    name = ""
    if 'email' in session:
        email = session['email']
    if 'picture' in session:
        picture = session['picture']
    if 'name' in session:
        name = session['name']
    #sort history in descending order and limit to top 20 searched words
    user_history = {}
    if email in history:
        user_history = history[email]

    history_sorted = dict(sorted(user_history.items(), key=lambda item: item[1], reverse=True))
    out = {i: history_sorted[i] for i in list(history_sorted)[:20]}

    #display query+history page
    return template('query', history = out, email=email, picture=picture, name=name)

#when search bar is pressed
@post('/')
def input():
    # url = request.query.get('url', '')
    # print(url)
    add_to_history = True
    global page_number, curr_search
    #grab words from the search
    session = request.environ.get('beaker.session')
    search_result = request.forms.get('keywords')
    if search_result != "":
        page_number = 0
        curr_search = search_result
    else:
        page_number+=1
        search_result = curr_search
        add_to_history = False

    #update history with words and lower case the words in case the user submits mulitple of the same word with different capitalization
    global history
    user_history = {}
    if 'email' in session:
        if session['email'] not in history:
            history[session['email']] = user_history
        else:
            user_history = history[session['email']]
    words = search_result.split()
    for word in words:
        word = word.lower()
    #create a list from the dict of only the words
    words_unique = dict.fromkeys(words)
    for word in words_unique:
        words_unique[word] = words.count(word)
        #if word is already in history update by the number of times the words appears in this search if not set number to the number of times the word appears in this search
        if add_to_history:
            if word in user_history:
                user_history[word] += words_unique[word]
            else:
                user_history[word] = words_unique[word]

    #get urls and pageranks
    mycursor.execute("SELECT URL, PAGERANKS.RANK FROM PAGERANKS INNER JOIN DOCUMENTS ON DOCUMENTS.DOC_ID = PAGERANKS.DOC_ID;")
    search = mycursor.fetchall()

    #spell check for multiword search
    #create dicts containing all single element and 2 element removals
    copies = defaultdict(list)
    for word in words:
        for i in range(len(word)):
            check = word[:i] + word[i + 1:]
            if check not in copies[word]:
                copies[word].append(word[:i] + word[i + 1:])
        if len(word) > 4 and len(word) < 10:
            for copy in copies[word]:
                for i in range(len(copy)):
                    check = copy[:i] + copy[i + 1:]
                    if check not in copies[word]:
                        copies[word].append(check)


    #Spell check algorithm runs difflib.SequenceMatcher to get word similarity any direct matches are given a score of 1
    #and any urls with a score of over 0.5 are added to the scores dict
    scores = {}
    results = [result for result in search]
    for word in words:
        regex = re.compile('[^a-zA-Z]')
        for result in results:
            fixed_url = regex.sub(',', result[0])
            if len(fixed_url) > len(word):
                url_words = list(filter(None, fixed_url.split(',')))
                for url_word in url_words:
                    similarity = max([difflib.SequenceMatcher(None, x, url_word).ratio() for x in copies])
                    if word == url_word:
                        if result[0] not in scores:
                            scores[result[0]] = 1 + result[1]
                        if result[0] in scores:
                            scores[result[0]] += 1
                    elif similarity > 0.5:
                        if result[0] not in scores:
                            scores[result[0]] = similarity + result[1]
                        if result[0] in scores:
                            scores[result[0]] += similarity
    

    #sorting in descending order to get the max scores
    urls = sorted(scores, key=scores.get, reverse=True)

    #if not matches are found simply return a list of url by descending pageranks
    if scores == {}:
        urls = [result for result in search]
        urls.sort(key=lambda tup: tup[1], reverse = True)

    if page_number < 0 or page_number > (len(urls)/5):
        page_number = 0
    #limit the number of elements to 5 or less if there aren't 5 elements
    x = 5
    if page_number*5 + 5 > len(urls):
        x = len(urls)-(page_number*5)


    return template('results', curr_search=curr_search, results = words_unique, urls = [x for x in urls[page_number*5:page_number*5+x]], page = page_number, query=search_result)

@error(404)
def error():
    return """
        <h1>ERROR404: Page not Found</h1>
        <p>Please return to <a href="/">home page</a>
    """

#test cases for backend of the lab
@route('/test')
def index():
    return template('test')
@route('/test2')
def index():
    return template('test2')
run(app=app, host='0.0.0.0', port=8080)


