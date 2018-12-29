#!/usr/bin/env python

from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import MultipleResultsFound

from model import Category, Item, User

from flask import Flask, jsonify, request, url_for, render_template
from flask import flash, redirect
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///categoryapp.db')
Base = declarative_base()
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine, autocommit=False)
session = scoped_session(DBSession)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# max number of items displayed in the homepage
ITEM_LIMIT = 20


@app.route('/login')
def showLogin():
    """Display login page."""

    # create state token and save in login_session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Logs the user in using Google authentication credentials."""

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    # Upgrade the authorization code into a credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already logged in.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user = session.query(User).filter_by(email=(data["email"])).one_or_none()
    if user is None:
        user = User(name=data['name'], email=data['email'],
                    picture=data['picture'])
        session.add(user)
        session.commit()
        user = session.query(User).filter_by(
            email=login_session['email']).one_or_none()
    login_session['user_id'] = user.id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px; " '
    output += ' "border-radius: 150px;-webkit-border-radius: 150px;"'
    output += ' "-moz-border-radius: 150px;"> '
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Logs out the user."""

    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        flash('Current user not connected.')
        # make sure login_session is cleared
        if 'gplus_id' in login_session:
            del login_session['gplus_id']
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        return redirect(url_for('getCatalog'))

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash('User Successfully logged out.')
        return redirect(url_for('getCatalog'))
    else:
        flash('Failed to revoke token for given user.')
        return redirect(url_for('getCatalog'))


@app.route('/api/catalog/JSON')
def catalogJSON():
    """JSOn API endpoint for getting catalog (GET request)."""

    catalog = session.query(Category).order_by("name").all()
    return jsonify(Catalog=[c.serialize for c in catalog])


@app.route('/api/catalog/category/<string:category_name>/JSON')
def categoryJSON(category_name):
    """JSOn API endpoint for getting items under a category (GET request)"""

    category = session.query(Category).filter(
        func.lower(Category.name) == func.lower(category_name)).one_or_none()
    if category is not None:
        return jsonify(Category=category.serialize)
    return jsonify()


@app.route('/api/catalog/item/<string:item_name>/JSON')
def itemsJSON(item_name):
    """JSOn API endpoint for getting items under a category (GET request)"""

    item = session.query(Item).filter(
        func.lower(Item.name) == func.lower(item_name)).one_or_none()
    if item is not None:
        return jsonify(Item=item.serialize)
    return jsonify()


@app.route('/')
@app.route('/catalog', methods=['GET'])
def getCatalog():
    """Load the main catalog page.

    Displays all categories with latest added items(across categories)."""

    categories = session.query(Category).order_by("name")
    items = session.query(Item).order_by(Item.id.desc()).limit(ITEM_LIMIT)
    user_loggedin = 'username' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('catalog.html', categories=categories,
                               items=items, user_loggedin=user_loggedin,
                               user_name=user_name, picture=picture)
    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog/<string:category_name>', methods=['GET'])
def getCategory(category_name):
    """Load the catalog page.

    Displays all categories and all items for the selected category."""

    categories = session.query(Category).order_by("name")
    items = session.query(Item).filter(
        func.lower(Item.category_name) == func.lower(category_name)).order_by(
            Item.name).all()
    user_loggedin = 'username' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('category.html', category_name=category_name,
                               categories=categories, items=items,
                               user_loggedin=user_loggedin,
                               user_name=user_name, picture=picture)
    return render_template('category.html', category_name=category_name,
                           categories=categories, items=items)


@app.route('/catalog/<string:category_name>/<string:item_name>',
           methods=['GET'])
def getItem(category_name, item_name):
    """Display details of the selected item."""

    try:
        item = session.query(Item).filter(
            func.lower(Item.name) == func.lower(item_name)).one_or_none()
        if item is None:
            flash("Item not found. Please try again later!")
            return redirect(url_for('getCatalog'))
    except MultipleResultsFound:
        flash("Something went wrong. Please try again later!")
        return redirect(url_for('getCatalog'))
    user_loggedin = 'username' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('item.html', item=item,
                               user_loggedin=user_loggedin,
                               user_name=user_name,
                               picture=picture)
    return render_template('item.html', item=item)


@app.route('/catalog/additem', methods=['GET', 'POST'])
def addItem():
    """Create a new Item."""

    if 'email' not in login_session:
        flash("You need to login to add items!")
        return redirect(url_for('getCatalog'))
    if request.method == 'POST':
        # set created user to current user
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        name = request.form['name']
        if name is not None and len(name) != 0:
            new_item = Item(name=request.form['name'])
            new_item.created_user = user
            category = request.form['category']
            if category is not None and len(category) != 0:
                new_item.category_name = category
            description = request.form['description']
            if description is not None and len(description) != 0:
                new_item.description = description
            session.add(new_item)
            session.commit()
            flash("New Book Added!")
            return redirect(url_for('getItem',
                                    category_name=new_item.category_name,
                                    item_name=new_item.name))
        else:
            flash("Book name cannot be empty!")
            # if name is empty, load the page again

    categories = session.query(Category).order_by("name")
    user_loggedin = 'email' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('additem.html', categories=categories,
                               user_loggedin=user_loggedin,
                               user_name=user_name, picture=picture)
    return render_template('additem.html', categories=categories)


@app.route('/catalog/<string:item_name>/edititem', methods=['GET', 'POST'])
def editItem(item_name):
    """Edit the selected Item."""

    if 'email' not in login_session:
        flash("Please login before you can edit items!")
        return redirect(url_for('getCatalog'))
    try:
        item = session.query(Item).filter(
            func.lower(Item.name) == func.lower(item_name)).one_or_none()
        if item is None:
            flash("Item not found. Please try again later!")
            return redirect(url_for('getCatalog'))
    except MultipleResultsFound:
        flash("Something went wrong. Please try again!")
        return redirect(url_for('getCatalog'))

    if login_session['email'] != item.created_user.email:
        flash("You can edit only your items!")
        return redirect(url_for('getItem', category_name=item.category_name,
                        item_name=item.name))

    if request.method == 'POST':
        print("in Edit POST Method")
        name = request.form['name']
        if name is not None and len(name) != 0:
            item.name = name
            category = request.form['category']
            item.category_name = category
            description = request.form['description']
            item.description = description
            session.commit()
            flash("Book Edited!")
            return redirect(url_for('getItem',
                                    category_name=item.category_name,
                                    item_name=item.name))
        else:
            flash("Book name cannot be empty!")
            return redirect(url_for('getItem',
                                    category_name=item.category_name,
                                    item_name=item.name))
    categories = session.query(Category).order_by("name")
    user_loggedin = 'username' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('edititem.html', item=item,
                               categories=categories,
                               user_loggedin=user_loggedin,
                               user_name=user_name, picture=picture)
    return render_template('edititem.html', item=item, categories=categories)


@app.route('/catalog/<string:item_name>/deleteitem', methods=['GET', 'POST'])
def deleteItem(item_name):
    """Delete the selected Item."""

    if 'email' not in login_session:
        flash("Please login before you can delete items!")
        return redirect(url_for('getCatalog'))
    try:
        item = session.query(Item).filter(
            func.lower(Item.name) == func.lower(item_name)).one_or_none()
        if item is None:
            flash("Item not found. Please try again later!")
            return redirect(url_for('getCatalog'))
    except MultipleResultsFound:
        flash("Something went wrong. Please try again!")
        return redirect(url_for('getCatalog'))

    if login_session['email'] != item.created_user.email:
        flash("You can delete only your items!")
        return redirect(url_for('getItem', category_name=item.category_name,
                        item_name=item.name))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Deleted book '" + item_name + "'.")
        return redirect(url_for('getCategory',
                                category_name=item.category_name))

    user_loggedin = 'username' in login_session
    if user_loggedin:
        user_name = login_session['username']
        picture = login_session['picture']
        return render_template('deleteitem.html', item=item,
                               user_loggedin=user_loggedin,
                               user_name=user_name, picture=picture)
    return render_template('deleteitem.html', item=item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
