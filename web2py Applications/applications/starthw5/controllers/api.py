#import tempfile

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
#from gluon.utils import web2py_uuid

# Here go your api methods.

@auth.requires_signature(hash_vars=False)
def get_images():
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    images = []
    has_more = False
    rows = db(db.user_images.user_email == auth.user.email).select(db.user_images.ALL, limitby=(start_idx, end_idx + 1), orderby=~db.user_images.id)

    for i, r in enumerate(rows):
        if i < end_idx - start_idx:
            m = dict(
                id = r.id,
                user_email = r.user_email,
                image_url = r.image_url,
                price = r.price,
            )
            images.append(m)
        else:
            has_more = True
    logged_in = auth.user is not None
    return response.json(dict(images=images, looged_in=logged_in, has_more=has_more,))


def get_users():
    users = []
    if auth.user is not None:
        rows = db(db.auth_user.email != auth.user.email).select(db.auth_user.ALL)
    else:
        rows = db().select(db.auth_user.ALL)

    for i, r in enumerate(rows):
        m = dict(
            id=r.id,
            user_email=r.email,
            first_name=r.first_name,
            last_name=r.last_name
        )
        users.append(m)

    return response.json(dict(users=users,))


def get_user_images():
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0
    user_email = request.vars.user_email if request.vars.user_email is not None else ""
    has_more = False
    images = []
    rows = db(db.user_images.user_email == user_email).select(db.user_images.ALL, limitby=(start_idx, end_idx + 1),  orderby=~db.user_images.id)

    for i, r in enumerate(rows):
        if i < end_idx - start_idx:
            m = dict(
                id = r.id,
                user_email = r.user_email,
                image_url = r.image_url,
                price = r.price,
            )
            images.append(m)
        else:
            has_more = True
    logged_in = auth.user is not None
    return response.json(dict(images=images, looged_in=logged_in, has_more=has_more,))


@auth.requires_signature()
def add_image():
    m_id = db.user_images.insert(
        image_url = request.vars.image_url,
        price = request.vars.price
    )
    m = db.user_images(m_id)
    image = dict(
        id = m.id,
        image_url = m.image_url,
        price = m.price,
    )
    return response.json(dict(image=image))

@auth.requires_signature()
def edit_price():
    img = db(db.user_images.id == request.vars.id).select().first()
    img.update_record(price = request.vars.price)
    return dict()

def purchase():
    """Ajax function called when a customer orders and pays for the cart."""
    if not URL.verify(request, hmac_key=session.hmac_key):
        raise HTTP(500)
    # Creates the charge.
    import stripe
    # Your secret key.
    stripe.api_key = myconf.get('stripe.private_key')
    token = json.loads(request.vars.transaction_token)
    amount = float(request.vars.amount)
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            source=token['id'],
            description="Purchase",
        )
    except stripe.error.CardError as e:
        logger.info("The card has been declined.")
        logger.info("%r" % traceback.format_exc())
        return "nok"
    return "ok"
