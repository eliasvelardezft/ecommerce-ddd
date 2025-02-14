from pydantic import BaseModel


class RegisterCustomerCommand(BaseModel):
    name: str
    email: str
