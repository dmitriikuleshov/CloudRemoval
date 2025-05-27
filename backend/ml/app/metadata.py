from typing import Any, Dict, Tuple

from dataclasses import dataclass, field

from common.models.storage import Entry


@dataclass
class RequestMetadata:
    entry: Entry
    source_keys: Tuple
    result_key: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
