import re
from enum import Enum
from ldap3.core.exceptions import LDAPAttributeError
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Iterable, Optional, Union


""" ######################################################### """
""" ******************* TINY LDAP3 MODELS ******************* """
""" ######################################################### """


LDAP_COMPUTER_DETAIL_RETURNED_ATTRS_TUPLE = (
    "cn",
    "description",
    "distinguishedName",
    "lastLogon",
    "logonCount",
    "name",
    "objectGUID",
    "operatingSystem",
    "operatingSystemVersion",
    "sAMAccountName",
    "sAMAccountType",
    "servicePrincipalName",
    "whenChanged",
    "whenCreated",
)
LDAP_COMPUTER_SEARCH_RETURNED_ATTRS_TUPLE = (
    "cn",
    "operatingSystem",
    "operatingSystemVersion",
    "whenChanged",
    "whenCreated",
)

LDAP_GROUP_DETAIL_RETURNED_ATTRS_TUPLE = (
    "cn",
    "description",
    "distinguishedName",
    "mail",
    "member",
    "memberOf",
    "name",
    "objectGUID",
    "sAMAccountName",
    "sAMAccountType",
    "whenChanged",
    "whenCreated",
)
LDAP_GROUP_SEARCH_RETURNED_ATTRS_TUPLE = (
    "distinguishedName",
    "mail",
    "sAMAccountName",
    "whenChanged",
    "whenCreated",
)

LDAP_PERSON_AUTH_RETURNED_ATTRS_TUPLE = (
    "cn",
    "employeeNumber",
    "ipPhone",
    "mail",
    "mobile",
    "userPrincipalName",
    "sAMAccountName",
)
# returned_attrs_collection = ["*"] doesn't contain: "msDS-UserPasswordExpiryTimeComputed" attr
LDAP_PERSON_DETAIL_RETURNED_ATTRS_TUPLE = (
    "accountExpires",
    "badPasswordTime",
    "badPwdCount",
    "cn",
    "company",
    "department",
    "displayName",
    "employeeID",
    "employeeNumber",
    "extensionAttribute12",
    "extensionAttribute5",
    "extensionAttribute6",
    "extensionAttribute9",
    "ipPhone",
    "l",
    "lastLogoff",
    "lastLogon",
    "lockoutTime",
    "logonCount",
    "mail",
    "manager",
    "memberOf",
    "mobile",
    "msDS-UserPasswordExpiryTimeComputed",
    "msExchExtensionAttribute22",
    "msExchExtensionAttribute23",
    "msExchExtensionCustomAttribute1",
    "msExchExtensionCustomAttribute2",
    "objectGUID",
    "pwdLastSet",
    "sAMAccountName",
    "sAMAccountType",
    "servicePrincipalName",
    "streetAddress",
    "telephoneNumber",
    "thumbnailPhoto",
    "title",
    "userAccountControl",
    "userPrincipalName",
    "whenChanged",
    "whenCreated",
)
LDAP_PERSON_SEARCH_BY_ATTRS_TUPLE = (
    "cn",
    "employeeNumber",
    "ipPhone",
    "mail",
    "mobile",
    "sAMAccountName",
)
LDAP_PERSON_SEARCH_RETURNED_ATTRS_TUPLE = (
    "department",
    "displayName",
    "employeeNumber",
    "ipPhone",
    "mail",
    "mobile",
    "sAMAccountName",
    "title",
    "userAccountControl",
    "whenChanged",
    "whenCreated",
)

ldap_objects_returned_attrs_schema = {
    "computer": {
        "detail": LDAP_COMPUTER_DETAIL_RETURNED_ATTRS_TUPLE,
        "search": LDAP_COMPUTER_SEARCH_RETURNED_ATTRS_TUPLE,
    },
    "group": {
        "detail": LDAP_GROUP_DETAIL_RETURNED_ATTRS_TUPLE,
        "search": LDAP_GROUP_SEARCH_RETURNED_ATTRS_TUPLE,
    },
    "person": {
        "detail": LDAP_PERSON_DETAIL_RETURNED_ATTRS_TUPLE,
        "search": LDAP_PERSON_SEARCH_RETURNED_ATTRS_TUPLE,
    }
}

# Fullmatch, no symbols !#$%&'*+/=?^_`{|}~- and no first '\"' after '^(?:[a-z0-9]+(?:\.[a-z0-9]+)*|'
ldap_upn_regex_rfc822based = re.compile(
    r"""^(?:[a-z0-9]+(?:\.[a-z0-9]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")
    @(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|
    \[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}
    (?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|
    \\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$""", re.X
)


class LdapObjectsCategoriesEnum(str, Enum):
    person = "person"
    group = "group"
    computer = "computer"


class LdapBaseModel(BaseModel):
    method_type: str = Field(exclude=True)
    object_category: LdapObjectsCategoriesEnum
    returned_attrs_collection: Optional[Union[Iterable[str], None]] = None

    @model_validator(mode="before")
    def _set_returned_attrs_field(cls, values: dict) -> dict:
        if not values["returned_attrs_collection"]:
            values["returned_attrs_collection"] = (
                ldap_objects_returned_attrs_schema)[values["object_category"]][values["method_type"]]

        # Add 'order_by' attribute to returned_attrs_collection
        returned_attrs_list = list(values["returned_attrs_collection"])
        match values["method_type"]:
            case "detail":
                if values["attr_name"] not in returned_attrs_list:
                    returned_attrs_list.append(values["attr_name"])
            case "search":
                if values["order_by"] not in returned_attrs_list:
                    returned_attrs_list.append(values["order_by"])
        values["returned_attrs_collection"] = tuple(returned_attrs_list)

        return values


class LdapObjectDetailModel(LdapBaseModel):
    attr_name: str = Field(min_length=1)
    attr_value: str = Field(min_length=1)


class LdapObjecsSearchModel(LdapBaseModel):
    attr_value: str = Field(min_length=1)
    order_by: str = Field(min_length=1)
    search_by_attrs_collection: Optional[Union[Iterable[str], None]] = None

    @model_validator(mode="before")
    def _set_search_by_attrs_field(cls, values: dict) -> dict:
        if values["object_category"] == "person" and not values["search_by_attrs_collection"]:
            values["search_by_attrs_collection"] = LDAP_PERSON_SEARCH_BY_ATTRS_TUPLE
        return values


class LdapPersonAuthModel(BaseModel):
    login: str
    password: str = Field(min_length=8)
    returned_attrs_collection: Optional[Union[Iterable[str], None]] = None

    @model_validator(mode="before")
    def _set_returned_attrs_field(cls, values: dict) -> dict:
        if not values["returned_attrs_collection"]:
            values["returned_attrs_collection"] = LDAP_PERSON_AUTH_RETURNED_ATTRS_TUPLE
        return values

    @field_validator("login")
    def _check_upn(cls, value) -> str:
        if not re.fullmatch(ldap_upn_regex_rfc822based, value):
            raise LDAPAttributeError("Doesn't match the format of the 'userPrincipalName' attribute.")
        return value
