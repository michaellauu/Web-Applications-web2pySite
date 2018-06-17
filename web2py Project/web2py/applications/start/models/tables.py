# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db, hmac_key=Auth.get_or_create_key())
crud, service, plugins = Crud(db), Service(), PluginManager()

import datetime

def get_user_email():
    return auth.user.email if auth.user else None

db.define_table('user_images',
                Field('user_email', default=get_user_email()),
                Field('created_by', 'reference auth_user', default=auth.user_id),
                Field('created_on', 'datetime', default=request.now),
                Field('image_url'),
				Field('upvotes', 'integer', default=0),
                Field('downvotes', 'integer', default=0),
                Field('category', default = 'ALL'),
                )

db.define_table('ratings',
                Field('user_id', db.auth_user, default=auth.user_id),
                Field('image_id', 'integer'),
                Field('image_url'),
                Field('favorited', 'boolean', default=False),
                Field('upvote', 'boolean', default=False),
                Field('downvote', 'boolean', default=False),
                )

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
