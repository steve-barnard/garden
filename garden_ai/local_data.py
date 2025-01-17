import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union
from uuid import UUID

from garden_ai.gardens import Garden
from garden_ai.pipelines import RegisteredPipeline
from garden_ai.utils.misc import garden_json_encoder

LOCAL_STORAGE = Path("~/.garden").expanduser()
LOCAL_STORAGE.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger()


class LocalDataException(Exception):
    """Exception raised when a user's local data.json is corrupted"""

    pass


class ResourceType(Enum):
    GARDEN = "gardens"
    PIPELINE = "pipelines"


def _read_local_db() -> Dict:
    data = {}
    if (LOCAL_STORAGE / "data.json").exists():
        with open(LOCAL_STORAGE / "data.json", "r+") as f:
            raw_data = f.read()
            if raw_data:
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError as e:
                    raise LocalDataException(
                        "Could not parse data.json as valid json"
                    ) from e
    return data


def _write_local_db(data: Dict) -> None:
    contents = json.dumps(data, default=garden_json_encoder)
    with open(LOCAL_STORAGE / "data.json", "w+") as f:
        f.write(contents)


def _store_user_email(email: str) -> None:
    data = _read_local_db()
    data["user_email"] = email
    _write_local_db(data)


def _get_user_email() -> str:
    data = _read_local_db()
    maybe_email = data.get("user_email")
    return str(maybe_email) if maybe_email else "unknown"


def _put_resource_from_metadata(
    resource_metadata: Dict, resource_type: ResourceType
) -> None:
    data = _read_local_db()
    resources = data.get(resource_type.value, {})
    resources[str(resource_metadata["uuid"])] = resource_metadata
    data[resource_type.value] = resources
    _write_local_db(data)


def _put_resource_from_obj(resource: Union[Garden, RegisteredPipeline]) -> None:
    resource_type = (
        ResourceType.GARDEN if isinstance(resource, Garden) else ResourceType.PIPELINE
    )
    resource_metadata = resource.dict()
    _put_resource_from_metadata(resource_metadata, resource_type)


def _make_obj_from_record(
    record: Dict, resource_type: ResourceType
) -> Union[Garden, RegisteredPipeline]:
    if resource_type is ResourceType.GARDEN:
        return Garden(**record)
    else:
        return RegisteredPipeline(**record)


def _get_resource_by_uuid(
    uuid: Union[UUID, str], resource_type: ResourceType
) -> Union[Garden, RegisteredPipeline, None]:
    data = _read_local_db()
    uuid = str(uuid)
    resources = data.get(resource_type.value, {})
    if resources and uuid in resources:
        return _make_obj_from_record(resources[uuid], resource_type)
    else:
        return None


def _get_resource_by_doi(
    doi: str, resource_type: ResourceType
) -> Union[Garden, RegisteredPipeline, None]:
    data = _read_local_db()
    resources_by_uuid = data.get(resource_type.value, {})
    resources_by_doi = _reindex_by_doi(resources_by_uuid)
    if resources_by_doi and doi in resources_by_doi:
        return _make_obj_from_record(resources_by_doi[doi], resource_type)
    else:
        return None


def _reindex_by_doi(resources: dict) -> Dict:
    by_doi = {}
    for resource in resources.values():
        if "doi" in resource:
            by_doi[resource["doi"]] = resource
    return by_doi


def put_local_garden(garden: Garden):
    """Helper: write a record to 'local database' for a given Garden
    Overwrites any existing entry with the same uuid in ~/.garden/data.json.

    Parameters
    ----------
    garden Garden
        The object to json-serialize and write/update in the local database.
        a TypeError will be raised if not a Garden.
    """
    _put_resource_from_obj(garden)


def put_local_garden_from_metadata(garden_metadata: Dict):
    """Helper: write a record to 'local database' for a given Garden
    Overwrites any existing entry with the same uuid in ~/.garden/data.json.

    Parameters
    ----------
    garden_metadata Dict
        Dictionary in the format serialized by the Garden Pydantic model.
    """
    _put_resource_from_metadata(garden_metadata, ResourceType.GARDEN)


def put_local_pipeline(pipeline: RegisteredPipeline):
    """Helper: write a record to 'local database' for a given Pipeline
    Overwrites any existing entry with the same uuid in ~/.garden/data.json.

    Parameters
    ----------
    pipeline Pipeline
        The object to json-serialize and write/update in the local database.
        a TypeError will be raised if not a Pipeline.
    """
    _put_resource_from_obj(pipeline)


def get_local_garden_by_uuid(uuid: Union[UUID, str]) -> Optional[Garden]:
    """Helper: fetch a Garden record from ~/.garden/data.json.

    Parameters
    ----------
    uuid Union[UUID, str]
        The uuid of the Garden you are fetching.

    Returns
    -------
    Optional[Garden]
        If successful, a dictionary in the form given by Garden.json().
    """
    return _get_resource_by_uuid(uuid, ResourceType.GARDEN)  # type: ignore


def get_local_pipeline_by_uuid(uuid: Union[UUID, str]) -> Optional[RegisteredPipeline]:
    """Helper: fetch a Pipeline record from ~/.garden/data.json.

    Parameters
    ----------
    uuid Union[UUID, str]
        The uuid of the Pipeline you are fetching.

    Returns
    -------
    Optional[RegisteredPipeline]
    """
    return _get_resource_by_uuid(uuid, ResourceType.PIPELINE)  # type: ignore


def get_local_garden_by_doi(doi: str) -> Optional[Garden]:
    """Helper: fetch a Garden record from ~/.garden/data.json.

    Parameters
    ----------
    doi str
        The doi of the Garden you are fetching.

    Returns
    -------
    Optional[Garden]
    """
    return _get_resource_by_doi(doi, ResourceType.GARDEN)  # type: ignore


def get_local_pipeline_by_doi(doi: str) -> Optional[RegisteredPipeline]:
    """Helper: fetch a Pipeline record from ~/.garden/data.json.

    Parameters
    ----------
    doi str
        The doi of the Pipeline you are fetching.

    Returns
    -------
    Optional[RegisteredPipeline]
    """
    return _get_resource_by_doi(doi, ResourceType.PIPELINE)  # type: ignore
