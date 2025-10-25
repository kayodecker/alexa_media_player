"""
Alexa Media Player Acoustic Event Sensors
These sensors are used to detect various acoustic events such as baby cries, dog barks, and more.
Each sensor is represented by a class that inherits from CoordinatorEntity and BinarySensorEntity.
"""

import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import STATE_UNAVAILABLE

from .alexa_entity import parse_acoustic_event_from_coordinator

_LOGGER = logging.getLogger(__name__)

# Base class for Alexa acoustic event sensors
# This class provides common functionality for all acoustic event sensors.
class AcousticEventSensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Alexa acoustic event sensors."""

    detection_mode: str = None  # Should be set by subclasses
    detection_state_key: str = None  # Will be derived from detection_mode

    def _get_detection_state(self, detection_state):
        return detection_state == "DETECTED"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.detection_mode:
            _LOGGER.error("Detection mode not set for %s", self._attr_name)
            return
        self.detection_state_key = self.detection_mode + "DetectionState"
        if not self.available:
            return STATE_UNAVAILABLE
        detection_state = parse_acoustic_event_from_coordinator(
            self.coordinator, self.alexa_entity_id, self.detection_state_key
        )
        if detection_state is None:
            return
        _LOGGER.debug("%s value: %s", self.detection_state_key, detection_state)
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
    
    @property
    def available(self) -> bool:
        """Return the availability of the client."""
        overallMode = parse_acoustic_event_from_coordinator(
            self.coordinator, self.alexa_entity_id, "overallMode"
        )
        if overallMode != "ENABLED":
            return False
        
        detectionModes = parse_acoustic_event_from_coordinator(
            self.coordinator, self.alexa_entity_id, "detectionModes"
        )
        overallMode = detectionModes.get(self.detection_mode, {}).get("overallMode")
        _LOGGER.debug("Detection mode %s for %s: %s", self.detection_mode, self.alexa_entity_id, overallMode)
        return overallMode == "ENABLED"


# Sensor classes for specific acoustic events
class BabyCrySensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "babyCry"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_baby_cry"
        self._attr_name = name + " Baby Cry"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:baby"
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
        

class BeepingApplianceSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "beepingAppliance"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_beeping_appliance"
        self._attr_name = name + " Beeping Appliance"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:alert"
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


class CarbonMonoxideSirenSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "carbonMonoxideSiren"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_carbon_monoxide_siren"
        self._attr_name = name + " Carbon Monoxide Siren"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:alert-octagon"
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
        

class CoughSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "cough"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_cough"
        self._attr_name = name + " Cough"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:emoticon-frown"
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
        

class DogBarkSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "dogBark"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_dog_bark"
        self._attr_name = name + " Dog Bark"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:dog"
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
        

class GlassBreakSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "glassBreak"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_glass_break"
        self._attr_name = name + " Glass Break"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:glass-fragile"
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
        

class HumanPresenceSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "humanPresence"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_human_presence"
        self._attr_name = name + " Human Presence"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:human"
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
        

class RunningWaterSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "runningWater"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_running_water"
        self._attr_name = name + " Running Water"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:water"
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
        

class SmokeAlarmSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "smokeAlarm"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_smoke_alarm"
        self._attr_name = name + " Smoke Alarm"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:smoke-detector"
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
        

class SmokeSirenSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "smokeSiren"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_smoke_siren"
        self._attr_name = name + " Smoke Siren"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:smoke-detector"
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
        

class SnoreSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "snore"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_snore"
        self._attr_name = name + " Snore"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:sleep"
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
        

class WaterSoundsSensor(AcousticEventSensorBase):
    """An acoustic event sensor controlled by an Echo."""

    detection_mode: str = "waterSounds"

    def __init__(
        self,
        coordinator: CoordinatorEntity,
        entity_id: str,
        name: str,
        media_player_device_id: Optional[str],
    ):
        """Initialize alexa acoustic event sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        value = parse_acoustic_event_from_coordinator(
            coordinator, entity_id, self.detection_state_key
        )
        self._attr_is_on = self._get_detection_state(value)
        self._attr_unique_id = f"{entity_id}_water_sounds"
        self._attr_name = name + " Water Sounds"
        self._attr_device_class = BinarySensorDeviceClass.SOUND
        self._attr_icon = "mdi:water"
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