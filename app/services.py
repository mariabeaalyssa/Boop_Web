import requests, json, os, uuid
from app import _cloud
from dateutil import parser
from flask import session
from PIL import Image
from app import boop

class Variable:
    @staticmethod
    def store_session(token):
        session["booped_in"] = token

    @staticmethod
    def api_url():
        return "http://127.0.0.1:5000"

class Helper:
    @staticmethod
    def user_existence_check(user):
        if len(user) == 6:
            return True

        else:
            return False

    def pet_existence_check(pet):
        if len(pet) == 8:
            return True

        else:
            return False

    @staticmethod
    def modify_addPetForm(form):
        allSpecie_json = Specie.get_all_specie()

        form.specie_input.choices = [(data["public_id"], data["specie_name"]) for data in allSpecie_json["data"]]

        dogBreeds_json = Breed.get_dog_breeds(allSpecie_json["data"][0]["public_id"])
        form.breed_input.choices = [(data["public_id"], data["breed_name"]) for data in dogBreeds_json["data"]]

    @staticmethod
    def datetime_str_to_datetime_obj(datetime_string):
        datetime_obj = parser.parse(datetime_string)

        return datetime_obj

    @staticmethod
    def save_image(form_image, folder):
        if form_image:
            filename = str(uuid.uuid4())

            _, f_ext = os.path.splitext(form_image.filename)
            picture_fn = filename + f_ext

            username = User.get_current_user()["username"]

            _cloud.uploader.upload_image(form_image, folder="BoopIt/{}/{}/".format(folder, username), public_id=filename)
            
            return picture_fn
        else:
            return "default"


class Auth:
    @staticmethod
    def signup_user(data):
        first_name = data.get("firstName_input")
        last_name = data.get("lastName_input")
        username = data.get("username_input")
        email = data.get("email_input")
        password = data.get("password_input")
        contact_no = data.get("contactNo_input")

        signup_req = requests.post("{}/user/".format(Variable.api_url()), json={"firstName" : first_name, "lastName" : last_name, "username" : username, "email" : email, "password" : password, "contactNo" : contact_no})

        return json.loads(signup_req.text)

    @staticmethod
    def login_user(data):
        username_or_email = data.get("usernameOrEmail_input")
        password = data.get("password_input")

        login_req = requests.post("{}/auth/login".format(Variable.api_url()), 
            json = {"usernameOrEmail" : username_or_email, "password" : password})

        return json.loads(login_req.text)

class User:
    @staticmethod
    def get_current_user():
        currentUser_req = requests.get("{}/user/".format(Variable.api_url()), headers={"authorization" : session["booped_in"]})

        return json.loads(currentUser_req.text)

    @staticmethod
    def get_a_user(username):
        user_req = requests.get("{}/user/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})

        return json.loads(user_req.text)

    @staticmethod
    def get_pet_owners(public_id):
        petOwners_req = requests.get("{}/user/pet/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(petOwners_req.text)

class Pet:
    @staticmethod
    def add_a_pet(data):
        form = data.form
        fileForm = data.files

        pet_name = form.get("petName_input")
        bio = form.get("bio_input")
        birthday = form.get("birthday_input")
        sex = form.get("sex_input")
        specie_id = form.get("specie_input")
        breed_id = form.get("breed_input")

        pet_profPic_filename = Helper.save_image(fileForm.get("pet_profPic_input"), "pet")

        addPet_req = requests.post("{}/pet/".format(Variable.api_url()), json={"petName" : pet_name, "bio" : bio, "birthday" : birthday, "sex" : sex, "profPicFilename" : pet_profPic_filename, "specieId" : specie_id, "breedId" : breed_id}, headers={"authorization" : session["booped_in"]})

        return json.loads(addPet_req.text)

    @staticmethod
    def get_a_pet(public_id):
        getPet_req = requests.get("{}/pet/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(getPet_req.text)

    @staticmethod
    def get_user_pets(username):
        getUserPets_req = requests.get("{}/pet/user/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getUserPets_req.text)

class Specie:
    @staticmethod
    def get_all_specie():
        getAllSpecie_req = requests.get("{}/specie/".format(Variable.api_url()), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getAllSpecie_req.text)

class Breed:
    @staticmethod
    def get_dog_breeds(specie_id):
        getDogBreeds_req = requests.get("{}/breed/specie/{}".format(Variable.api_url(), specie_id), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getDogBreeds_req.text)

class Content:
    @staticmethod
    def share_a_content(data):
        content = data.get("shareContent_input")
        tagged_pets = data.get("taggedPet_input")
        
        shareContent_req = requests.post("{}/content/".format(Variable.api_url()), json={"content" : content, "taggedPets" : tagged_pets}, headers={"authorization" : session["booped_in"]})

        return json.loads(shareContent_req.text)

