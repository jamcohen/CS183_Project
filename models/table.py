def get_email():
    if auth.user:
        return auth.user.email
    else:
        return 'None'
<<<<<<< HEAD

def get_dish_name(id):
    name = db.dish(id).name
    return name
    
db.define_table('dish',
=======
    
db.define_table('appetizer',
                Field('name'),
                Field('description', 'text'),
                Field('price', 'decimal(3,2)'),
                Field('ingredients', 'list:string'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )

db.define_table('entree',
                Field('name'),
                Field('description', 'text'),
                Field('price', 'decimal(3,2)'),
                Field('ingredients', 'list:string'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )

db.define_table('dessert',
>>>>>>> ea7f5e14eede99b614fa877e26ef0e200c822582
                Field('name'),
                Field('description', 'text'),
                Field('price', 'decimal(3,2)'),
                Field('category'),
                Field('ingredients', 'list:string'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )


db.define_table('menu',
<<<<<<< HEAD
                Field('appetizer',db.dish),
                Field('appetizer_name'),
                Field('entree',db.dish),
                Field('entree_name'),
                Field('dessert',db.dish),
                Field('dessert_name'),
=======
                Field('appetizer'),
                Field('entree'),
                Field('dessert'),
>>>>>>> ea7f5e14eede99b614fa877e26ef0e200c822582
                Field('name'),
                Field('serving_number', 'integer'), #number of people this menu should serve
                Field('delivery_time', 'datetime'),
                Field('frequency', 'integer'), #number of days between deliveries ex. 7 = weekly deliveries
                Field('user_id', default = get_email(), writable = False)
                )

