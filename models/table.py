def get_email():
    if auth.user:
        return auth.user.email
    else:
        return 'None'
    
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
                Field('name'),
                Field('description', 'text'),
                Field('price', 'decimal(3,2)'),
                Field('ingredients', 'list:string'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )

db.define_table('menu',
                Field('appetizer'),
                Field('entree'),
                Field('dessert'),
                Field('name'),
                Field('serving_number', 'integer'), #number of people this menu should serve
                Field('delivery_time', 'datetime'),
                Field('frequency', 'integer'), #number of days between deliveries ex. 7 = weekly deliveries
                Field('user_id', default = get_email(), writable = False)
                )

