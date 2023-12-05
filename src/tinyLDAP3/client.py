import logging, re
from ldap3 import ALL, AUTO_BIND_DEFAULT, ROUND_ROBIN, SUBTREE, Connection, Server, ServerPool
from typing import Any, Union, Iterable
from .decorators import conn_logging
from .exceptions import LdapAttrFormatError, LdapBoundError, LdapObjTypeError


""" ######################################################### """
""" ******************* TINY LDAP3 CLIENT ******************* """
""" ######################################################### """


# Fullmatch, no symbols !#$%&'*+/=?^_`{|}~- and no first '\"' after '^(?:[a-z0-9]+(?:\.[a-z0-9]+)*|'
mail_regex_rfc822fw_2 = re.compile(
    r"""^(?:[a-z0-9]+(?:\.[a-z0-9]+)*|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")
    @(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|
    \[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}
    (?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|
    \\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$""", re.X
)


class tinyLDAP3Client:

    """
        tinyLDAP3 Client. Wrapper for Python 'ldap3' Package.
        """

    __LDAP_COMPUTER_COMMON_RETURNED_ATTRS_TUPLE = (
        "cn",
        "operatingSystem",
        "operatingSystemVersion",
        "whenChanged",
        "whenCreated",
    )
    __LDAP_COMPUTER_DETAIL_RETURNED_ATTRS_TUPLE = (
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
    __LDAP_GROUP_COMMON_RETURNED_ATTRS_TUPLE = (
        "distinguishedName",
        "mail",
        "sAMAccountName",
        "whenChanged",
        "whenCreated",
    )
    __LDAP_GROUP_DETAIL_RETURNED_ATTRS_TUPLE = (
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
    __LDAP_PERSON_AUTH_RETURNED_ATTRS_TUPLE = (
        "cn",
        "employeeNumber",
        "ipPhone",
        "mail",
        "mobile",
        "userPrincipalName",
        "sAMAccountName",
    )
    __LDAP_PERSON_COMMON_SEARCH_BY_ATTRS_TUPLE = (
        "cn",
        "employeeNumber",
        "ipPhone",
        "mail",
        "mobile",
        "sAMAccountName",
    )
    __LDAP_PERSON_COMMON_RETURNED_ATTRS_TUPLE = (
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
    # "ldap_attributes = '*'" doesn't contain: "accountExpires" & "msDS-UserPasswordExpiryTimeComputed" attrs
    __LDAP_PERSON_DETAIL_RETURNED_ATTRS_TUPLE = (
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

    def __init__(self, **kwargs):
        super(tinyLDAP3Client, self).__init__()

        self._person_order_by = "displayName"
        self._group_order_by = "sAMAccountName"
        self._computer_order_by = "cn"

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

    @conn_logging
    def __ldap_entries(self, search_query: str, returned_attrs_collection: Iterable[str]) -> list:

        """
        Get Entries via Connection Context Manager.
        :param search_query:                Search Query String
        :param returned_attrs_collection:   Returned Attributes Collection
        :return:
        """

        log_message = "@ LDAP Entries @ - {message}"

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
                logging.debug(log_message.format(message="Connection Has Been Successfully Bound."))

                conn.search(
                    search_base=self.__search_base,
                    search_filter=search_query,
                    search_scope=SUBTREE,
                    attributes=returned_attrs_collection
                )
                return conn.entries
            logging.error(log_message.format(message=f"Error Detail:\n{conn}."))
            raise LdapBoundError(log_message.format(message="Bound Error Occurred."))

    @staticmethod
    def __ldap_computer_get_detail_query(attr_name: str, attr_value: str) -> str:

        """
        Computer Get Detail. Strict Match Query.
        :param attr_name:   Attribute Name
        :param attr_value:  Attribute Value
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
        Computers Search Query.
        :param attr_value:  Search by "name" Attribute Value
        :return:
        """

        return f"(&(objectCategory=Computer)(!(objectCategory=Group))(!(objectCategory=Person))(cn=*{attr_value}*))"

    @staticmethod
    def __ldap_group_get_detail_query(attr_name: str, attr_value: str) -> str:

        """
        Group Get Detail. Strict Match Query.
        :param attr_name:   Attribute Name
        :param attr_value:  Attribute Value
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
        Groups Search Query.
        :param attr_value:  Search by "cn" Attribute Value
        :return:
        """

        return f"(&(objectCategory=Group)(!(objectCategory=Computer))(!(objectCategory=Person))(cn=*{attr_value}*))"

    @staticmethod
    def __ldap_person_get_active_query(attr_name: str, attr_value: str) -> str:

        """
        Person Get Active. Strict Match Query.
        :param attr_name:   Attribute Name
        :param attr_value:  Attribute Value
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
    def __ldap_person_get_all_query(attr_name: str, attr_value: str) -> str:

        """
        Person Get All. Strict Match Query.
        :param attr_name:   Attribute Name
        :param attr_value:  Attribute Value
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
        Persons Search Query.
        :param attr_value:                  Attributes Value
        :param search_by_attrs_collection:  Search by Attributes Collection
        :return:
        """

        search_filter = "".join([
            f"({attr_name}={attr_value}*)" for attr_name in search_by_attrs_collection])
        return f"""(
            &(objectCategory=Person)(objectClass=User)
            (!(objectCategory=Computer))
            (!(objectCategory=Group))
            (|{search_filter})
        )"""

    @staticmethod
    def __ldap_obj_not_found(message: str) -> None:

        """
        LDAP Object Not Found.
        :param message: Warning Message
        :return:
        """

        logging.warning(message)
        return None

    @staticmethod
    def sat_description(sat_value: int) -> str:

        """
        Attribute 'sAMAccountType' Values Descriptions.
        :param sat_value:   'sAMAccountType' Value
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
        Attribute 'userAccountControl' Values Descriptions.
        :param uac_value:   'userAccountControl' Value
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

    def computer_get(
            self,
            attr_name: str,
            attr_value: str,
            returned_attrs_collection: Iterable[str] = None
    ) -> Union[dict[str, Any], None]:

        """
        Computer Get Will Return Dictionary of Computer Attributes Values.
        :param attr_name:                   Attribute Name
        :param attr_value:                  Attribute Value
        :param returned_attrs_collection:   Returned Attributes Collection or "*" or None
        :return:
        """

        log_message = f"@ LDAP Computer Get @ - 'Attribute: {attr_name}, Value: {attr_value}' - {{message}}"

        resp_raw = self.__ldap_entries(
            search_query=self.__ldap_computer_get_detail_query(attr_name=attr_name, attr_value=attr_value),
            returned_attrs_collection=returned_attrs_collection or self.__LDAP_COMPUTER_DETAIL_RETURNED_ATTRS_TUPLE
        )
        if resp_raw:
            return {attr.key: attr.value for attr in resp_raw[0]}
        self.__ldap_obj_not_found(log_message.format(message="LDAP Object Not Found."))

    def group_get(
            self,
            attr_name: str,
            attr_value: str,
            returned_attrs_collection: Iterable[str] = None
    ) -> Union[dict[str, Any], None]:

        """
        Group Get Will Return Dictionary of Group Attributes Values.
        :param attr_name:                   Attribute Name
        :param attr_value:                  Attribute Value
        :param returned_attrs_collection:   Returned Attributes Collection or "*" or None
        :return:
        """

        log_message = f"@ LDAP Group Get @ - 'Attribute: {attr_name}, Value: {attr_value}' - {{message}}"

        resp_raw = self.__ldap_entries(
            search_query=self.__ldap_group_get_detail_query(attr_name=attr_name, attr_value=attr_value),
            returned_attrs_collection=returned_attrs_collection or self.__LDAP_GROUP_DETAIL_RETURNED_ATTRS_TUPLE
        )
        if resp_raw:
            resp_result = {attr.key: attr.value for attr in resp_raw[0]}
            for attr_key in ("member", "memberOf"):
                if attr_key in resp_result and resp_result[attr_key]:
                    if isinstance(resp_result[attr_key], list):
                        resp_result[attr_key] = tuple([(item, item) for item in resp_result[attr_key]])
                    else:
                        resp_result[attr_key] = ((resp_result[attr_key], resp_result[attr_key]),)
            return resp_result
        self.__ldap_obj_not_found(log_message.format(message="LDAP Object Not Found."))

    @conn_logging
    def person_auth(self, login: str, password: str) -> tuple[bool, dict[str, Any]]:

        """
        Person Auth Will Return Dictionary of Person Attributes Values.
        :param login:       User Login as UPN (sAMAccountName@example.com)
        :param password:    User Password
        :return:
        """

        log_message = f"@ LDAP Person Auth @ - 'Login: {login}' - {{message}}"

        if not re.fullmatch(mail_regex_rfc822fw_2, login):
            raise LdapAttrFormatError(log_message.format(message="LDAP Person Invalid Login Format."))
        conn = Connection(
            self.__server_pool,
            raise_exceptions=False,
            user=login,
            password=password,
            receive_timeout=self._receive_timeout
        )
        conn.bind()
        if conn.result["result"] == 0:
            conn.search(
                search_base=self.__search_base,
                search_filter=self.__ldap_person_get_active_query(attr_name="userPrincipalName", attr_value=login),
                search_scope=SUBTREE,
                attributes=self.__LDAP_PERSON_AUTH_RETURNED_ATTRS_TUPLE
            )
            resp_result = {attr.key: attr.value for attr in conn.entries[0]}
            conn.unbind()
            return True, resp_result
        # conn.bound = False, conn.result["result"] = 49
        logging.warning(log_message.format(message="LDAP Person Invalid Credentials."))
        return False, conn.result

    def person_get(
            self,
            attr_name: str,
            attr_value: str,
            is_active: bool = False,
            returned_attrs_collection: Iterable[str] = None
    ) -> Union[dict[str, Any], None]:

        """
        Person Get Will Return Dictionary of Person Attributes Values.
        :param attr_name:                   Attribute Name
        :param attr_value:                  Attribute Value
        :param is_active:                   Search Scope (Active or All Users)
        :param returned_attrs_collection:   Returned Attributes Collection or "*" or None
        :return:
        """

        log_message = \
            f"@ LDAP Person Get @ - 'Attribute: {attr_name}, Value: {attr_value}', Active: {is_active}' - {{message}}"

        search_query = self.__ldap_person_get_all_query(attr_name=attr_name, attr_value=attr_value)
        if is_active:
            search_query = self.__ldap_person_get_active_query(attr_name=attr_name, attr_value=attr_value)
        resp_raw = self.__ldap_entries(
            search_query=search_query,
            returned_attrs_collection=returned_attrs_collection or self.__LDAP_PERSON_DETAIL_RETURNED_ATTRS_TUPLE
        )
        if resp_raw:
            return {attr.key: attr.value for attr in resp_raw[0]}
        self.__ldap_obj_not_found(log_message.format(message="LDAP Object Not Found."))

    def objects_search(
            self,
            objects_type: str,
            search_value: str,
            search_by_attrs_collection: Iterable[list] = None,
            returned_attrs_collection: Iterable[str] = None,
    ) -> tuple:

        """
        Objects (`Person`, `Group` or `Computer`) Search Will Return Collection of Dictionary of Objects Attributes Values.
        :param objects_type:                Objects Types: `Person`, `Group` or `Computer`
        :param search_value:                Objects Search Attributes Value
        :param search_by_attrs_collection:  Objects Search via Attributes Collection or None
        :param returned_attrs_collection:   Objects Returned Attributes Collection or None
        :return:
        """

        log_message = f"@ LDAP Objects Search @ - 'Objects: {objects_type}, Search Value: {search_value}' - {{message}}"

        match objects_type.lower():
            case "person":
                search_query = self.__ldap_persons_search_query(
                    attr_value=search_value,
                    search_by_attrs_collection=search_by_attrs_collection or self.__LDAP_PERSON_COMMON_SEARCH_BY_ATTRS_TUPLE
                )
                common_returned_attrs_collection = self.__LDAP_PERSON_COMMON_RETURNED_ATTRS_TUPLE
                order_by = self._person_order_by
            case "group":
                search_query = self.__ldap_groups_search_query(attr_value=search_value)
                common_returned_attrs_collection = self.__LDAP_GROUP_COMMON_RETURNED_ATTRS_TUPLE
                order_by = self._group_order_by
            case "computer":
                search_query = self.__ldap_computers_search_query(attr_value=search_value)
                common_returned_attrs_collection = self.__LDAP_COMPUTER_COMMON_RETURNED_ATTRS_TUPLE
                order_by = self._computer_order_by
            case _:
                raise LdapObjTypeError(log_message.format(message="LDAP Objects Type Error."))

        if returned_attrs_collection and order_by not in returned_attrs_collection:
            returned_attrs_collection = list(returned_attrs_collection)
            returned_attrs_collection.append(order_by)

        resp_raw = self.__ldap_entries(
            search_query=search_query,
            returned_attrs_collection=returned_attrs_collection or common_returned_attrs_collection
        )
        if not resp_raw:
            logging.warning(log_message.format(message="LDAP Object(s) Not Found."))

        # Return Empty Tuple if not 'resp_raw'
        return tuple(
            sorted(
                [{attr.key: attr.value for attr in item} for item in resp_raw],
                key=lambda item: item[order_by]
            )
        )
