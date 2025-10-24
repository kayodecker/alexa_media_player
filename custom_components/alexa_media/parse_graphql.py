import json
from typing import Any
import aiofiles
import asyncio

input_file_path = ""
output_file_path = ""


async def read_json_file(input_file_path: str) -> dict[str, Any]:
    async with aiofiles.open(input_file_path, mode="r", encoding="utf-8") as file:
        content = await file.read()
        data = json.loads(content)
    return data


async def write_details_to_file(details: list[Any], output_file_path: str):
    async with aiofiles.open(output_file_path, "a") as file:
        await file.write(json.dumps(details, indent=2))


async def main():
    data = await read_json_file(input_file_path)
    items = data.get("data", {}).get("endpoints", {}).get("items", None)
    details: list[Any] = []
    for item in items:
        legacyAppliance = item.get("legacyAppliance", None)
        if (
            legacyAppliance is not None
            and legacyAppliance.get("driverIdentity", {}).get("namespace", "")
            != "SKILL"
        ):
            details.append(legacyAppliance)

    if details:
        await write_details_to_file(details, output_file_path)
    print(json.dumps(details, indent=2))


asyncio.run(main())
