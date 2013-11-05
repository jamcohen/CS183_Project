db.define_table('dish',
                Field('name'),
                Field('description', 'text'),
                Field('cost', decimal(3,2)),
                Field('ingredients', 'list:string'),
                Field('category', 'String'),
                Field('vegetarian', 'boolean'),
                Field('vegan', 'boolean'),
                Field('gluten_free', 'boolean')
                )

db.define_table('menu',
                Field('appetizer', db.dish),
                Field('entree', db.dish),
                Field('dessert',  db.dish),
                Field('name'),
                Field('serving_number', 'boolean'), #number of people this menu should serve
                Field('delivery_time', 'datetime'),
                Field('frequency', 'integer'), #number of days between deliveries ex. 7 = weekly deliveries
                Field('user', db.auth_user)
                )
