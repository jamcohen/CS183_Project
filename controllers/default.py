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
    
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    #to populate the drop down to select the category
    categories = ("Appetizer", "Entree", "Dessert")
    form = SQLFORM.factory(Field('category', requires=IS_IN_SET(range(1, 4), categories)), db.dessert, db.appetizer, db.entree, deletable=True, upload=URL(r=request, f='download'))
    
    #based on which category the user selects the form processes to a different table
    if form.process().accepted:
        if(form.vars.category == "1"):
            db.appetizer.insert(**db.appetizer._filter_fields(form.vars))
            response.flash = 'form accepted'
            redirect(URL('default', 'view_dish',args=[form.vars.name,"appetizer"]))
        elif(form.vars.category == "2"):
            db.entree.insert(**db.entree._filter_fields(form.vars))
            response.flash = 'form accepted'
            redirect(URL('default', 'view_dish',args=[form.vars.name,"entree"]))
        elif(form.vars.category == "3"):
            db.dessert.insert(**db.dessert._filter_fields(form.vars))
            response.flash = 'form accepted'
            redirect(URL('default', 'view_dish',args=[form.vars.name,"dessert"]))
        
    return dict(form=form, menu="yolo")

#method to view single dishes
def view_dish():
   
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    dishname = request.args(0).replace("_"," ")
    if(request.args(1) == "appetizer"):
        dish = db(db.appetizer.name==dishname).select().first()
        return dict(dish=dish)
    elif(request.args(1) == "entree"):
        dish = db(db.entree.name==dishname).select().first()
        return dict(dish=dish)
    elif(request.args(1) == "dessert"):
        dish = db(db.dessert.name==dishname).select().first()
        return dict(dish=dish,menu="yolo")
    

def all_dishes():
   
   appetizers = SQLFORM.grid(db.appetizer)
   entrees = SQLFORM.grid(db.entree)
   desserts = SQLFORM.grid(db.dessert)
   return locals()

@auth.requires_login() 
def create_menu():
    
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
    
    db.menu.appetizer.requires = IS_IN_DB(db, 'appetizer.name', '%(name)s')
    db.menu.entree.requires = IS_IN_DB(db, 'entree.name', '%(name)s')
    db.menu.dessert.requires = IS_IN_DB(db, 'dessert.name', '%(name)s')

    form = SQLFORM(db.menu)
    if form.process().accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
       response.flash = 'please fill the form'
   # Note: no form instance is passed to the view
    return dict(form=form, menu="yolo")

@auth.requires_login() 
def my_menus():
    
    response.menu = [['Home', False, URL('default', 'index')],
                     ['Make A Menu', False, URL('default', 'create_menu')],
                     ['Make A Schedule', False, URL('default', 'construction')],
                     ['Make A Dish', False, URL('default', 'make_dish')],
                     ['View My Menus', False, URL('default', 'my_menus')]]
        
    email = auth.user.email
    mymenus = db(db.menu.user_id == email).select()
    return dict(mymenus=mymenus, menu="yolo")


@auth.requires_login() 
def view_menu():
    
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
