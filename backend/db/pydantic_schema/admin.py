from pydantic import BaseModel

class CreateCode(BaseModel):
    new_code_identifier: str


class CreateCodeResponse(BaseModel):
    code: str
    used: bool
    identifier: str | None
    creation_code: bool
    join_code: bool
    admin_code: bool
    team_related: str | None
