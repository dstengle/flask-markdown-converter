"""
Pydantic models for request validation.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CalendarEventTime(BaseModel):
    """Model for calendar event time."""
    
    date: Optional[str] = None
    dateTime: Optional[str] = None
    timeZone: Optional[str] = None
    
    @validator('date')
    def validate_date(cls, v):
        """Validate date format."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Invalid date format. Expected YYYY-MM-DD')
        return v
    
    @validator('dateTime')
    def validate_date_time(cls, v):
        """Validate dateTime format."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid dateTime format. Expected ISO 8601')
        return v


class CalendarEventPerson(BaseModel):
    """Model for calendar event person (creator, organizer, attendee)."""
    
    email: Optional[str] = None
    displayName: Optional[str] = None
    self: Optional[bool] = None
    responseStatus: Optional[str] = None


class WorkingLocationProperties(BaseModel):
    """Model for working location properties."""
    
    type: str
    homeOffice: Optional[Dict[str, Any]] = None
    customLocation: Optional[Dict[str, Any]] = None
    officeLocation: Optional[Dict[str, Any]] = None


class CalendarEvent(BaseModel):
    """Model for Google Calendar event."""
    
    id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: CalendarEventTime
    end: CalendarEventTime
    created: Optional[str] = None
    updated: Optional[str] = None
    status: Optional[str] = None
    creator: Optional[CalendarEventPerson] = None
    organizer: Optional[CalendarEventPerson] = None
    attendees: Optional[List[CalendarEventPerson]] = None
    eventType: Optional[str] = None
    workingLocationProperties: Optional[WorkingLocationProperties] = None
    
    # Additional fields that might be present
    htmlLink: Optional[str] = None
    iCalUID: Optional[str] = None
    kind: Optional[str] = None
    originalStartTime: Optional[CalendarEventTime] = None
    recurringEventId: Optional[str] = None
    reminders: Optional[Dict[str, Any]] = None
    sequence: Optional[int] = None
    transparency: Optional[str] = None
    visibility: Optional[str] = None
    etag: Optional[str] = None


class CalendarEventList(BaseModel):
    """Model for a list of Google Calendar events."""
    
    __root__: List[CalendarEvent]


class ConversionOptions(BaseModel):
    """Model for conversion options."""
    
    template: Optional[str] = Field(None, description="Template ID to use for conversion")
    preprocessors: Optional[List[str]] = Field(None, description="List of preprocessor IDs to apply")
    timezone: Optional[str] = Field(None, description="Timezone for date/time formatting")