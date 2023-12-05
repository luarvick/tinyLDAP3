import logging
from ldap3.core.exceptions import (
    LDAPAttributeError,
    LDAPInvalidCredentialsResult,
    LDAPObjectClassError,
    LDAPPasswordIsMandatoryError,
    LDAPSocketOpenError,
    LDAPSocketReceiveError,
    LDAPSocketSendError,
)
from .exceptions import LdapConnectionError, LdapUnexpectedError


""" ######################################################### """
""" ***************** TINY LDAP3 DECORATORS ***************** """
""" ######################################################### """


def ldap_logging(conn_method):

    """
    LDAP. Connection & Methods Logging Decorator
    :param conn_method: LDAP Connection
    :return:
    """

    def wrapped(*args, **kwargs):

        """
        LDAP. Connection & Methods Log Wrapper
        :return:
        """

        log_message = f"@ LDAP {repr(conn_method.__name__)} Method @ - {{message}}"
        logging.debug(log_message.format(message=f"Query Params:\nArgs: {args}\nKwargs: {kwargs}."))

        try:
            # Return Union[tuple, dict, None]
            return conn_method(*args, **kwargs)
        except (LDAPAttributeError, LDAPObjectClassError) as err:
            logging.error(log_message.format(message=f"Error Detail: {repr(err)}."))
            raise err
        except (
                LDAPInvalidCredentialsResult,
                LDAPPasswordIsMandatoryError,   # No User Password Error (None or "")
                LDAPSocketOpenError,
                LDAPSocketReceiveError,
                LDAPSocketSendError
        ) as err:
            logging.error(log_message.format(message=f"Error Detail: {repr(err)}."))
            raise LdapConnectionError("Connection has been failed.")
        except Exception as err:
            logging.error(log_message.format(message=f"Error Detail: {repr(err)}."))
            raise LdapUnexpectedError("Unexpected error occurred.")
    return wrapped
