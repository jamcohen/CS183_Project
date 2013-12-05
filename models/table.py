def get_email():
    if auth.user:
        return auth.user.email
    else:
        return 'None'

def get_dish_name(id):
    name = db.dish(id).name
    return name

db.define_table('dish',
                Field('name'),
                Field('description', 'text'),
                Field('price', 'decimal(3,2)'),
                Field('category'),
                Field('ingredients', 'list:string'),
                Field('ingredientWeights', 'list:integer'),
                Field('weightsMeasurements', 'list:string'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )


db.define_table('menu',
                Field('appetizer',db.dish),
                Field('entree',db.dish),
                Field('dessert',db.dish),
                Field('name'),
                Field('serving_number', 'integer'), #number of people this menu should serve
                Field('delivery_time', 'datetime'),
                Field('frequency', 'integer'), #number of days between deliveries ex. 7 = weekly deliveries
                Field('user_id', default = get_email(), writable = False)
                )

db.define_table('deliveries',
                Field('menu', db.menu),
                Field('delivery_time', 'datetime'),
                Field('user_id', default = get_email(), writable = False)
                )



