from workos.resources.directory_sync import DirectoryUser
from workos.types.events.previous_attributes import PreviousAttributes


class DirectoryUserWithPreviousAttributes(DirectoryUser):
    previous_attributes: PreviousAttributes
