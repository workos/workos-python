class SSOProfile(object):
    OBJECT_FIELDS = [
        'id',
        'email',
        'first_name',
        'connection_type',
        'last_name',
        'idp_id',
    ]
    
    @classmethod
    def construct_from_response(cls, response):
        profile_data = response['profile']

        profile = cls()
        for field in SSOProfile.OBJECT_FIELDS:
            setattr(profile, field, profile_data[field])

        return profile

    def to_dict(self):
        profile_dict = {}
        for field in SSOProfile.OBJECT_FIELDS:
            profile_dict[field] = getattr(self, field, None)

        return profile_dict