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
                <li><a href="#create-class-instance">Create Class Instance</a></li>
                <li><a href="#get-computer-detail">Get Computer Detail</a></li>
                <li><a href="#get-group-detail">Get Group Detail</a></li>
                <li><a href="#get-person-detail">Get Person Detail</a></li>
                <li><a href="#search-objects">Search Objects</a></li>
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



#### Create Class Instance

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


#### Get Computer Detail

Predefined list of returned attributes:
* `"cn"`,
* `"description"`,
* `"distinguishedName"`,
* `"lastLogon"`,
* `"logonCount"`,
* `"name"`,
* `"objectGUID"`,
* `"operatingSystem"`,
* `"operatingSystemVersion"`,
* `"sAMAccountName"`,
* `"sAMAccountType"`,
* `"servicePrincipalName"`,
* `"whenChanged"`,
* `"whenCreated"`,

Optional method arguments:</br>
`returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes

```python
ldap = ...
print(ldap.computer_get(
    attr_name="cn", 
    attr_value="value",
    returned_attrs_collection=["cn", "description", "distinguishedName"]
))
# {'description': None, 'distinguishedName': '...', 'cn': '...'}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Get Group Detail

Predefined list of returned attributes:
* `"cn"`,
* `"description"`,
* `"distinguishedName"`,
* `"mail"`,
* `"member"`,
* `"memberOf"`,
* `"name"`,
* `"objectGUID"`,
* `"sAMAccountName"`,
* `"sAMAccountType"`,
* `"whenChanged"`,
* `"whenCreated"`,

Optional method arguments:</br>
`returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes 

```python
ldap = ...
print(ldap.group_get(
    attr_name="sAMAccountName", 
    attr_value="value",
    returned_attrs_collection=["description", "sAMAccountName", "mail", "distinguishedName"]
))
# {'mail': None, 'sAMAccountName': '...', 'distinguishedName': '...', 'description': '...'}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Get Person Detail

Predefined list of returned attributes:
* `"accountExpires"`,
* `"badPasswordTime"`,
* `"badPwdCount"`,
* `"cn"`,
* `"company"`,
* `"department"`,
* `"displayName"`,
* `"employeeID"`,
* `"employeeNumber"`,
* `"extensionAttribute12"`,
* `"extensionAttribute5"`,
* `"extensionAttribute6"`,
* `"extensionAttribute9"`,
* `"ipPhone"`,
* `"l"`,
* `"lastLogoff"`,
* `"lastLogon"`,
* `"lockoutTime"`,
* `"logonCount"`,
* `"mail"`,
* `"manager"`,
* `"memberOf"`,
* `"mobile"`,
* `"msDS-UserPasswordExpiryTimeComputed"`,
* `"msExchExtensionAttribute22"`,
* `"msExchExtensionAttribute23"`,
* `"msExchExtensionCustomAttribute1"`,
* `"msExchExtensionCustomAttribute2"`,
* `"objectGUID"`,
* `"pwdLastSet"`,
* `"sAMAccountName"`,
* `"sAMAccountType"`,
* `"servicePrincipalName"`,
* `"streetAddress"`,
* `"telephoneNumber"`,
* `"thumbnailPhoto"`,
* `"title"`,
* `"userAccountControl"`,
* `"userPrincipalName"`,
* `"whenChanged"`,
* `"whenCreated"`,

Optional method arguments:</br>
`is_active: bool = False` - Define the search scope: Active or All Persons (Users)</br>
`returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes 

```python
ldap = ...
print(ldap.person_get(
    attr_name="sAMAccountName", 
    attr_value="value",
    returned_attrs_collection=["displayName", "sAMAccountName", "employeeNumber"]
))
# {'displayName': '...', 'employeeNumber': '...', 'sAMAccountName': '...'}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


#### Search Objects

`object_type` expect 3 type of values: `Person`, `Group` or `Computer`.</br>
`Person` search wildcard: `value*`</br>
`Group` search wildcard: `*value*`</br>
`Computer` search wildcard: `*value*`

Optional method arguments:</br>
`search_by_attrs_collection: Iterable[str] = None` - Override the predefined list of search attributes for Person (User)</br>
`returned_attrs_collection: Iterable[str] = None` - Override the predefined list of returned attributes 

```python
ldap = ...
print(ldap.objects_search(objects_type="Person", search_value="value"))
# ({'displayName': '...', 'mobile': '...', 'ipPhone': '...', 'sAMAccountName': '...', 'mail': '...', 'employeeNumber': '...', 'userAccountControl': '...', 'department': '...', 'title': '...'},)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CUSTOMIZATION -->
## Customization

Overriding `order_by` instance attributes:

```python
from tinyLDAP3 import tinyLDAP3Client

class tinyLDAP3Custom(tinyLDAP3Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._person_order_by = "New Attr Name"
        self._group_order_by = "New Attr Name"
        self._computer_order_by = "New Attr Name"
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
