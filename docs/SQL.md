
# SQL Interface
This documentation provides an overview of the SQL Manager, a streamlined interface designed to ease interactions with SQLite databases in Python applications. 

## 1. ManagerSQL

The `ManagerSQL` class is responsible for managing the SQLite database interface. It provides methods to run SQL commands and handle database operations.

**Constructor**

> `__init__(self, sql_file) -> None`
Initializes the `ManagerSQL` object with a SQLite database file.

Parameters
- `sql_file`: Path to the SQLite database file.

### Methods

> 1. `run(self, cmd: str, data: Tuple = ()) -> List[Tuple]`
Executes a SQL command with optional data and fetches the results.

Parameters
- `cmd`: SQL command to be executed.
- `data`: Tuple of data to be used in the SQL command (default is an empty tuple).

Returns:
- List of tuples representing the query result.

> 2. `write(self, cmd: str, data: Tuple = (), isResult: bool = False) -> List[Tuple]`
Executes a SQL write command with optional data, commits the changes, and fetches the results if required.

Parameters
- `cmd`: SQL command to be executed.
- `data`: Tuple of data to be used in the SQL command (default is an empty tuple).
- `isResult`: Boolean indicating whether to fetch results after execution (default is `False`).

Returns:
- List of tuples representing the query result.

> 3. `get_last_id(self) -> int`
Returns the ID of the last inserted row.

Returns:
- `int`: ID of the last inserted row.

---

## 2. MemberInfo

The `MemberInfo` class stores information about a member, including name, roll number, Discord ID, role ID, and group manager roll number.

**Constructor**

> `__init__(self, inputTuple: Tuple) -> None`
Initializes a `MemberInfo` object with the provided data tuple.

Parameters:
- `inputTuple`: A tuple containing member information.

---

## 3. MainTable

The `MainTable` class manages member information in an SQL table. It provides methods to retrieve, search, and add members.

**Constructor**

> `__init__(self, tableID: int, sqlManager: ManagerSQL) -> None`
Initializes a `MainTable` object with the provided table ID and SQL manager.

Parameters:
- `tableID`: The ID of the SQL table.
- `sqlManager`: An instance of the `ManagerSQL` object.

### Methods

> 1.`getMember(self, discordID: int = 0, name: str = '', rollno: str = '', roleID: int = -1, groupManager: str = '') -> MemberInfo | None`
Fetches a member from the table based on various attributes.

Parameters:
- `discordID`: Discord ID of the member (default is `0`).
- `name`: Name of the member (default is an empty string).
- `rollno`: Roll number of the member (default is an empty string).
- `roleID`: Role ID of the member (default is `-1`).
- `groupManager`: Group manager roll number (default is an empty string).

Returns:
- `MemberInfo` object if a member is found, otherwise `None`.

> 2.`getMembersFuzzy(self, name: str = '', rollno: str = '', roleID: int = -1, groupManager: str = '') -> List[MemberInfo]`
Performs a fuzzy search for members based on name and other attributes.

Parameters:
- `name`: Name of the member (default is an empty string).
- `rollno`: Roll number of the member (default is an empty string).
- `roleID`: Role ID of the member (default is `-1`).
- `groupManager`: Group manager roll number (default is an empty string).

Returns:
- List of `MemberInfo` objects matching the criteria.

> 3.`getAllMembers(self, name: str = '', rollno: str = '', roleID: int = -1, groupManager: str = '') -> List[MemberInfo]`
Fetches all members from the table, optionally filtering by attributes.

Parameters:
- `name`: Name of the member (default is an empty string).
- `rollno`: Roll number of the member (default is an empty string).
- `roleID`: Role ID of the member (default is `-1`).
- `groupManager`: Group manager roll number (default is an empty string).

Returns:
- List of `MemberInfo` objects.

> 4.`isMember(self, discordID: int = 0, rollno: str = '', roleID: int = -1, groupManager: str = '') -> bool`
Checks if a member exists in the table based on attributes.

Parameters:
- `discordID`: Discord ID of the member (default is `0`).
- `rollno`: Roll number of the member (default is an empty string).
- `roleID`: Role ID of the member (default is `-1`).
- `groupManager`: Group manager roll number (default is an empty string).

Returns:
- `True` if the member exists, otherwise `False`.

> 5.`addMember(self, discordID: int = 0, name: str = '', rollno: str = '', roleID: int = 0, groupManager: str = '') -> MemberInfo`
Adds a member to the table.

Parameters:
- `discordID`: Discord ID of the member (default is `0`).
- `name`: Name of the member (default is an empty string).
- `rollno`: Roll number of the member (default is an empty string).
- `roleID`: Role ID of the member (default is `0`).
- `groupManager`: Group manager roll number (default is an empty string).

Returns:
- The added `MemberInfo` object.

---

## 4. QueueLink

The `QueueLink` class manages information about a link, including its status and associated data. Changes to link data are immediately reflected in the SQL database.

**Constants**

- `PENDING`: Represents a pending link status.
- `VIEWING`: Represents a viewing link status.
- `VIEWED`: Represents a viewed link status.
- `FORWARDED`: Represents a forwarded link status.

**Constructor**

> `__init__(self, memberQueue, rawLinkTuple: List = [], id: int = -1)`
Initializes a `QueueLink` object, optionally with raw data and an ID.

Parameters:
- `memberQueue`: The `MemberQueue` object this link belongs to.
- `rawLinkTuple`: A list containing raw data for the link (default is an empty list).
- `id`: The ID of the link (default is `-1`).

### Methods

> 1.`add_layer(self, rollno: str, time: float) -> QueueLink`
Adds a layer to the link data.

Parameters:
- `rollno`: The roll number associated with the layer.
- `time`: The time associated with the layer.

Returns:
- The modified `QueueLink` object.

> 2.`set_link(self, link: str) -> QueueLink`
Sets the link URL.

Parameters:
- `link`: The link URL.

Returns:
- The modified `QueueLink` object.

> 3.`set_time(self, time: float) -> QueueLink`
Sets the time for the link.

Parameters:
- `time`: The time value.

Returns:
- The modified `QueueLink` object.

> 4.`from_queueLink(self, queueLink: QueueLink) -> QueueLink`
Copies data from another `QueueLink` object.

Parameters:
- `queueLink`: The `QueueLink` object to copy data from.

Returns:
- The modified `QueueLink` object.

> 5.`_append_self(self) -> None`
Appends the current link to the database. (Internal use only)

### Properties

> `status`
Gets or sets the status of the link as an `int`.

> `link`
Gets the link URL as a `str`.

> `rawlink`
Gets the raw serialized JSON data of the link.

> `time`
Gets the time associated with the link as a `float`.

> `layers`
Gets all the layers of the link in a read-only format as `List[Tuple]`

> `queue`
Gets the `MemberQueue` object this link belongs to.

> `valid`
Checks if the link is valid (i.e., in the database). Returns a `bool`
---

## 5. RoleQueueTable

The `RoleQueueTable` class manages a queue of roles, storing information about links and statuses.

**Constructor**

> `__init__(self, tableID: int, sqlManager: ManagerSQL) -> None`
Initializes a `RoleQueueTable` object with the provided table ID and SQL manager.

Parameters:
- `tableID`: The ID of the SQL table.
- `sqlManager`: An instance of `ManagerSQL`.

### Methods

> 1.`getMemberQueues(self, rollno: str) -> MemberQueue`
Fetches all queues for a member based on their roll number.

Parameters:
- `rollno`: The roll number of the member.

Returns:
- A `MemberQueue` object.

> 2.`getQueue(self, rollno: str, datatype: str = '', status: int = -1) -> List`
Fetches a sorted queue for a member based on data
