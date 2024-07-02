from typing import Dict, Any, Optional, List
from enum import Enum

JsonDict = Dict[str, Any]

class DirectoryUserRole():
  def __init__(self, attributes: JsonDict) -> None:
    self.slug: str = attributes['slug']

class DirectoryUserEmail():
  def __init__(self, attributes: JsonDict) -> None:
    self.type: Optional[str] = attributes.get('type')
    self.value: Optional[str] = attributes.get('value')
    self.primary: Optional[bool] = attributes.get('primary')

class DirectoryUserState(Enum):
  ACTIVE = 'active'
  INACTIVE = 'inactive'

class DirectoryUserCreatedEvent():
  def __init__(self, attributes: JsonDict) -> None:
    self.id: str = attributes['id']
    self.name: str = attributes['name']
    self.idp_id: str = attributes['idp_id']
    self.directory_id: str = attributes['directory_id']
    self.organization_id: str = attributes['organization_id']
    self.first_name: Optional[str] = attributes.get('first_name')
    self.last_name: Optional[str] = attributes.get('last_name')
    self.job_title: Optional[str] = attributes.get('job_title')
    self.emails: List[DirectoryUserEmail] = []
    for email in attributes.get('emails'):
      self.emails.push(DirectoryUserEmail(email))
    self.username: Optional[str] = attributes.get('username')
    self.state: DirectoryUserState = DirectoryUserState(attributes['state'])
    self.custom_attributes: JsonDict = attributes.get('custom_attributes', {})
    self.raw_attributes: JsonDict = attributes.get('raw_attributes', {})
    self.created_at: str = attributes['created_at']
    self.updated_at: str = attributes['updated_at']
    self.raw_attributes: JsonDict = attributes.get('raw_attributes', {})
    self.role: Optional[DirectoryUserRole] = attributes.get('role') ? DirectoryUserRole(attributes['role']) : None
    # always 'directory_user' for this event
    self.object: str = attributes['object'] 