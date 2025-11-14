from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.events.previous_attributes import PreviousAttributes


class DirectoryUserWithPreviousAttributes(DirectoryUser):
    previous_attributes: PreviousAttributes
