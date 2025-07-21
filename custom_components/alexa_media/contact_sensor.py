"""Alexa Media Player Contact Sensor
This module defines a contact sensor entity for Home Assistant that is controlled by an Echo device.
It inherits from `CoordinatorEntity` and `BinarySensorEntity`, allowing it to integrate with Home Assistant's update coordinator system and binary sensor functionality.
"""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .alexa_entity import parse_detection_state_from_coordinator

_LOGGER = logging.getLogger(__name__)

class ContactSensor(CoordinatorEntity, BinarySensorEntity):
    """A contact sensor controlled by an Echo."""

    def __init__(
        self, 
        coordinator: CoordinatorEntity, 
        details: dict,
        device_class: BinarySensorDeviceClass = BinarySensorDeviceClass.DOOR
    ):
        """Initialize the contact sensor entity."""
        super().__init__(coordinator)
        self.alexa_entity_id = details["id"]
        self._name = details["name"]
        self._attr_device_class = device_class

    @property
    def name(self):
        """Return name."""
        return self._name

    @property
    def unique_id(self):
        """Return unique id."""
        return self.alexa_entity_id

    @property
    def is_on(self):
        """Return whether on."""
        detection = parse_detection_state_from_coordinator(
            self.coordinator, self.alexa_entity_id, "Alexa.ContactSensor"
        )
        return detection == "DETECTED"

    @property
    def assumed_state(self) -> bool:
        """Return assumed state."""
        # If the coordinator has no data or the entity ID is not in the data,
        # we assume the state is not accurate.
        # This is a simple check to determine if the last refresh was successful.
        last_refresh_success = (
            self.coordinator.data and self.alexa_entity_id in self.coordinator.data
        )
        return not last_refresh_success