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
    delivery = get_next_delivery()
    return dict(delivery=delivery)

@auth.requires_login()
def make_dish():
    weightURL = URL('default', 'add_weights')
    db.dish.category.requires = IS_IN_SET(['Appetizer', 'Entree', 'Dessert'])

    form = SQLFORM(db.dish, fields = ['name', 'description', 'price', 'ingredients',
                                       'category', 'vegetarian', 'vegan', 'gluten_free'])
    if form.process().accepted:
        response.flash = 'Your dish has been created'
        redirect(URL('default', 'view_dish',args=[form.vars.id]))
    return dict(form=form, menu="yolo")

    return dict(form=form,weightURL=weightURL)

@auth.requires_login()
def add_weights():
    weightArray = eval(request.vars.array)
    dishid = int(request.vars.id)
    dish = db.dish(dishid)
    for i in range(len(weightArray)):
        if (((i+2)%2) == 0):
            dish.ingredientWeights.insert(weightArray[i])
        else:
            dish.weightsMeasurements.insert(weightArray[i])

    return response.json(dict(result=weightArray))

def about_us():
    return dict()


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
    date = get_date_from_json(request.vars['datetime'])
    name = request.vars['name']
    frequency = int(request.vars['frequency'])
    end = date + timedelta(30)

    menu = db((db.menu.name == name) & (db.menu.user_id == email)).select().first()
    if menu == None:
        return json.dumps({'success':False})

    deliveries = db(db.deliveries.menu == menu.id).select()
    timeout = 0

    #gets the dates to add to the calendar
    while date < end:
        timeframe = query_by_date(date)
        t = db.deliveries
        query = (t.menu==menu.id) & (t.delivery_time >= timeframe[0]) & (t.delivery_time < timeframe[1]) & (t.user_id==email)
        overwrittenSet = db(query)
        overwrittendelivery = overwrittenSet.select().first()
        if overwrittendelivery is None:
            db.deliveries.insert(menu=menu, delivery_time=date)
        else:
            overwrittenSet.update(delivery_time=date)

        if frequency <= 0:
            break

        date = date + timedelta(frequency*7)

        timeout+=1
        if timeout > 60:
            return json.dumps({'success':frequency})

    return  json.dumps({'success':True})

def move_delivery():
    newDate = get_date_from_json(request.vars['newDate'])
    oldDate = newDate - timedelta(int(request.vars['dayDelta']))
    name = request.vars['name']
    email = get_email()
    menu = db((db.menu.name == name) & (db.menu.user_id == email)).select().first()
    if menu is None:
        return {'success':False, 'reload':False}

    timeframe = query_by_date(oldDate)
    t = db.deliveries
    query = (t.menu==menu.id) & (t.delivery_time >= timeframe[0]) & (t.delivery_time < timeframe[1]) & (t.user_id==email)
    deliverySet = db(query)
    delivery = deliverySet.select().first()
    if delivery is None:
        return json.dumps({'success':False, 'error':"Could not find original record", 'reload':False})
    else:
        #check if an event of the same name already exists in that location, if so overwrite it
        timeframe = query_by_date(newDate)
        t = db.deliveries
        query = (t.menu==menu.id) & (t.delivery_time >= timeframe[0]) & (t.delivery_time < timeframe[1]) & (t.user_id==email)
        overwrittenSet = db(query)
        overwrittenDelivery = overwrittenSet.select().first()
        if overwrittenDelivery is None:
            deliverySet.update(delivery_time=newDate)
        else:
            overwrittenSet.update(delivery_time=newDate)
            deliverySet.delete()
            response.flash = 'Meal Overwritten'
            return  json.dumps({'success':True, 'reload':True})


    return  json.dumps({'success':True, 'reload':False})


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
def get_next_delivery():
    email = auth.user.email
    myMenus = db(db.menu.user_id == email).select()
    start = datetime.today()
    end = start + timedelta(31)
    date = datetime.today() - timedelta(1)

    nextDelivery = db( (db.deliveries.delivery_time >= start) & (db.deliveries.delivery_time < end) & (db.deliveries.user_id==email)).select(orderby=db.deliveries.delivery_time).first()
    return nextDelivery



@auth.requires_login()
def get_json_schedule():
    email = auth.user.email
    myMenus = db(db.menu.user_id == email).select()
    if myMenus is None:
        return json.dumps([])

    start = datetime.fromtimestamp(long(request.vars['start']))
    end = datetime.fromtimestamp(long(request.vars['end']))
    data = []
    deliveries = db( (db.deliveries.delivery_time <= end) & (db.deliveries.delivery_time >= start) & (db.deliveries.user_id == email)).select()

    for delivery in deliveries:
        date = delivery.delivery_time
        if date is None:
            continue
        color = '#FFDEAD' if date < datetime.today() else '#C2B280'
        event = {'title':delivery.menu.name, 'start':date.strftime('%Y-%m-%dT%H:%M:%S'), 'color':color};
        data.append(event)

    return json.dumps(data)

def query_by_date(dt):
    date_start = dt.date()
    date_end = date_start + timedelta(days=1)
    return date_start, date_end

def get_date_from_json(dateString):
    newDate = str.join(' ', dateString.split(' ')[0:5])
    date = datetime.strptime(newDate, '%a %b %d %Y %H:%M:%S')
    return date


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
