import logging
from ldap3.core.exceptions import (
    LDAPInvalidCredentialsResult,
    LDAPPasswordIsMandatoryError,
    LDAPSocketOpenError,
    LDAPSocketReceiveError,
    LDAPSocketSendError,
)
from .exceptions import LdapConnectionError, LdapUnexpectedError


""" ######################################################### """
""" ***************** TINY LDAP3 DECORATORS ***************** """
""" ######################################################### """


def conn_logging(conn_method):

    """
    LDAP. Connection Logging Decorator
    :param conn_method: LDAP Connection
    :return:
    """

    def wrapped(*args, **kwargs):

        """
        LDAP. Connection Log Wrapper
        :return:
        """

        log_message = f"@ LDAP {repr(conn_method.__name__)} Method @ - {{message}}"
        logging.debug(log_message.format(message=f"Query Params:\nArgs: {args}\nKwargs: {kwargs}."))

        try:
            # Return Union[tuple, dict, None]
            return conn_method(*args, **kwargs)
        except (
                LDAPInvalidCredentialsResult,
                LDAPPasswordIsMandatoryError,
                LDAPSocketOpenError,
                LDAPSocketReceiveError,
                LDAPSocketSendError
        ) as err:
            logging.error(log_message.format(message=f"Error Detail:\n{err}."))
            raise LdapConnectionError(log_message.format(message="Connection Has Been Failed."))

        except Exception as err:
            logging.error(log_message.format(message=f"Error Detail:\n{err}."))
            raise LdapUnexpectedError(log_message.format(message="Unexpected Error Occurred."))
    return wrapped
