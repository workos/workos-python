from workos.types.directory_sync import DirectoryGroup
from workos.types.events.previous_attributes import PreviousAttributes


class DirectoryGroupWithPreviousAttributes(DirectoryGroup):
    previous_attributes: PreviousAttributes
