from ldap3.core.exceptions import (
    LDAPAttributeError,
    LDAPInvalidCredentialsResult,
    LDAPNoSuchObjectResult,
    LDAPObjectClassError,
    LDAPPasswordIsMandatoryError,
    LDAPSocketOpenError,
    LDAPSocketReceiveError,
    LDAPSocketSendError,
)
from pydantic import ValidationError

from .exceptions import LdapConnectionError, LdapUnexpectedError
from .logger import logger


""" ######################################################### """
""" ***************** TINY LDAP3 DECORATORS ***************** """
""" ######################################################### """


def ldap_logging(ldap_method):

    """
    Connection & Methods Logging Decorator
    :param ldap_method: LDAP Method
    :return:
    """

    def wrapped(*args, **kwargs):

        """
        Connection & Methods Log Wrapper
        :return:
        """

        message = f"@ LDAP {repr(ldap_method.__name__)} Method @ - {{msg}}"
        logger.debug(message.format(msg=f"Query Params:\nArgs: {args}\nKwargs: {kwargs}."))

        try:
            # Return Union[tuple, dict, None]
            return ldap_method(*args, **kwargs)
        except LDAPNoSuchObjectResult as err:
            # Object Reader by DN Not Found
            logger.warning(message.format(msg=f"Warning Detail: {repr(err)}."))
            return None
        except (LDAPAttributeError, LDAPObjectClassError, ValidationError) as err:
            logger.error(message.format(msg=f"Error Detail: {repr(err)}."))
            raise err
        except (
                LDAPInvalidCredentialsResult,
                LDAPPasswordIsMandatoryError,   # No User Password Error (None or "")
                LDAPSocketOpenError,
                LDAPSocketReceiveError,
                LDAPSocketSendError
        ) as err:
            logger.error(message.format(msg=f"Error Detail: {repr(err)}."))
            raise LdapConnectionError("Connection has been failed.")
        except Exception as err:
            logger.error(message.format(msg=f"Error Detail: {repr(err)}."))
            raise LdapUnexpectedError("Unexpected error occurred.")
    return wrapped
