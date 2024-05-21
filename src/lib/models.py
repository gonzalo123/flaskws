from typing import Dict, Any, Union

from pydantic import BaseModel


class EmitWebsocketRequest(BaseModel):
    channel: str
    body: Union[Dict[str, Any], str]
