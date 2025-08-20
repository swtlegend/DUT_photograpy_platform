from pydantic import BaseModel, field_validator
from typing import Any, Dict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    id_number: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        # 在Pydantic v2中，我们需要通过info.data访问其他字段的值
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('密码和确认密码不一致')
        return v