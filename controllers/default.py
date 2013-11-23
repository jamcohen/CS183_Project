# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
# # This is a sample controller
# # - index is the default action of any application
# # - user is required for authentication and authorization
# # - download is for downloading files uploaded in the db (does streaming)
# # - call exposes all registered services (none by default)
#########################################################################
from datetime import date, datetime, timedelta
import json

@auth.requires_login()
def index():
    menu = get_next_menu()
    return dict(menu=menu)

@auth.requires_login()
def make_dish():
    db.dish.category.requires = IS_IN_SET(['Appetizer', 'Entree', 'Dessert'])
    form = SQLFORM(db.dish, fields = ['name', 'description', 'price', 'ingredients',
                                       'category', 'vegetarian', 'vegan', 'gluten_free'])
    if form.process().accepted:
        response.flash = 'Your dish has been created'
        redirect(URL('default', 'view_dish',args=[form.vars.id]))


    return dict(form=form, menu="yolo")

@auth.requires_login()
#method to view single dishes
def view_dish():
    dish = db.dish(db.dish.id==request.args(0))
    if dish is None:
        session.flash = 'invalid request'
        redirect(URL('default', 'index'))
    return dict(dish=dish)

@auth.requires_login()
def all_dishes():
    q = db.dish
    grid = SQLFORM.grid(q,
           fields = [db.dish.name],
           csv = False
           )
    return dict(grid=grid)

@auth.requires_login()
def schedule():
    email = get_email()
    rows = db(db.menu.user_id == email).select()
    return dict(rows=rows)

@auth.requires_login()
def set_schedule():
    #date = json.load(request.vars)
    email = get_email()
    jsonDate = request.vars['datetime']
    #Tue Nov 05 2013 22:00:00 GMT-0800 (PST)
    date = datetime.strptime(jsonDate, '%a %b %d %Y %H:%M:%S GMT-0800 (PST)')
    name = request.vars['name']
    frequency = request.vars['frequency']
    query = (db.menu.name==name) & (db.menu.user_id==email)
    db(query).update(delivery_time=date)
    db(query).update(frequency=frequency)
    return  json.dumps({'success':True})


@auth.requires_login()
def create_menu():
    db.menu.appetizer.requires = IS_IN_DB(db(db.dish.category=="Appetizer"), db.dish.id, '%(name)s')
    db.menu.entree.requires = IS_IN_DB(db(db.dish.category=="Entree"), db.dish.id, '%(name)s')
    db.menu.dessert.requires = IS_IN_DB(db(db.dish.category=="Dessert"), db.dish.id, '%(name)s')
    form = SQLFORM(db.menu, fields = ['name', 'appetizer', 'entree', 'dessert',
                                       'serving_number'],)
    if form.process().accepted:
        response.flash = 'Your menu has been created'
        redirect(URL('default', 'view_menu',args=[form.vars.id]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
       response.flash = 'Please fill out the form'
    return dict(form=form)

def get_dish_name(id):
    name = db.dish(id).name
    return name

@auth.requires_login()
def my_menus():
    email = auth.user.email
    mymenus = db(db.menu.user_id == email).select()
    return dict(mymenus=mymenus)


@auth.requires_login()
def view_menu():
    menu = db.menu(request.args(0))
    if menu is None:
        session.flash = 'invalid request'
        redirect(URL('default', 'index'))
    email = auth.user.email
    if menu.user_id == email:
        return dict(menu=menu, app=menu.appetizer)
    else:
        session.flash = 'invalid request'
        redirect(URL('default', 'index'))

@auth.requires_login()
def all_menus():
   menus = SQLFORM.grid(db.menu)
   return dict(menus=menus)

@auth.requires_login()
def get_next_menu():
    email = auth.user.email
    myMenus = db(db.menu.user_id == email).select()
    start = datetime.today()
    end = start + timedelta(31)
    date = datetime.today() - timedelta(1)

    #very inefficient, should probably get a better way to do this
    #generate all menus in the next month
    recurringMenus = []
    for menu in myMenus:
        frequency = menu.frequency
        date = menu.delivery_time
        recurringMenus.append({'menu':menu, 'date':date})
        while date < end:
            date = date + timedelta(frequency*7)
            recurringMenus.append({'menu':menu, 'date':date})

    recurringMenus.sort(key=lambda menu: menu['date'])
    nextMenu = None
    for event in recurringMenus:
        if event['date'] > start:
            nextMenu = event
            break

    return nextMenu



@auth.requires_login()
def get_json_schedule():
    email = auth.user.email
    myMenus = db(db.menu.user_id == email).select()
    start = datetime.fromtimestamp(long(request.vars['start']))
    end = datetime.fromtimestamp(long(request.vars['end']))
    data = []
    for menu in myMenus:
        frequency = menu.frequency
        date = menu.delivery_time
        color = 'rgb(200,200,200)' if date < datetime.today() else 'yellow'
        event = {'title':menu.name, 'start':date.strftime('%Y-%m-%dT%H:%M:%S'), 'color':color};
        data.append(event)
        while date < end:
            date = date + timedelta(frequency*7)
            color = 'rgb(200,200,200)' if date < datetime.today() else 'yellow'
            event = {'title':menu.name, 'start':date.strftime('%Y-%m-%dT%H:%M:%S'), 'color':color};
            data.append(event)

    return json.dumps(data)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def construction():
    return dict(message="Under Construction")


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
