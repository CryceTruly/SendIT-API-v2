# SendIT-Api
[![Build Status](https://travis-ci.org/CryceTruly/SendITApi-v2.svg?branch=dev)](https://travis-ci.org/CryceTruly/SendITApi-v2)
[![Coverage Status](https://coveralls.io/repos/github/CryceTruly/SendITApi-v2/badge.svg?branch=dev)](https://coveralls.io/github/CryceTruly/SendITApi-v2?branch=dev)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ac47983c1bc5459e9774c9af64f7974d)](https://www.codacy.com/app/CryceTruly/SendIT-Api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CryceTruly/SendIT-Api&amp;utm_campaign=Badge_Grade)
![Hackage-Deps](https://img.shields.io/hackage-deps/v/lens.svg)

SendIT is a courier service app that helps users deliver parcels to different destinations.
# Built with

  - Python 3.7.1
  - Flask 1.0.2
  - PostgreSQL 11.0
  - Celery
  - RabbitMQ
  


#  Features!

  - Users can create an account and log in.
  - Users can create a parcel delivery order.
  - Users can change the destination of a parcel delivery order.
  - Users can cancel a parcel delivery order.
  - Users can see the details of a delivery order.
  - Admin can change the status and present location of a parcel delivery order.




And  also:
- The user gets real-time email notification when Admin changes the status of their parcel.
- The user gets real-time email notification when Admin changes the present location their parcel.
- The app stores Location details and computes travel distance between the pickup location and the destination.




## Installation
Want to contribute Great!

Create a virtual environment for the project.

```
virtualenv "name of the virtual environment"
```
Then Activate the venv using:
```
source "name of the virtual environment/bin/activate
```

 Navigate to the application directory:

```
git clone https://github.com/CryceTruly/SendITApi-v2.git
cd SendITApi-v2
git checkout develop
```

Create a virtual environment to install the
application in. You could install virtualenv and virtualenvwrapper.
Within your virtual environment, install the application package dependencies with:

```
pip install -r requirements.txt
```

 Run the application with:

```
python run.py
```
for tests run in terminal using:

```
py.test --cov
```

#### URL endpoints

| URL Endpoint | HTTP Methods | Summary |
| -------- | ------------- | --------- |
| `api/v2/parcels` | `POST`  | Creates a new Parcel delivery order|
| `api/v2/parcels/<int:id>` | `GET` | Retrieves a specific parcel
| `api/v2/parcels/<int:id>/cancel` | `PUT` | Cancels a specific parcel
| `api/v2/users` | `GET` | Retrieve all users |
| `api/v2/auth/signup` | `POST` |  Creates a new User |
| `api/v2/auth/login` | `POST` |  Log in a user |
| `api/v2/parcels/<parcelId>/destination`|`PUT`| Change the desination of a specific  order
| `api/v2/parcels/<int:parcelId>/status` | `GET` | Retrieves parcel orders for a specific user |
| `api/v2/parcels/<parcelId>/presentLocation`|`PUT`| Change the present location of a specific parcel delivery order|
| `api/v2/users/<int:id>/parcels` | `GET` | Retrieves parcel orders for a specific use|
| `api/v2/auth/logout` | `POST` |  Logs out a user |




#### Example New User body
```
Example body
{
"fullname":"fullname",
"username":"username",
"phone_number":"0756778877",
"email":"email@email.com",
"password":"password"

}
```

#### Example New Parcel Body
```
{
	"recipient_name": "Aron Mike",
            "parcel_description": "Here are my stuff",
            "weight":90,
            "quantity": 22,
            "pickup_address":"Mukono",
            "destination_address":"Entebbe",
            "recipient_phone_number":"0767878787",
            "recipient_email":"rme@gmail.com"
}
```

#### Example Changedestination body
 ```'
 {
 	"destination_address": "Mumbai"
 }
 ```

 #### Example Changestatus body
 ```'
 {
 	"status": "Delivered"
 }
 ```

## Deployement
[Heroku Deployement](https://trulysendit.herokuapp.com)

### Todos

 - Write MORE Tests
 - Format addresses
 - Build a mobile app

License
---
MIT
## Author
[Cryce Truly](https://github.com/crycetruly)
