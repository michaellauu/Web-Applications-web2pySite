import tempfile

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
from gluon.utils import web2py_uuid

@auth.requires_signature()
def add_image():
    img_id = db.user_images.insert(image_url = request.vars.image_url, category = request.vars.current_page)
    i = db.user_images(img_id)
    return response.json(dict(image_data = dict(
        id = i.id,
        created_on = i.created_on,
        created_by = i.created_by,
        image_url = i.image_url,
        upvotes = i.upvotes,
        downvotes = i.downvotes,
        category = i.category
    )))

def get_profile_images():
    current_id = int(request.vars.current_id) if request.vars.current_id is not None else 0
    images = []
    ratings = []
    rate = db().select(db.ratings.ALL)
    img = db().select(db.user_images.ALL)
    for i in rate:
        if i.user_id == current_id:
            ra = dict (
                id = i.user_id,
                image_id = i.image_id,
                image_url = i.image_url,
                favorited = i.favorited,
                upvote = i.upvote,
                downvote = i.downvote
            )
            ratings.append(ra)
    for r in img:
        print r.created_by == current_id
        if r.created_by == current_id:
            t = dict(
                id = r.id,
                created_on = r.created_on,
                created_by = r.created_by,
                image_url = r.image_url,
                upvotes= r.upvotes,
                downvotes=r.downvotes,
            )
            images.append(t)
    if (auth.user_id is not None):
        user_id = auth.user_id
    else:
        user_id = 0
    logged_in = auth.user is not None
    return response.json(dict(
        images = images,
        logged_in = logged_in,
        ratings = ratings,
        user_id = user_id,
    ))

def get_user():
    users = []
    u = db(db.auth_user.id > 0).select()
    if auth.is_logged_in():
        cuser = dict(
            id = auth.user.id,
            first_name = auth.user.first_name,
            last_name = auth.user.last_name
        )
        users.append(cuser)
    for i in u:
        if (i.id != auth.user_id):
            ouser = dict(
                id = i.id,
                first_name = i.first_name,
                last_name = i.last_name
            )
            users.append(ouser)
    if (auth.user_id is not None):
        user_id = auth.user_id
    else:
        user_id = 0
    return response.json(dict(
        users = users,
        user_id = user_id,
    ))

@auth.requires_signature()
def del_image():
    db(db.user_images.id == request.vars.id).delete()
    db(db.ratings.image_id == request.vars.id).delete()
    return "done"

@auth.requires_signature()
def toggle_favorite():
    image_id = int(request.vars.image_id) if request.vars.image_id is not None else 0
    u = db(db.ratings.user_id == request.vars.user_id).select()
    for i in u:
        if i.image_id == image_id:
            i.update_record(favorited = not i.favorited)
    return "done"

@auth.requires_signature()
def toggle_upvote():
    image_id = int(request.vars.image_id) if request.vars.image_id is not None else 0
    u = db(db.ratings.user_id == request.vars.user_id).select()
    work = db.user_images(request.vars.id)
    for i in u:
        if i.image_id == image_id:
            i.update_record(upvote = not i.upvote)
            if (i.upvote is True and i.downvote is True):
                i.update_record(downvote = not i.downvote)
                work.update_record(downvotes=work.downvotes - 1)
            if (i.upvote is True):
                work.update_record(upvotes=work.upvotes + 1)
            if (i.upvote is False):
                work.update_record(upvotes=work.upvotes - 1)
    return "done"

@auth.requires_signature()
def toggle_downvote():
    image_id = int(request.vars.image_id) if request.vars.image_id is not None else 0
    u = db(db.ratings.user_id == request.vars.user_id).select()
    work = db.user_images(request.vars.id)
    for i in u:
        if i.image_id == image_id:
            i.update_record(downvote = not i.downvote)
        if (i.upvote is True and i.downvote is True):
            i.update_record(upvote = not i.upvote)
            work.update_record(upvotes=work.upvotes - 1)
        if (i.downvote is True):
            work.update_record(downvotes=work.downvotes + 1)
        if (i.upvote is False):
            work.update_record(downvotes=work.downvotes - 1)
    return "done"

@auth.requires_signature()
def add_favorite():
    img_id = db.ratings.insert(user_id = request.vars.user_id, image_id = request.vars.image_id, favorited = True, image_url = request.vars.image_url)
    i = db.ratings(img_id)
    favorite_data = dict(
        id = i.user_id,
        image_id = i.image_id,
        image_url = i.image_url,
        favorited = i.favorited,
        upvote = i.upvote,
        downvote = i.downvote
    )
    return response.json(dict(
        favorite_data= favorite_data
    ))

@auth.requires_signature()
def add_upvote():
    img_id = db.ratings.insert(user_id = request.vars.user_id, image_id = request.vars.image_id, upvote = True, image_url = request.vars.image_url)
    i = db.ratings(img_id)
    upvote_data = dict(
        id = i.user_id,
        image_id = i.image_id,
        image_url = i.image_url,
        favorited = i.favorited,
        upvote = i.upvote,
        downvote = i.downvote
    )
    addup = db.user_images(request.vars.image_id)
    addup.update_record(upvotes = addup.upvotes+1)
    return response.json(dict(
        upvote_data= upvote_data
    ))

@auth.requires_signature()
def add_downvote():
    img_id = db.ratings.insert(user_id = request.vars.user_id, image_id = request.vars.image_id, downvote = True, image_url = request.vars.image_url)
    i = db.ratings(img_id)
    downvote_data = dict(
        id = i.user_id,
        image_id = i.image_id,
        image_url = i.image_url,
        favorited = i.favorited,
        upvote = i.upvote,
        downvote = i.downvote
    )
    adddown = db.user_images(request.vars.image_id)
    adddown.update_record(downvotes = adddown.downvotes+1)
    return response.json(dict(
        downvote_data= downvote_data
    ))

def get_images():
    current_id = int(request.vars.current_id) if request.vars.current_id is not None else 0
    current_page = str(request.vars.current_page) if request.vars.current_page is not None else 'ALL'
    images = []
    ratings = []
    rate = db().select(db.ratings.ALL)
    img = db().select(db.user_images.ALL)
    for i in rate:
        if i.user_id == current_id:
            ra = dict (
                id = i.user_id,
                image_id = i.image_id,
                image_url = i.image_url,
                favorited = i.favorited,
                upvote = i.upvote,
                downvote = i.downvote
            )
            ratings.append(ra)
    for r in img:
        if r.category == current_page:
            t = dict(
                id = r.id,
                created_on = r.created_on,
                created_by = r.created_by,
                image_url = r.image_url,
                upvotes= r.upvotes,
                downvotes=r.downvotes,
                category = r.category
            )
            images.append(t)
        elif current_page == 'ALL':
            t = dict(
                id = r.id,
                created_on = r.created_on,
                created_by = r.created_by,
                image_url = r.image_url,
                upvotes= r.upvotes,
                downvotes=r.downvotes,
                category = r.category
            )
            images.append(t)
    if (auth.user_id is not None):
        user_id = auth.user_id
    else:
        user_id = 0
    logged_in = auth.user is not None
    return response.json(dict(
        images = images,
        ratings = ratings,
        logged_in = logged_in,
        user_id = user_id,
    ))
# Here go your api methods.


