from passlib.hash import bcrypt

# ------------------------------------


def hash_password(password):
    return bcrypt.hash(password)


def verify_password(password, hash):
    return bcrypt.verify(password, hash)
