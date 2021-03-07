Device Registry Service
Usage
All responses will have the form

{
    "data": "Mixed type holding the content of the response",
    "message": "Description of what happened"
}
Subsequent response definitions will only detail the expected value of the data field

List all devices
Definition

GET /books

Response

200 OK on success
[
  {
    "author": "A1",
    "id": 1,
    "language": "Engligh",
    "title": "T1"
  },
  {
    "author": "A2",
    "id": 2,
    "language": "Engligh",
    "title": "T2"
  },
  {
    "author": "A3",
    "id": 3,
    "language": "Engligh",
    "title": "T3"
  },
  {
    "author": "A4",
    "id": 4,
    "language": "Hindi",
    "title": "T4"
  },
  {
    "author": "A5",
    "id": 5,
    "language": "Engligh",
    "title": "T5"
  }
]

Registering a new book
Definition

POST /books

Arguments

"title":string a friendly name for this device
"author":string the type of the device as understood by the client
"language":string the IP address of the device's controller

If a book with the given title already exists, the existing device will be overwritten.

Response

201 Created on success
 {
    "author": "updated",
    "id": 6,
    "language": "Engligh",
    "title": "new ttile"
  }
  
Lookup device details
GET /books/<identifier>

Response

404 Not Found if the device does not exist.

200 OK on success
{
    "author": "A5",
    "id": 5,
    "language": "Engligh",
    "title": "T5"
  }
Delete a device
Definition

DELETE /devices/<identifier>

Response

404 Not Found if the device does not exist
204 No Content on success