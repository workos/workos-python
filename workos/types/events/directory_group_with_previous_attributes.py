from workos.types.directory_sync.directory_group import DirectoryGroup
from workos.types.events.previous_attributes import PreviousAttributes


class DirectoryGroupWithPreviousAttributes(DirectoryGroup):
    previous_attributes: PreviousAttributes
