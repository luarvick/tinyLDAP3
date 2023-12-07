<a name="readme-top"></a>

<!-- PROJECT NAME -->
<br />
<div align="center">
  <h3 align="center">tinyLDAP3</h3>
  <p align="center">Tiny wrapper for Python `ldap3` Package.</p>
</div>

---

<!-- TABLE OF CONTENTS -->
<details>
    <summary>Table of Contents</summary>
    <ol>
        <li><a href="#about-the-project">About The Project</a></li>
        <li><a href="#installation">Installation</a></li>
        <li>
            <a href="#usage">Usage</a>
            <ul>
                <li><a href="#instance-create">Instance Create</a></li>
                <li><a href="#object-detail">Object Detail</a></li>
                <li><a href="#object-read">Object Read</a></li>
                <li><a href="#objects-search">Objects Search</a></li>
                <li><a href="#person-auth">Person Auth</a></li>
            </ul>
        </li>
        <li><a href="#customization">Customization</a></li>
        <li><a href="#license">License</a></li>
        <li><a href="#contact">Contact</a></li>
    </ol>
</details>

---

<!-- ABOUT THE PROJECT -->
## About The Project

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam aliquam pretium mi quis laoreet.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- INSTALLATION -->
## Installation

Installation is as simple as:

   ```sh
   pip install tinyLDAP3
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage



#### Instance Create

Create a new instance of the `tinyLDAP3Client` class and assigns this object to the local variable `ldap`.

Optional Instance Attributes:</br>
`connect_timeout: int` - Default value 10 (sec.)</br>
`receive_timeout: int` - Default value 10 (sec.)

<span style="color:#ff0000">**Don't store sensitive information in source code. For example use ".env" file.**</span>

```python
from tinyLDAP3 import tinyLDAP3Client
from typing import Iterable

LDAP_USER_DN: str = "CN=Your-LDAP-Account,OU=_SpecialUsers,DC=example,DC=com"
LDAP_USER_PASSWORD: str  = "You%wILL#&neVeR!gUEss"
LDAP_SEARCH_BASE: str = "DC=example,DC=com"
LDAP_HOSTS: Iterable = ["10.10.10.2", "10.10.20.2", "10.10.30.2"]

if __name__ == "__main__":
    ldap = tinyLDAP3Client(
        user_dn=LDAP_USER_DN,
        user_pass=LDAP_USER_PASSWORD,
        search_base=LDAP_SEARCH_BASE,
        hosts=LDAP_HOSTS
    )
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Object Detail

`object_category` - Three categories are expected: `Computer`, `Group` or `Person`.

<details>
    <summary>Predefined list of returned attributes</summary>
    <ul>
        <li>
            <p>Category: Computer</p>
            <details>
                <ul>
                    <li><p>cn</p></li>
                    <li><p>description</p></li>
                    <li><p>distinguishedName</p></li>
                    <li><p>lastLogon</p></li>
                    <li><p>logonCount</p></li>
                    <li><p>name</p></li>
                    <li><p>objectGUID</p></li>
                    <li><p>operatingSystem</p></li>
                    <li><p>operatingSystemVersion</p></li>
                    <li><p>sAMAccountName</p></li>
                    <li><p>sAMAccountType</p></li>
                    <li><p>servicePrincipalName</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>
                </ul>
            </details>
        </li>
        <li>
            <p>Category: Group</p>
            <details>
                <ul>
                    <li><p>cn</p></li>
                    <li><p>description</p></li>
                    <li><p>distinguishedName</p></li>
                    <li><p>mail</p></li>
                    <li><p>member</p></li>
                    <li><p>memberOf</p></li>
                    <li><p>name</p></li>
                    <li><p>objectGUID</p></li>
                    <li><p>sAMAccountName</p></li>
                    <li><p>sAMAccountType</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>
                </ul>
            </details>
        </li>
        <li>
            <p>Category: Person</p>
            <details>
                <ul>
                    <li><p>accountExpires</p></li>
                    <li><p>badPasswordTime</p></li>
                    <li><p>badPwdCount</p></li>
                    <li><p>cn</p></li>
                    <li><p>company</p></li>
                    <li><p>department</p></li>
                    <li><p>displayName</p></li>
                    <li><p>employeeID</p></li>
                    <li><p>employeeNumber</p></li>
                    <li><p>extensionAttribute12</p></li>
                    <li><p>extensionAttribute5</p></li>
                    <li><p>extensionAttribute6</p></li>
                    <li><p>extensionAttribute9</p></li>
                    <li><p>ipPhone</p></li>
                    <li><p>l</p></li>
                    <li><p>lastLogoff</p></li>
                    <li><p>lastLogon</p></li>
                    <li><p>lockoutTime</p></li>
                    <li><p>logonCount</p></li>
                    <li><p>mail</p></li>
                    <li><p>manager</p></li>
                    <li><p>memberOf</p></li>
                    <li><p>mobile</p></li>
                    <li><p>msDS-UserPasswordExpiryTimeComputed</p></li>
                    <li><p>msExchExtensionAttribute22</p></li>
                    <li><p>msExchExtensionAttribute23</p></li>
                    <li><p>msExchExtensionCustomAttribute1</p></li>
                    <li><p>msExchExtensionCustomAttribute2</p></li>
                    <li><p>objectGUID</p></li>
                    <li><p>pwdLastSet</p></li>
                    <li><p>sAMAccountName</p></li>
                    <li><p>sAMAccountType</p></li>
                    <li><p>servicePrincipalName</p></li>
                    <li><p>streetAddress</p></li>
                    <li><p>telephoneNumber</p></li>
                    <li><p>thumbnailPhoto</p></li>
                    <li><p>title</p></li>
                    <li><p>userAccountControl</p></li>
                    <li><p>userPrincipalName</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>
                </ul>
            </details>
        </li>
    </ul>
</details>

Optional arguments:
* `is_active: bool = False` - Define the search scope: Active or All Users.
* `returned_attrs_collection: Iterable[str] = None` - Override the collection of predefined returned attributes. 

##### Computer

```python
ldap = ...
print("Result:", ldap.object_detail(
    object_category="computer",
    attr_name="sAMAccountName", 
    attr_value="value",
    returned_attrs_collection=["description", "sAMAccountName", "mail", "distinguishedName"]
))
# Result: {
#     'operatingSystem': None, 
#     'sAMAccountName': 'value', 
#     'whenCreated': datetime.datetime(...), 
#     'lastLogon': None, 
#     'cn': '...'
# }
```

##### Group

```python
ldap = ...
print("Result:", ldap.object_detail(
    object_category="group",
    attr_name="sAMAccountName", 
    attr_value="value",
    returned_attrs_collection=["description", "sAMAccountName", "mail", "distinguishedName"]
))
# Result: {'mail': None, 'sAMAccountName': 'value', 'description': '...', 'distinguishedName': '...', 'cn': '...'}
```

##### Person

```python
ldap = ...
# Unique value
print("Result:", ldap.object_detail(
    object_category="person",
    attr_name="sAMAccountName", 
    attr_value="unique_value",
    returned_attrs_collection=["sAMAccountName", "mail", "employeeNumber"]
))
# Result: {'mail': '...', 'sAMAccountName': 'unique_value', 'employeeNumber': '...'}

print("Result", ldap.object_detail(
    object_category="person",
    attr_name="sn",
    attr_value="value",
    returned_attrs_collection=["sAMAccountName", "mail", "employeeNumber"]
))
# WARNING:root:@ LDAP Object Detail @ - 'ObjectCategory: `person`, AttrName: `sn`, Value: `value`' \
# - More than one LDAP Object were found. Use attributes with unique values.
# Result: (
#     {'mail': '...', 'employeeNumber': '...', 'sAMAccountName': '...', 'sn': 'value'}, 
#     {'mail': '...', 'employeeNumber': '...', 'sAMAccountName': '...', 'sn': 'value'}
# )
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Object Read

Reading object attributes by category and `distinguishedName` attribute value.

* `returned_attrs_collection: Iterable[str] = None` - Override the collection of returned attributes (Default: All attributes).

```python
ldap = ...
print("Result:", ldap.object_read(
    object_category=["top", "person", "user"],
    dn="CN=Any-LDAP-Account,OU=_Users,DC=example,DC=com",
    returned_attrs_collection=[
        "objectClass", "description", "sAMAccountName", "name", "objectGUID"
    ]
))
# Result: {
#     'objectClass': ['top', 'person', 'organizationalPerson', 'user'], 
#     'description': None, 
#     'name': '...', 
#     'objectGUID': '{...-...-...-...-...}', 
#     'sAMAccountName': '...'
# }
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Objects Search

`object_category` - Three categories are expected: `Computer`, `Group` or `Person`.

<details>
    <summary>Predefined list of attributes for Person (User) search</summary>
    <ul>
        <li>
            <p>Category: Person</p>
            <details>
                <ul>
                    <li><p>cn</p></li>
                    <li><p>employeeNumber</p></li>
                    <li><p>ipPhone</p></li>
                    <li><p>mail</p></li>
                    <li><p>mobile</p></li>
                    <li><p>sAMAccountName</p></li>
                </ul>
            </details>
        </li>
    </ul>
</details>

<details>
    <summary>Predefined list of returned attributes</summary>
    <ul>
        <li>
            <p>Category: Computer</p>
            <details>
                <ul>
                    <li><p>cn</p></li>
                    <li><p>operatingSystem</p></li>
                    <li><p>operatingSystemVersion</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>
                </ul>
            </details>
        </li>
        <li>
            <p>Category: Group</p>
            <details>
                <ul>
                    <li><p>distinguishedName</p></li>
                    <li><p>mail</p></li>
                    <li><p>sAMAccountName</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>   
                </ul>
            </details>
        </li>
        <li>
            <p>Category: Person</p>
            <details>
                <ul>
                    <li><p>department</p></li>
                    <li><p>displayName</p></li>
                    <li><p>employeeNumber</p></li>
                    <li><p>ipPhone</p></li>
                    <li><p>mail</p></li>
                    <li><p>mobile</p></li>
                    <li><p>sAMAccountName</p></li>
                    <li><p>title</p></li>
                    <li><p>userAccountControl</p></li>
                    <li><p>whenChanged</p></li>
                    <li><p>whenCreated</p></li>
                </ul>
            </details>
        </li>
    </ul>
</details>

Category searching:
* `Computer` - wildcard: `*value*`
* `Group` - wildcard: `*value*`
* `Person` - wildcard: `value*`


Optional method arguments:
* `order_by: str = "sAMAccountName"` -  Sorting by a specific attribute. Default value `sAMAccountname`. 
The attribute will be added automatically if it's missing from the collection of returned attributes.
* `search_by_attrs_collection: Iterable[str] = None` - Override the predefined list for Person (User) search.
* `returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes.

##### Computer

```python
ldap = ...
print("Result:", ldap.objects_search(
    object_category="computer",
    attr_value="value",
    returned_attrs_collection=["cn", "lastLogon", "operatingSystem"]
))
# Result: (
#     {'sAMAccountName': '...', 'cn': 'value', 'lastLogon': datetime.datetime(...), 'operatingSystem': '...'},
#     ...,
#     {'sAMAccountName': '...', 'cn': 'value', 'lastLogon': None, 'operatingSystem': '...'}, 
# )
```

##### Group

```python
ldap = ...
print("Result:", ldap.objects_search(
    object_category="group",
    attr_value="value",
    returned_attrs_collection=["sAMAccountName", "distinguishedName"]
))
# Result: (
#     {'distinguishedName': 'CN=...', 'sAMAccountName': 'value'}, 
#     ...,
#     {'distinguishedName': 'CN=...', 'sAMAccountName': 'value'},
# )
```

##### Person

```python
ldap = ...
print("Result", ldap.objects_search(
    object_category="person",
    attr_value="value",
    order_by="displayName",
    returned_attrs_collection=["mail"]
))
# Result: ({'mail': None, 'displayName': '...'}, ..., {'mail': '...', 'displayName': '...'}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Person Auth

`login` - Expected value of the `userPrincipalName` attribute.

Predefined list of returned attributes:
* `"cn"`,
* `"employeeNumber"`,
* `"ipPhone"`,
* `"mail"`,
* `"mobile"`,
* `"userPrincipalName"`,
* `"sAMAccountName"`,

Optional method arguments:</br>
`returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes.

```python
ldap = ...
print(ldap.person_auth(
    login="login@example.com", 
    password="***",
))
# Result Auth Pass:
# (
#     True,
#     {
#         'ipPhone': '...', 
#         'userPrincipalName': 'login@example.com', 
#         'mobile': '...', 
#         'employeeNumber': '...', 
#         'mail': '...', 
#         'cn': '...', 
#         'sAMAccountName': '...'
#     }
# )
# Result Auth Failed:
# (
#     False, 
#     {
#         'result': 49,
#         'description': 'invalidCredentials',
#         'dn': '',
#         'message': '80090308: LdapErr: DSID-0C09056B, comment: AcceptSecurityContext error, data 52e, v4f7c\x00',
#         'referrals': None,
#         'saslCreds': None,
#         'type': 'bindResponse'
#     }
# )
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CUSTOMIZATION -->
## Customization

Overriding `_search_limit` instance attributes:

```python
from tinyLDAP3 import tinyLDAP3Client

class tinyLDAP3Custom(tinyLDAP3Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._search_limit = 1000
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Luarvick - lu.luarvick@gmail.com

Project Link: [https://github.com/luarvick/tinyLDAP3](https://github.com/luarvick/tinyLDAP3)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
