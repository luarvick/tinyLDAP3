import logging


logger = logging.getLogger("ldap_client")


def ldap_log_level_set(log_level: str):

    """
    Log Level Set
    :param log_level:   LDAP Log Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    :return:
    """

    logger.setLevel(log_level)