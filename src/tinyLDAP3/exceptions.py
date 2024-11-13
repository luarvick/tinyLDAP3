from .logger import logger


""" ######################################################### """
""" ***************** TINY LDAP3 EXCEPTIONS ***************** """
""" ######################################################### """


class LdapBaseError(Exception):

    """
        tinyLDAP3. Base Error.
        """

    def __init__(self, message: str = None):
        self.message = message
        if self.message:
            logger.error(self.message)

    def __str__(self):
        return self.message


class LdapBoundError(LdapBaseError):
    pass


class LdapConnectionError(LdapBaseError):
    pass


class LdapUnexpectedError(LdapBaseError):
    pass
