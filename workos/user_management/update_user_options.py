def serialize_update_user_options(options):
    return {
        'email': options['email'],
        'email_verified': options['emailVerified'],
        'first_name': options['firstName'],
        'last_name': options['lastName'],
        'password': options['password'],
        'password_hash': options['passwordHash'],
        'password_hash_type': options['passwordHashType'],
        'external_id': options['externalId'],
    }