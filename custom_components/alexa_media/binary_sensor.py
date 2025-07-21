"""
Alexa Devices Sensors.

SPDX-License-Identifier: Apache-2.0

For more details about this platform, please refer to the documentation at
https://community.home-assistant.io/t/echo-devices-alexa-as-media-player-testers-needed/58639
"""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.exceptions import ConfigEntryNotReady

from . import (
    CONF_EMAIL,
    CONF_EXCLUDE_DEVICES,
    CONF_INCLUDE_DEVICES,
    DATA_ALEXAMEDIA,
    hide_email,
    hide_serial,
)
from .const import CONF_EXTENDED_ENTITY_DISCOVERY
from .helpers import add_devices
from .contact_sensor import ContactSensor
from .motion_sensor import MotionSensor
from .acoustic_event_sensors import (
    BabyCrySensor,
    BeepingApplianceSensor,
    CarbonMonoxideSirenSensor,
    CoughSensor,
    DogBarkSensor,
    GlassBreakSensor,
    HumanPresenceSensor,
    RunningWaterSensor,
    SmokeAlarmSensor,
    SmokeSirenSensor,
    SnoreSensor,
    WaterSoundsSensor,
)

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

    acoustic_event_sensors = []
    acoustic_event_entities = account_dict.get("devices", {}).get("acoustic_event_sensor", [])
    if acoustic_event_entities and account_dict["options"].get(CONF_EXTENDED_ENTITY_DISCOVERY):
        _LOGGER.debug(
            "%s: Found %d acoustic sensors", hide_email(account), len(acoustic_event_entities)
        )
        acoustic_event_sensors = await create_acoustic_event_sensors(
            account_dict, acoustic_event_entities
        )
            
    return await add_devices(
        hide_email(account),
        motion_sensors + contact_sensors + acoustic_event_sensors,
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
        contact_sensor = ContactSensor(coordinator, contact_entity)
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
        motion_sensor = MotionSensor(coordinator, motion_entity["id"], motion_entity["name"], device_info)
        account_dict["entities"]["binary_sensor"].append(motion_sensor)
        devices.append(motion_sensor)
    return devices


def detection_modes():
    """Return a dictionary of detection modes and their corresponding sensor classes."""
    return {
        "babyCry": BabyCrySensor,
        "beepingAppliance": BeepingApplianceSensor,
        "carbonMonoxideSiren": CarbonMonoxideSirenSensor,
        "cough": CoughSensor,
        "dogBark": DogBarkSensor,
        "glassBreak": GlassBreakSensor,
        "humanPresence": HumanPresenceSensor,
        "runningWater": RunningWaterSensor,
        "smokeAlarm": SmokeAlarmSensor,
        "smokeSiren": SmokeSirenSensor,
        "snore": SnoreSensor,
        "waterSounds": WaterSoundsSensor,
    }


async def create_acoustic_event_sensors(account_dict, acoustic_event_entities):
    """Create acoustic event sensors."""
    devices: list[BinarySensorEntity] = []
    coordinator = account_dict["coordinator"]
    detection_mode_dict = detection_modes()
    for acoustic_event_entity in acoustic_event_entities:
        _LOGGER.debug(
            "Creating entity %s for an acoustic event sensor with name %s (%s)",
            hide_serial(acoustic_event_entity["id"]),
            acoustic_event_entity["name"],
            acoustic_event_entity,
        )
        serial = acoustic_event_entity["device_serial"]
        device_info = lookup_device_info(account_dict, serial)
        for detection_mode, sensor_class in detection_mode_dict.items():
            _LOGGER.debug(
                "Creating %s sensor on device %s",
                detection_mode,
                hide_serial(acoustic_event_entity["id"]),
            )
            sensor = sensor_class(coordinator, acoustic_event_entity["id"], acoustic_event_entity["name"], device_info)
            account_dict["entities"]["binary_sensor"].append(sensor)
            devices.append(sensor)
    return devices


def lookup_device_info(account_dict, device_serial):
    """Look up device info for a given device serial."""
    for key, mediaplayer in account_dict["entities"]["media_player"].items():
        if (
            key == device_serial
            and mediaplayer.device_info
            and "identifiers" in mediaplayer.device_info
        ):
            for ident in mediaplayer.device_info["identifiers"]:
                return ident
    return None