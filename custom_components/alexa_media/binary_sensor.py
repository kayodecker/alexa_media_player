"""
Alexa Devices Sensors.

SPDX-License-Identifier: Apache-2.0

For more details about this platform, please refer to the documentation at
https://community.home-assistant.io/t/echo-devices-alexa-as-media-player-testers-needed/58639
"""

import datetime
import logging
from typing import Optional

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import (
    CONF_EMAIL,
    CONF_EXCLUDE_DEVICES,
    CONF_INCLUDE_DEVICES,
    DATA_ALEXAMEDIA,
    hide_email,
    hide_serial,
)
from .alexa_entity import parse_detection_state_from_coordinator
from .const import CONF_EXTENDED_ENTITY_DISCOVERY
from .helpers import add_devices

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Alexa sensor platform."""
    account = None
    if config:
        account = config.get(CONF_EMAIL)
    if account is None and discovery_info:
        account = discovery_info.get("config", {}).get(CONF_EMAIL)
    if account is None:
        raise ConfigEntryNotReady
    account_dict = hass.data[DATA_ALEXAMEDIA]["accounts"][account]
    include_filter = config.get(CONF_INCLUDE_DEVICES, [])
    exclude_filter = config.get(CONF_EXCLUDE_DEVICES, [])
    _LOGGER.debug("%s: Loading binary sensors", hide_email(account))

    motion_sensors = []
    motion_entities = account_dict.get("devices", {}).get("motion_sensor", [])
    if motion_entities and account_dict["options"].get(CONF_EXTENDED_ENTITY_DISCOVERY):
        motion_sensors = await create_motion_sensors(
            account_dict, motion_entities
        )

    contact_sensors = []
    contact_entities = account_dict.get("devices", {}).get("contact_sensor", [])
    if contact_entities and account_dict["options"].get(CONF_EXTENDED_ENTITY_DISCOVERY):
        contact_sensors = await create_contact_sensors(
            account_dict, contact_entities
        )
            
    return await add_devices(
        hide_email(account),
        motion_sensors + contact_sensors,
        add_devices_callback,
        include_filter,
        exclude_filter,
    )


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Alexa sensor platform by config_entry."""
    return await async_setup_platform(
        hass, config_entry.data, async_add_devices, discovery_info=None
    )


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    account = entry.data[CONF_EMAIL]
    account_dict = hass.data[DATA_ALEXAMEDIA]["accounts"][account]
    _LOGGER.debug("Attempting to unload binary sensors")
    for binary_sensor in account_dict["entities"]["binary_sensor"]:
        await binary_sensor.async_remove()
    return True


async def create_contact_sensors(account_dict, contact_entities):
    """Create contact sensors."""
    devices: list[BinarySensorEntity] = []
    coordinator = account_dict["coordinator"]
    for contact_entity in contact_entities:
        _LOGGER.debug(
            "Creating entity %s for a contact sensor with name %s (%s)",
            hide_serial(contact_entity["id"]),
            contact_entity["name"],
            contact_entity,
        )
        contact_sensor = AlexaContact(coordinator, contact_entity)
        account_dict["entities"]["binary_sensor"].append(contact_sensor)
        devices.append(contact_sensor)
    return devices


async def create_motion_sensors(account_dict, motion_entities):
    """Create motion sensors."""
    devices: list[BinarySensorEntity] = []
    coordinator = account_dict["coordinator"]
    for motion_entity in motion_entities:
        _LOGGER.debug(
            "Creating entity %s for a motion sensor with name %s (%s)",
            hide_serial(motion_entity["id"]),
            motion_entity["name"],
            motion_entity,
        )
        serial = motion_entity["device_serial"]
        device_info = lookup_device_info(account_dict, serial)
        motion_sensor = AlexaMotion(coordinator, motion_entity["id"], motion_entity["name"], device_info)
        account_dict["entities"]["binary_sensor"].append(motion_sensor)
        devices.append(motion_sensor)
    return devices


def lookup_device_info(account_dict, device_serial):
    """Get the device to use for a given Echo based on a given device serial id.

    This may return nothing as there is no guarantee that a given temperature sensor is actually attached to an Echo.
    """
    for key, mediaplayer in account_dict["entities"]["media_player"].items():
        if (
            key == device_serial
            and mediaplayer.device_info
            and "identifiers" in mediaplayer.device_info
        ):
            for ident in mediaplayer.device_info["identifiers"]:
                return ident
    return None


class AlexaContact(CoordinatorEntity, BinarySensorEntity):
    """A contact sensor controlled by an Echo."""

    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, coordinator: CoordinatorEntity, details: dict):
        """Initialize alexa contact sensor.

        Args
            coordinator (CoordinatorEntity): Coordinator
            details (dict): Details dictionary

        """
        super().__init__(coordinator)
        self.alexa_entity_id = details["id"]
        self._name = details["name"]

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

        return detection == "DETECTED" if detection is not None else None

    @property
    def assumed_state(self) -> bool:
        """Return assumed state."""
        last_refresh_success = (
            self.coordinator.data and self.alexa_entity_id in self.coordinator.data
        )
        return not last_refresh_success


class AlexaMotion(CoordinatorEntity, BinarySensorEntity):
    """A motion sensor controlled by an Echo."""

    def __init__(self, coordinator, entity_id, name, media_player_device_id):
        """Initialize alexa motion sensor."""
        super().__init__(coordinator)
        self.alexa_entity_id = entity_id
        self._attr_unique_id = entity_id + "_motion"
        self._attr_name = name + " Motion"
        self._attr_device_class = BinarySensorDeviceClass.MOTION
        detection_state: Optional[datetime.datetime] = (
            parse_detection_state_from_coordinator(coordinator, entity_id, "Alexa.MotionSensor")
        )
        self._attr_is_on = self._get_detection_state(detection_state)
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        detection_state = parse_detection_state_from_coordinator(
            self.coordinator, self.alexa_entity_id, "Alexa.MotionSensor"
        )
        self._attr_is_on = self._get_detection_state(detection_state)
        _LOGGER.debug(
            "Coordinator update: %s: %s",
            self._attr_name,
            self._attr_is_on,
        )
        super()._handle_coordinator_update()

    def _get_detection_state(self, detection_state):
        _LOGGER.debug("MotionSensor value: %s", detection_state)
        return detection_state == "DETECTED" if detection_state is not None else None

    @property
    def is_on(self):
        """Return whether on."""
        detection = parse_detection_state_from_coordinator(
            self.coordinator, self.alexa_entity_id, "Alexa.MotionSensor"
        )

        return detection == "DETECTED" if detection is not None else None
