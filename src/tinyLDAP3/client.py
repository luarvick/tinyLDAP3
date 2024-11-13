import datetime
from ldap3 import (
    ALL,
    AUTO_BIND_DEFAULT,
    ROUND_ROBIN,
    SUBTREE,
    AttrDef,
    Connection,
    ObjectDef,
    Reader,
    Server,
    ServerPool
)
from typing import Any, Union, Iterable

from .decorators import ldap_logging
from .exceptions import LdapBoundError
from .logger import logger
from .models import LdapObjectDetailModel, LdapObjecsSearchModel, LdapPersonAuthModel


""" ######################################################### """
""" ******************* TINY LDAP3 CLIENT ******************* """
""" ######################################################### """


class tinyLDAP3Client:

    """
        tinyLDAP3 Client. Wrapper for Python `ldap3` Package.
        """

    def __init__(self, **kwargs):
        super(tinyLDAP3Client, self).__init__()

        self._search_limit = 1000

        self._connect_timeout = kwargs.get("connect_timeout") or 10
        self._receive_timeout = kwargs.get("receive_timeout") or 10

        self.__user_dn = kwargs.get("user_dn")
        self.__user_pass = kwargs.get("user_pass")
        self.__search_base = kwargs.get("search_base") or SUBTREE
        self.__server_pool = ServerPool(
            [
                Server(
                    host, port=636, use_ssl=True, get_info=ALL, connect_timeout=self._connect_timeout
                ) for host in kwargs.get("hosts")
            ],
            ROUND_ROBIN,
            active=False,
            exhaust=False
        )

    def __ldap_entries(self, search_query: str, returned_attrs_collection: Iterable[str]) -> list:

        """
        Get entries via connection context manager.
        :param returned_attrs_collection:   Collection of Returned Attributes
        :return:
        """

        message = "@ LDAP Entries @ - {msg}"

        # 'conn' example: "{ldap_uri} - ssl - user: {ldap_user} - not lazy - \
        # bound - open - <local: {local_ip}:{local_port} - remote: {ldap_ip}:{ldap_port}> - \
        # tls not started - listening - SyncStrategy - internal decoder"
        with Connection(
            self.__server_pool,
            raise_exceptions=True,
            auto_bind=AUTO_BIND_DEFAULT,
            user=self.__user_dn,
            password=self.__user_pass,
            return_empty_attributes=True,
            receive_timeout=self._receive_timeout
        ) as conn:
            # 'conn.bound' - The status of the LDAP session (True / False)
            if conn.bound:
                conn.search(
                    search_base=self.__search_base,
                    search_filter=search_query,
                    search_scope=SUBTREE,
                    size_limit=self._search_limit,
                    attributes=returned_attrs_collection
                )
                return conn.entries
            logger.error(message.format(msg=f"Error Detail: {repr(conn)}."))
            raise LdapBoundError("Bound error occurred.")

    def __ldap_reader(self, object_category: Iterable[str], dn: str) -> Reader:

        """
        Get reader via connection context manager.
        :param object_category:             Object Categories & Classes Collection
        :param dn:                          Object `distinguishedName` Attribute Value
        :return:
        """

        message = "@ LDAP Reader @ - {msg}"

        with Connection(
            self.__server_pool,
            raise_exceptions=True,
            auto_bind=AUTO_BIND_DEFAULT,
            user=self.__user_dn,
            password=self.__user_pass,
            return_empty_attributes=True,
            receive_timeout=self._receive_timeout
        ) as conn:
            # 'conn.bound' - The status of the LDAP session (True / False)
            if conn.bound:
                object_def = ObjectDef(object_category, conn)
                if any(value in object_category for value in ["computer", "group", "person", "user"]):
                    object_def += AttrDef("sAMAccountName")
                return Reader(connection=conn, object_def=object_def, base=dn)
            logger.error(message.format(msg=f"Error Detail: {repr(conn)}."))
            raise LdapBoundError("Bound error occurred.")

    def __ldap_object_detail_query_selector(
            self,
            object_category: str,
            attr_name: str,
            attr_value: str,
            is_active: bool
    ) -> str:

        """
        Object (`Person`, `Group` or `Computer`) detail query selector.
        :param object_category:             Object Category: `Person`, `Group` or `Computer`
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :param is_active:                   Person (User) Search Scope (Active or All Users)
        :return:
        """

        match object_category:
            case "computer":
                search_query = self.__ldap_computer_detail_query(attr_name=attr_name, attr_value=attr_value)
            case "group":
                search_query = self.__ldap_group_detail_query(attr_name=attr_name, attr_value=attr_value)
            case _:
                # Person
                search_query = self.__ldap_person_detail_all_users_query(attr_name=attr_name, attr_value=attr_value)
                if is_active:
                    search_query = self.__ldap_person_detail_active_users_query(
                        attr_name=attr_name, attr_value=attr_value
                    )
        return search_query

    def __ldap_objects_search_query_selector(
            self,
            object_category: str,
            attr_value: str,
            search_by_attrs_collection: Iterable[str]
    ) -> str:

        """
        Objects (`Person`, `Group` or `Computer`) search query selector.
        :param object_category:             Object Category: `Person`, `Group` or `Computer`
        :param attr_value:                  Attributes Value for Searching
        :param search_by_attrs_collection:  Searching for Person (User) Based on Attributes from the Collection
        :return:
        """

        match object_category:
            case "computer":
                search_query = self.__ldap_computers_search_query(attr_value=attr_value)
            case "group":
                search_query = self.__ldap_groups_search_query(attr_value=attr_value)
            case _:
                # Person
                search_query = self.__ldap_persons_search_query(
                    attr_value=attr_value, search_by_attrs_collection=search_by_attrs_collection
                )
        return search_query

    @staticmethod
    def __ldap_computer_detail_query(attr_name: str, attr_value: str) -> str:

        """
        Computer detail query. Strict match.
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :return:
        """

        return f"""(
            &(objectCategory=Computer)
            (!(objectCategory=Group))
            (!(objectCategory=Person))
            ({attr_name}={attr_value})
        )"""

    @staticmethod
    def __ldap_computers_search_query(attr_value: str) -> str:

        """
        Computers search query.
        :param attr_value:                  Attributes Value for Searching by `cn`
        :return:
        """

        return f"(&(objectCategory=Computer)(!(objectCategory=Group))(!(objectCategory=Person))(cn=*{attr_value}*))"

    @staticmethod
    def __ldap_group_detail_query(attr_name: str, attr_value: str) -> str:

        """
        Group detail query. Strict match.
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :return:
        """

        return f"""(
            &(objectCategory=Group)
            (!(objectCategory=Computer))
            (!(objectCategory=Person))
            ({attr_name}={attr_value})
        )"""

    @staticmethod
    def __ldap_groups_search_query(attr_value: str) -> str:

        """
        Groups search query.
        :param attr_value:                  Attributes Value for Searching by `cn`
        :return:
        """

        return f"(&(objectCategory=Group)(!(objectCategory=Computer))(!(objectCategory=Person))(cn=*{attr_value}*))"

    @staticmethod
    def __ldap_person_detail_active_users_query(attr_name: str, attr_value: str) -> str:

        """
        Person detail active users query. Strict match.
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :return:
        """

        return f"""(
            &(objectCategory=Person)(objectClass=User)
            (!(UserAccountControl:1.2.840.113556.1.4.803:=2))
            (!(objectCategory=Computer))
            (!(objectCategory=Group))
            ({attr_name}={attr_value})
        )"""

    @staticmethod
    def __ldap_person_detail_all_users_query(attr_name: str, attr_value: str) -> str:

        """
        Person detail all users query. Strict match.
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :return:
        """

        return f"""(
            &(objectCategory=Person)(objectClass=User)
            (!(objectCategory=Computer))
            (!(objectCategory=Group))
            ({attr_name}={attr_value})
        )"""

    @staticmethod
    def __ldap_persons_search_query(attr_value: str, search_by_attrs_collection: Iterable[str]) -> str:

        """
        Persons search query.
        :param attr_value:                  Attributes Value for Searching
        :param search_by_attrs_collection:  Searching for Person (User) Based on Attributes from the Collection
        :return:
        """

        search_filter = "".join([f"({attr_name}={attr_value}*)" for attr_name in search_by_attrs_collection])
        return f"""(
            &(objectCategory=Person)(objectClass=User)
            (!(objectCategory=Computer))
            (!(objectCategory=Group))
            (|{search_filter})
        )"""

    @staticmethod
    def pwd_expiration(attr_value: int) -> datetime:

        """
        Normalization of the `msDS-UserPasswordExpiryTimeComputed` attribute.
        :param attr_value:                  `msDS-UserPasswordExpiryTimeComputed` Attribute Value
        :return:
        """

        # January 1, 1970 as MS file time
        jan_1970 = 116444736000000000
        us = (attr_value - jan_1970) // 10

        # us = 910692730085477580   - Password Doesn't Expiry Account -> OverflowError
        # us = 1622438419382306     - Normal Account
        try:
            expiration_date = datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=us)
        except OverflowError:
            expiration_date = datetime.datetime.strptime("9999-12-31", "%Y-%m-%d")
        return expiration_date

    @staticmethod
    def sat_description(sat_value: int) -> str:

        """
        Description of the `sAMAccountType` attribute.
        :param sat_value:                   `sAMAccountType` Attribute Value
        :return:
        """

        sat_value_schema = {
            0: "SAM_DOMAIN_OBJECT",
            268435456: "SAM_GROUP_OBJECT",
            268435457: "SAM_NON_SECURITY_GROUP_OBJECT",
            536870912: "SAM_ALIAS_OBJECT",
            536870913: "SAM_NON_SECURITY_ALIAS_OBJECT",
            805306368: "SAM_NORMAL_USER_ACCOUNT",
            805306369: "SAM_MACHINE_ACCOUNT",
            805306370: "SAM_TRUST_ACCOUNT",
            1073741824: "SAM_APP_BASIC_GROUP",
            1073741825: "SAM_APP_QUERY_GROUP",
            2147483647: "SAM_ACCOUNT_TYPE_MAX",
        }
        return sat_value_schema[sat_value] if sat_value in sat_value_schema.keys() else "sAMAccountType Unknown"

    @staticmethod
    def uac_description(uac_value: int) -> str:

        """
        Description of the `userAccountControl` attribute.
        :param uac_value:               `userAccountControl` Attribute Value
        :return:
        """

        uac_value_schema = {
            512: "Normal Account",
            514: "Disabled Account",
            544: "Enabled, Password Not Required",
            546: "Disabled, Password Not Required",
            66048: "Enabled, Password Doesn't Expire",
            66050: "Disabled, Password Doesn't Expire",
            66082: "Disabled, Password Doesn't Expire & Not Required",
            262656: "Enabled, Smartcard Required",
            262658: "Disabled, Smartcard Required",
            262690: "Disabled, Smartcard Required, Password Not Required",
            328194: "Disabled, Smartcard Required, Password Doesn't Expire",
            328226: "Disabled, Smartcard Required, Password Doesn't Expire & Not Required",
            2163200: "Enabled, Password Doesn't Expire, Use Des Key Only"
        }
        return uac_value_schema[uac_value] if uac_value in uac_value_schema.keys() else "userAccountControl Unknown"

    @ldap_logging
    def object_detail(
            self,
            object_category: str,
            attr_name: str,
            attr_value: str,
            is_active: bool = False,
            returned_attrs_collection: Iterable[str] = None
    ) -> Union[dict[str, Any], tuple[dict, ...], None]:

        """
        Object (`Person`, `Group` or `Computer`) detail method will return an Object dictionary or a collection of
        Objects dictionaries.
        :param object_category:             Object Category: `Person`, `Group` or `Computer`
        :param attr_name:                   Attribute Name for Searching
        :param attr_value:                  Attributes Value for Searching
        :param is_active:                   Person (User) Search Scope (Active or All Users)
        :param returned_attrs_collection:   Collection of Returned Attributes or None
        :return:
        """

        message = \
            f"@ LDAP Object Detail @ - 'ObjectCategory: `{object_category}`, AttrName: `{attr_name}`, Value: `{attr_value}`' - {{msg}}"

        validated_data = LdapObjectDetailModel(
            **{
                "method_type": "detail",
                "object_category": object_category.lower(),
                "attr_name": attr_name,
                "attr_value": attr_value,
                "returned_attrs_collection": returned_attrs_collection
            }
        ).model_dump()
        search_query = self.__ldap_object_detail_query_selector(
            object_category=validated_data["object_category"],
            attr_name=validated_data["attr_name"],
            attr_value=validated_data["attr_value"],
            is_active=is_active
        )
        # Object Detail request
        resp_raw = self.__ldap_entries(
            search_query=search_query,
            returned_attrs_collection=tuple(validated_data["returned_attrs_collection"])
        )
        if resp_raw:
            if len(resp_raw) == 1:
                return {attr.key: attr.value for attr in resp_raw[0]}
            else:
                logger.warning(
                    message.format(msg="More than one LDAP Object were found. Use attributes with unique values.")
                )
                return tuple(
                    sorted(
                        [{attr.key: attr.value for attr in item} for item in resp_raw],
                        key=lambda item: item[validated_data["attr_name"]]
                    )
                )
        logger.warning(message.format(msg="LDAP Object not found."))
        return None

    @ldap_logging
    def object_read(
            self,
            object_category: Iterable[str],
            dn: str,
            returned_attrs_collection: Iterable[str] = None
    ) -> Union[dict[str, Any], tuple[dict, ...], None]:

        """
        Object (Any Category or Class) read method will return an Object dictionary or a collection of
        Objects dictionaries.
        :param object_category:             Object Categories & Classes Collection
        :param dn:                          Object `distinguishedName` Attribute Value
        :param returned_attrs_collection:   Collection of Returned Attributes or None
        :return:
        """

        message = f"@ LDAP Object Read @ - 'ObjectCategory: `{object_category}`, DN: `{dn}`' - {{msg}}"

        resp_raw = self.__ldap_reader(object_category, dn).search(attributes=returned_attrs_collection)
        if resp_raw:
            if len(resp_raw) == 1:
                return {attr.key: attr.value for attr in resp_raw[0]}
            else:
                return tuple([{attr.key: attr.value for attr in item} for item in resp_raw])
        logger.warning(message.format(msg="LDAP Object not found."))
        return None

    @ldap_logging
    def objects_search(
            self,
            object_category: str,
            attr_value: str,
            order_by: str = "sAMAccountName",
            search_by_attrs_collection: Iterable[str] = None,
            returned_attrs_collection: Iterable[str] = None,
    ) -> Union[tuple[dict, ...], None]:

        """
        Objects (`Person`, `Group` or `Computer`) search method will return a collection of Objects dictionaries.
        :param object_category:             Object Category: `Person`, `Group` or `Computer`
        :param attr_value:                  Attributes Value for Searching
        :param order_by:                    Attribute Name for Sorting
        :param search_by_attrs_collection:  Searching for Person (User) Based on Attributes from the Collection or None
        :param returned_attrs_collection:   Collection of Returned Attributes or None
        :return:
        """

        message = \
            f"@ LDAP Objects Search @ - 'ObjectCategory: `{object_category}`, AttrValue: `{attr_value}`' - {{msg}}"

        validated_data = LdapObjecsSearchModel(
            **{
                "method_type": "search",
                "object_category": object_category.lower(),
                "attr_value": attr_value,
                "order_by": order_by,
                "search_by_attrs_collection": search_by_attrs_collection,
                "returned_attrs_collection": returned_attrs_collection
            }
        ).model_dump()
        search_query = self.__ldap_objects_search_query_selector(
            object_category=validated_data["object_category"],
            attr_value=validated_data["attr_value"],
            search_by_attrs_collection=validated_data["search_by_attrs_collection"]
        )
        # Objects Search request
        resp_raw = self.__ldap_entries(
            search_query=search_query,
            returned_attrs_collection=tuple(validated_data["returned_attrs_collection"])
        )
        if resp_raw:
            return tuple(
                sorted(
                    [{attr.key: attr.value for attr in item} for item in resp_raw],
                    key=lambda item: item[validated_data["order_by"]]
                )
            )
        logger.warning(message.format(msg="LDAP Object(s) not found."))
        return None

    @ldap_logging
    def person_auth(
            self,
            login: str,
            password: str,
            returned_attrs_collection: Iterable[str] = None
    ) -> tuple[bool, dict[str, Any]]:

        """
        Person Auth will return a tuple of connection binding values and a dictionary of person attribute values
        or a dictionary of connection results (Authentication error case).
        :param login:                       User Login as UPN (`sAMAccountName@example.com`)
        :param password:                    User Password
        :param returned_attrs_collection:   Collection of Returned Attributes or None
        :return:
        """

        message = f"@ LDAP Person Auth @ - 'Login: {login}' - {{msg}}"

        validated_data = LdapPersonAuthModel(
            **{
                "login": login,
                "password": password,
                "returned_attrs_collection": returned_attrs_collection
            }
        ).model_dump()
        conn = Connection(
            self.__server_pool,
            raise_exceptions=False,
            user=validated_data["login"],
            password=validated_data["password"],
            receive_timeout=self._receive_timeout
        )
        conn.bind()
        if conn.result["result"] == 0:
            conn.search(
                search_base=self.__search_base,
                search_filter=self.__ldap_person_detail_active_users_query(
                    attr_name="userPrincipalName", attr_value=validated_data["login"]
                ),
                search_scope=SUBTREE,
                attributes=tuple(validated_data["returned_attrs_collection"])
            )
            resp_result = {attr.key: attr.value for attr in conn.entries[0]}
            conn.unbind()
            return True, resp_result
        # conn.bound = False, conn.result["result"] = 49
        logger.warning(message.format(msg="LDAP Person invalid credentials."))
        return False, conn.result
