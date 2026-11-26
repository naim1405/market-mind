from pydantic import BaseModel, EmailStr


class FacebookPageSchema(BaseModel):
    id: str
    name: str
    access_token: str


class FacebookCursorsSchema(BaseModel):
    before: str
    after: str


class FacebookPagingSchema(BaseModel):
    cursors: FacebookCursorsSchema


class FacebookAccountsSchema(BaseModel):
    data: list[FacebookPageSchema]
    paging: FacebookPagingSchema | None = None


class FacebookUserSchema(BaseModel):
    id: str
    name: str | None = None
    email: EmailStr | None = None
    accounts: FacebookAccountsSchema | None = None


class FacebookCodeVerifyResponseSchema(BaseModel):
    access_token: str
    token_type: str


class FacebookAccount(BaseModel):
    id: str
    name: str
    access_token: str


class FacebookPagingCursors(BaseModel):
    before: str
    after: str


class FacebookPaging(BaseModel):
    cursors: FacebookPagingCursors


class FacebookAccounts(BaseModel):
    data: list[FacebookAccount]
    paging: FacebookPaging


class FacebookUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    accounts: FacebookAccounts


class FacebookGetUserResponse(BaseModel):
    message: str
    user: FacebookUser
