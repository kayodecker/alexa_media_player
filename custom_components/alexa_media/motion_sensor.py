""" Alexa Media Player Motion Sensor
This module defines a motion sensor entity that can be controlled by an Echo device.
It inherits from CoordinatorEntity and BinarySensorEntity to integrate with Home Assistant.
"""

import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .alexa_entity import parse_detection_state_from_coordinator

_LOGGER = logging.getLogger(__name__)

class MotionSensor(CoordinatorEntity, BinarySensorEntity):
    """A motion sensor controlled by an Echo."""

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa motion sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        detection_state = (
            parse_detection_state_from_coordinator(coordinator, entity_id, "Alexa.MotionSensor")
        )
        self._attr_is_on = self._get_detection_state(detection_state)
        self._attr_unique_id = f"{entity_id}_motion"
        self._attr_name = name + " Motion"
        self._attr_device_class = BinarySensorDeviceClass.MOTION
        _LOGGER.debug(
            "Coordinator init: %s: %s",
            self._attr_name,
            self._attr_is_on,
        )
        self._attr_device_info = (
            {
                "identifiers": {media_player_device_id},
                "via_device": media_player_device_id,
            }
            if media_player_device_id
            else None
        )

    def _get_detection_state(self, detection_state):
        return detection_state == "DETECTED"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        detection_state = parse_detection_state_from_coordinator(
            self.coordinator, self.alexa_entity_id, "Alexa.MotionSensor"
        )
        if detection_state is None:
            return
        _LOGGER.debug("MotionSensor value: %s", detection_state)
        if detection_state not in ["DETECTED", "NOT_DETECTED"]:
            self._attr_is_on = False
        else:
            self._attr_is_on = self._get_detection_state(detection_state)
            _LOGGER.debug(
                "Coordinator update: %s: %s",
                self._attr_name,
                self._attr_is_on,
            )
        super()._handle_coordinator_update()

    @property
    def is_on(self):
        """Return whether on."""
        return self._attr_is_on
