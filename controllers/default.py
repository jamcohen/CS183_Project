# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
# # This is a sample controller
# # - index is the default action of any application
# # - user is required for authentication and authorization
# # - download is for downloading files uploaded in the db (does streaming)
# # - call exposes all registered services (none by default)
#########################################################################


def index():
    
    response.flash = T("Welcome to web2py!")
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    return dict(menu="yolo")

@auth.requires_login()
def make_dish():
    
    response.flash = T("Welcome to web2py!")
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]

    db.dish.category.requires = IS_IN_SET(['Appetizer', 'Entree', 'Dessert'])
    form = SQLFORM(db.dish, fields = ['name', 'description', 'price', 'ingredients',
                                       'category', 'vegetarian', 'vegan', 'gluten_free'])
    if form.process().accepted:
        db.dish(form.vars.id)
        redirect(URL('default', 'view_dish', args=[form.vars.id]))
    return dict(form=form)

def view_dish():
    dish = db.dish(request.args(0,cast=int))
    return dict(dish=dish)

def all_dishes():
    q = db.dish
    grid = SQLFORM.grid(q,
           fields = [db.dish.name],
           csv = False
           )
    return dict(grid=grid)

@auth.requires_login() 
def create_menu():
    
    response.flash = T("Welcome to web2py!")
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    db.menu.appetizer.requires = IS_IN_DB(db(db.dish.category=="Appetizer"), db.dish.id, '%(name)s')
    db.menu.entree.requires = IS_IN_DB(db(db.dish.category=="Entree"), db.dish.id, '%(name)s')
    db.menu.dessert.requires = IS_IN_DB(db(db.dish.category=="Dessert"), db.dish.id, '%(name)s')
    form = SQLFORM(db.menu, fields = ['name', 'appetizer', 'entree', 'dessert',
                                       'serving_number', 'delivery_time', 'frequency'],)
    if form.process().accepted:
        
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
       response.flash = 'please fill the form'
   # Note: no form instance is passed to the view
    return dict(form=form)

def get_dish_name(id):
    name = db.dish(id).name
    return name

@auth.requires_login() 
def my_menus():
    
    response.flash = T("Welcome to web2py!")
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    email = auth.user.email
    mymenus = db(db.menu.user_id == email).select()
    for menu in mymenus:
        menu.update_record(appetizer_name=get_dish_name(menu.appetizer))
        menu.update_record(entree_name=get_dish_name(menu.entree))
        menu.update_record(dessert_name=get_dish_name(menu.dessert))
        print menu.appetizer
    return dict(mymenus=mymenus)


@auth.requires_login() 
def view_menu():
    
    response.flash = T("Welcome to web2py!")
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    menu = db.menu(request.args(0))
    email = auth.user.email
    if menu.user_id == email:
        return dict(menu=menu)
    else:
        session.flash = 'invalid request'
        redirect(URL('default', 'index'))
        
def all_menus():
   
   menus = SQLFORM.grid(db.menu)
   return locals()
        

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
