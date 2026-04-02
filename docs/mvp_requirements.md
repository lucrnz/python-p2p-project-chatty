# MVP Requirements

This document defines the initial requirements for the project

## Requirements
- Create rooms (for now public-only)
- Join rooms
- Discover rooms in the network (for example - if two devices are in the same Wi-Fi, they can see the room)
- Send messages back and forth in the room - Show the user name, and the message. The UI Must look modern enough (think a group chat in telegram)

## Network constraints

No data is uploaded to any server, everything must work peer to peer

## Future work (Do not implemnet now)

End-to-end encrypted messages: The room holds an encryption key and users joining recieve the key, then when new users join, the key is shared in the network securely.

This means no one sniffing the network can read messages.
