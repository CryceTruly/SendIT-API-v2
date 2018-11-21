# SendIT-Api
[![Build Status](https://travis-ci.org/CryceTruly/SendITApi-v2.svg?branch=develop)](https://travis-ci.org/CryceTruly/SendITApi-v2)
[![Maintainability](https://api.codeclimate.com/v1/badges/16b58c2fd68f0361a2bf/maintainability)](https://codeclimate.com/github/CryceTruly/SendITApi-v2/maintainability)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ac47983c1bc5459e9774c9af64f7974d)](https://www.codacy.com/app/CryceTruly/SendIT-Api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CryceTruly/SendIT-Api&amp;utm_campaign=Badge_Grade)
![Hackage-Deps](https://img.shields.io/hackage-deps/v/lens.svg)


A rest api v2 for the SendIT application

## Installation

Create a virtual environment for the project.

```
virtualenv "name of the virtual environment"
```
Then Activate the venv using:
```
source "name of the virtual environment/bin/activate
```

* Navigate to the application directory:

```
git clone https://github.com/CryceTruly/SendITApi-v2.git
cd SendITApi-v2
git checkout develop
```

* Create a virtual environment to install the
application in. You could install virtualenv and virtualenvwrapper.
Within your virtual environment, install the application package dependencies with:

```
pip install -r requirements.txt
```

* Run the application with:

```
python run.py
```
* for tests run in terminal using:

```
py.test
```

#### URL endpoints

| URL Endpoint | HTTP Methods | Summary |
| -------- | ------------- | --------- |
| `api/v2/parcels` | `POST`  | Creates a new Parcel delivery order|
| `api/v2/parcels/<int:id>` | `GET` | Retrieves a specific parcel 
| `api/v2/parcels/<int:id>/cancel` | `PUT` | Cancels a specific parcel 
| `api/v2/users` | `GET` | Retrieve all users |
| `api/v2/users` | `POST` |  Creates a new User |
| `api/v1/users/<int:id>/parcels` | `GET` | Retrieves parcel orders for a specific user 

Example body
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
## Deployement
[Heroku Deployement](https://trulysendit.herokuapp.com)
