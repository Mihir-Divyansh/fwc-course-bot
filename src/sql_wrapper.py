
import sqlite3 as sql
from typing import List, Dict, Tuple

import time
import json
import re
import bisect
from src.serializers import SerializedJSON

# This class manages SQL interface
class ManagerSQL:

    def run(self, cmd, data=()):
        try:
            self.cursor.execute(cmd, data)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f'Error executing/fetching SQL: {cmd}, {data}\n\t{e}')

    def write(self, cmd, data=(), isResult=False):
        try:
            self.cursor.execute(cmd, data)
            result = self.cursor.fetchall()
            self.sql_db.commit()
            return result
        except Exception as e:
            raise Exception(f'Error executing/fetching SQL: {cmd}, {data}\n\t{e}')

    def __init__(self, sql_file) -> None:
        self.file = sql_file
        self.sql_db = sql.connect(sql_file, detect_types=sql.PARSE_DECLTYPES)
        self.cursor = self.sql_db.cursor()

    def get_last_id(self) -> int:
        return self.cursor.lastrowid

# holds information about a member
class MemberInfo:
    def __init__(self, inputTuple) -> None:
        self.name : str = inputTuple[0]
        self.rollno : str = inputTuple[1]
        self.discordID : int = int(inputTuple[2])
        self.roleID : int = int(inputTuple[3])
        self.groupManagerRollNo : str = str(inputTuple[4])

# This class holds data about evey members's role,
# discord id and roll-no
class MainTable:
    def __init__(self, tableID : int, sqlManager) -> None:
        self.tableID : int = int(tableID)
        self.sqlManager : ManagerSQL = sqlManager

    # get a member from a discord ID or their roll no
    def getMember(self, discordID : int = 0, name : str = '', rollno : str = '', roleID : int = -1, groupManager : str = '') -> MemberInfo | None:
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = self.sqlManager.run(f"SELECT * FROM table_{self.tableID} WHERE name=? OR rollno=? OR discord=? OR roleID=? OR groupManager=?",(
                            name,
                            rollno,
                            discordID,
                            roleID,
                            groupManager
        ))

        if result:
            return MemberInfo(result[0])
        else:
            None

    # check loosely if a someone has a part of a name in database
    # if roleID is specified, then it will do Fuzzy search for only that role
    def getMembersFuzzy(self, name : str = '', rollno : str = '', roleID : int = -1, groupManager : str = '') -> List[MemberInfo]:
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')
        
        if roleID >= 0:
            result = self.sqlManager.run(f"SELECT * FROM table_{self.tableID} WHERE (name LIKE '%'||?||'%' OR rollno=? OR groupManager=?) AND roleID=?",(
                                name,
                                rollno,
                                groupManager,
                                roleID
            ))
        else:
            result = self.sqlManager.run(f"SELECT * FROM table_{self.tableID} WHERE name LIKE '%'||?||'%' OR rollno=? OR groupManager=?",(
                                name,
                                rollno,
                                groupManager
            ))

        return [MemberInfo(_) for _ in result]
    
    # get all members
    def getAllMembers(self, name : str = '', rollno : str = '', roleID : int = -1, groupManager : str = '') -> List[MemberInfo]:
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')
        
        if roleID >= 0:
            result = self.sqlManager.run(f"SELECT * FROM table_{self.tableID} WHERE roleID=?",(roleID,))
        else:
            result = self.sqlManager.run(f"SELECT * FROM table_{self.tableID}")

        return [MemberInfo(_) for _ in result]

    # check if a member is in our database
    def isMember(self, discordID : int = 0, rollno : str = '', roleID : int = -1, groupManager : str = '') -> bool:
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = self.sqlManager.run(f"SELECT COUNT(1) FROM table_{self.tableID} WHERE rollno=? OR discord=? OR roleID=? OR groupManager=?",( 
                            rollno,
                            discordID,
                            roleID,
                            groupManager
        ))
        
        return result[0][0] > 0

    # add a member to the database
    # DOES NOT check for duplication
    def addMember(self, discordID : int = 0, name : str = '', rollno : str = '', roleID : int = 0, groupManager : str = ''):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = self.sqlManager.write(f"INSERT INTO table_{self.tableID} VALUES (?, ?, ?, ?, ?) RETURNING *;",(
                        name,
                        rollno,
                        discordID,
                        roleID,
                        groupManager
        ))
        
        return MemberInfo(result[0])

    def wipeDB(self, db_path: str):
        """Wipes the entire SQLite database by dropping all tables."""
        conn = None  
        try:
            conn = sql.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table_name in tables:
                table_name = table_name[0] 
                print(f"Dropping table {table_name}...")
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

            conn.commit()
            print("Database wiped successfully.")

        except Exception as e:
            print(f"An error occurred while wiping the database: {e}")

        finally:
            if conn:  
                conn.close()



# holds information about a link
# a change in link data is immediately reflected in the SQL database
class QueueLink:
    PENDING   = 0
    VIEWING   = 1
    VIEWED    = 2
    FORWARDED = 3

    def __init__(self, memberQueue, rawLinkTuple=[], id = -1):
        if rawLinkTuple:
            self.__link = rawLinkTuple[0]
            self.__linkData : SerializedJSON = rawLinkTuple[1]
            self.__time = rawLinkTuple[2]
            self.__status = rawLinkTuple[3]
            self.__id = id
            self.__builded = True
        else:
            self.__linkData : SerializedJSON = SerializedJSON()
            self.__time = None
            self.__status = QueueLink.PENDING
            self.__id = -1
            self.__builded = False
        self.__queue = memberQueue

    def add_layer(self, rollno : str, time : float):
        if not self.__linkData.exists('headers'):
            self.__linkData.dictionary['headers'] = {}
        
        currentLayerID = len(self.__linkData['headers'])
        
        self.__linkData.dictionary['headers'] |= {
            f'layer-{currentLayerID}':
                {
                    'rollno':rollno, 
                    'time':time 
                }
            }

        return self
    def set_link(self, link : str):
        self.__link = link
        return self
    def set_time(self, time : float):
        self.__time = time
        return self

    def from_queueLink(self, queueLink):
        self.__link = queueLink.__link
        self.__linkData : SerializedJSON = queueLink.__linkData
        return self

    # internal function
    def _append_self(self):
        self.__id = self.__queue.roleQueueTable.append(self.__queue.rollno, 'link', self.__link, self.__linkData, time=self.__time, status=self.__status)

    # getter
    @property
    def status(self) -> int:
        return self.__status
    # setter, updates value in database
    @status.setter
    def status(self, new_status):
        self.__status = new_status
        if self.__builded:
            self.__queue.roleQueueTable.update(self.__id, self.__linkData, self.__time, self.__status)

    # getter
    @property
    def link(self) -> str:
        return self.__link
    
    @property
    def rawlink(self) -> SerializedJSON:
        return self.__linkData
    
    @property
    def time(self) -> float:
        return self.__time

    # getter for getting all readonly info about the layers
    @property
    def layers(self) -> List[Tuple[str, float]]:
        size = 0
        _tmp = {}
        for layerID, values in self.__linkData['headers'].items():
            _tmp[int(layerID.removeprefix('layer-'))] = ( values['rollno'], values['time'] )
            size += 1
        _result = []
        for i in range(size):
            _result.append(_tmp[i])
        return _result
    
    @property
    def queue(self):
        return self.__queue
    
    # a link is valid if it is in the database
    @property
    def valid(self) -> bool:
        return self.__id != -1

# This class holds data about people having a Role
# like name(more for later)
class RoleQueueTable:
    def __init__(self, tableID : int, sqlManager) -> None:
        self.tableID : int = int(tableID)
        self.sqlManager : ManagerSQL = sqlManager

    # get a member from a roll no
    def getMemberQueues(self, rollno : str):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = self.sqlManager.run(f"SELECT * FROM (SELECT * FROM table_{self.tableID} WHERE rollno=?) ORDER BY status ASC, time ASC",(rollno,))
        return MemberQueue(rollno, self, result)

    # get a sorted queue of member with a roll no
    # and only containing datatype and status type entries
    def getQueue(self, rollno : str, datatype : str='', status : int = -1):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = []

        if datatype and status >= 0:
            result = self.sqlManager.run(f"SELECT * FROM (SELECT * FROM table_{self.tableID} WHERE rollno=? AND datatype=? AND status=?) ORDER BY status ASC, time ASC",(rollno,datatype, status))
        elif datatype:
            result = self.sqlManager.run(f"SELECT * FROM (SELECT * FROM table_{self.tableID} WHERE rollno=? AND datatype=?) ORDER BY status ASC, time ASC",(rollno,datatype))
        elif status >= 0:
            result = self.sqlManager.run(f"SELECT * FROM (SELECT * FROM table_{self.tableID} WHERE rollno=? AND status=?) ORDER BY status ASC, time ASC",(rollno,status))
        else:
            result = self.sqlManager.run(f"SELECT * FROM (SELECT * FROM table_{self.tableID} WHERE rollno=?) ORDER BY status ASC, time ASC",(rollno,))

        return result

    # adds only if the status and value attributes are unique
    # returns a unique id of the added data
    def append(self, rollno : str, datatype : str, value : str, data : SerializedJSON, time=0.0, status=QueueLink.PENDING):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')
        
        isUnique = None
        if status == QueueLink.PENDING:
            isUnique = 1

        result = self.sqlManager.write(f"""
            INSERT INTO table_{self.tableID}(rollno, datatype, value, data, time, status, isunique) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(value, isunique) DO NOTHING
            RETURNING rowid
            """,
            
            (rollno, datatype, value, data, time, status, isUnique))
        
        if result:
            return result[0][0]
        else:
            return -1
    
    def count(self, rollno : str, datatype : str, status=QueueLink.PENDING):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')

        result = self.sqlManager.run(f"SELECT COUNT(*) FROM table_{self.tableID} WHERE rollno=? AND datatype=? AND status=?",(rollno, datatype, status))

        return result[0][0]

    # update a datatype with an ID
    def update(self, id : int, data : SerializedJSON, time=0.0, status=QueueLink.PENDING):
        if not isinstance(self.tableID, int):
            raise TypeError('Error: tableID is not an integer!')
        
        isUnique = None
        if status == QueueLink.PENDING:
            isUnique = 1
        
        result = self.sqlManager.write(f"UPDATE OR IGNORE table_{self.tableID} SET data=?, time=?, status=?, isunique=? WHERE id=?",(data, time, status, isUnique, id))

# holds information about a member
# the lists in this class WILL grow over the course of 
# the course
class MemberQueue:
    def __init__(self, rollno, roleQTable : RoleQueueTable) -> None:
        self.roleQueueTable : RoleQueueTable = roleQTable
        self.rollno = rollno
        
        plinks = self.roleQueueTable.getQueue(rollno, datatype='link', status=QueueLink.PENDING)
        vlinks = self.roleQueueTable.getQueue(rollno, datatype='link', status=QueueLink.VIEWING)
        
        # store only pending and viewing links
        self.pending_links : List[QueueLink] = [QueueLink(self, rawLinkTuple=_[3:], id=_[0]) for _ in plinks]
        self.viewing_links : List[QueueLink] = [QueueLink(self, rawLinkTuple=_[3:], id=_[0]) for _ in vlinks]
        # dict of status and size
        self.link_sizes : Dict[int, int] = {
                    QueueLink.PENDING:len(self.pending_links), 
                    QueueLink.VIEWING:self.roleQueueTable.count(rollno, 'link', QueueLink.VIEWING),
                    QueueLink.VIEWED:self.roleQueueTable.count(rollno, 'link', QueueLink.VIEWED)
                }

    def append_link(self, link : QueueLink):
        link._append_self()

        if not link.valid:
            return
        
        if link.status == QueueLink.PENDING:
            # add link to list but keep it sorted
            bisect.insort(self.pending_links, link, key=lambda x: x.time)
        
        self.link_sizes[link.status] += 1

    # pops a pending link 
    # but if a link is being viewed, it will be showed instead
    # also marks the link as VIEWING
    def pop_pending_link(self):
        if self.link_sizes[QueueLink.VIEWING] > 0:
            link = self.viewing_links.pop(0)
            self.link_sizes[QueueLink.VIEWING] -= 1
            return link
        else:
            link = self.pending_links.pop(0)
            self.viewing_links.insert(0, link)
            link.status = QueueLink.VIEWING
            self.link_sizes[QueueLink.PENDING] -= 1
            return link
    
    # pops a viewing link(if there is one, otherwise do nothing)
    # also marks the link as VIEWED
    def pop_viewing_link(self):
        if self.link_sizes[QueueLink.VIEWING] > 0:
            link = self.viewing_links.pop(0)
            link.status = QueueLink.VIEWED
            self.link_sizes[QueueLink.VIEWING] -= 1
            return link

