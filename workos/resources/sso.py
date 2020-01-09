class WorkOSProfile(object):
    '''Representation of a User Profile as returned by WorkOS through the SSO feature.
    
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfile is comprised of.
    '''

    OBJECT_FIELDS = [
        'id',
        'email',
        'first_name',
        'last_name',
        'connection_type',
        'idp_id',
    ]
    
    @classmethod
    def construct_from_response(cls, response):
        '''Returns an instance of WorkOSProfile.

        Args:
            response (dict): Response from a WorkOS API request as returned by RequestHelper

        Returns:
            WorkOSProfile: The WorkOS profile of a User
        '''
        profile_data = response['profile']

        profile = cls()
        for field in WorkOSProfile.OBJECT_FIELDS:
            setattr(profile, field, profile_data[field])

        return profile

    def to_dict(self):
        '''Returns a dict representation of the WorkOSProfile.
        
        Returns:
            dict: A dict representation of the WorkOSProfile
        '''
        profile_dict = {}
        for field in WorkOSProfile.OBJECT_FIELDS:
            profile_dict[field] = getattr(self, field, None)

        return profile_dict