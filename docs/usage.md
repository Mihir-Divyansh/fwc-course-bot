# Discord Bot Functionalities

This Discord server bot is designed for the course **FWC** and includes the following commands and roles.

## Bot Functionalities

1. **/register**:  
   Registers a student using their FWC roll number, mapping it with their Discord ID.

2. **/eval**:  
   Sends a GitHub repo link to the next role in the hierarchy (manager).

3. **/view**:  
   Allows managers to see submissions.

4. **/viewstats**:  
   Provides number of links in queue

5. **/approve**:  
   Can be used if the manager has a manager to forward the currently viewed link to the next in the hierarchy.

## Role Hierarchy

- **GVV**: Topmost role in the server hierarchy.
  - **TA (Teaching Assistant)**: Manages the "module student" role.
  - **PM (Project Manager)**: Manages the "project student" role.

## Role Responsibilities

- **Module Student**:  
  Managed by **TA (Teaching Assistant)**.

- **Project Student**:  
  Managed by **PM (Project Manager)**.

## Command Flow

1. `/eval`: Used to send a GitHub repo link to the respective manager role.
2. `/view`: Managers use this command to view submissions.
3. `/approve`: Forwards the currently viewed link to the next manager in the hierarchy (if applicable).
