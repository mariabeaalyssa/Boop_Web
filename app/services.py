import requests, json, os, uuid
from app import boop, _cloud
from dateutil import parser
from flask import session
from PIL import Image
import urllib.request as urllib
import io
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
        if len(user) == 9:
            return True

        else:
            return False

    def pet_existence_check(pet):
        if len(pet) == 10:
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
    def save_image(form_image):
        if form_image:
            filename = str(uuid.uuid4())
            
            _cloud.uploader.upload_image(form_image, folder="BoopIt/", public_id=filename)

            _, f_ext = os.path.splitext(form_image.filename)
            picture_fn = filename + f_ext
            picture_path = os.path.join(boop.root_path,'static/images', picture_fn)
            
            output_size=(500, 500)
            i = Image.open(form_image)
            i.thumbnail(output_size)
            i.save(picture_path)

            return picture_fn
    
        else:
            return "default.jpg"

    @staticmethod
    def ensure_localAndCloud_imageUpload_reflection(photo_id):
        file_exists = os.path.exists("{}/static/images/{}".format(boop.root_path, photo_id + ".jpg"))
        photo_fn = photo_id + ".jpg"

        if file_exists is True:

            return photo_fn + "IF"
        
        else:
            upload_path = os.path.join(boop.root_path, 'static/images', photo_fn)

            url = "https://res.cloudinary.com/fmscrns/image/upload/v1579236287/BoopIt/{}".format(photo_fn)
            
            fd = urllib.urlopen(url)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)
            im.save(upload_path)
            return photo_fn + "ELSE"

class Auth:
    @staticmethod
    def verify_email(email):
        verifyEmail_resp = requests.get("{}/user/verify/email".format(Variable.api_url()), json={"email" : email})

        email_resp = json.loads(verifyEmail_resp.text)

        return email_resp

    @staticmethod
    def verify_username(username):
        verifyUsername_resp = requests.get("{}/user/verify/username".format(Variable.api_url()), json={"username" : username})

        username_resp = json.loads(verifyUsername_resp.text)

        return username_resp

    @staticmethod
    def signup_user_part_two(data):
        signup_req = requests.post("{}/user/".format(Variable.api_url()), json={"firstName" : data["first_name"], "lastName" : data["last_name"], "username" : data["username"], "email" : data["email"], "password" : data["password"], "contactNo" : data["contact_no"]})
    
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

    @staticmethod
    def update_user(data):
        current_user = User.get_current_user()

        form = data.form
        fileForm = data.files

        new_first_name = form.get("firstName_input")
        new_last_name = form.get("lastName_input")
        new_username = form.get("username_input")
        new_email = form.get("email_input")
        new_password = form.get("password_input")
        new_contact_no = form.get("contactNo_input")
        new_user_profPhoto_filename = current_user["profPhotoFilename"]
        new_user_coverPhoto_filename = current_user["coverPhotoFilename"]
        
        if fileForm.get("user_profPhoto_input"):
            new_user_profPhoto_filename = Helper.save_image(fileForm.get("user_profPhoto_input"))
        if fileForm.get("user_coverPhoto_input"):
            new_user_coverPhoto_filename = Helper.save_image(fileForm.get("user_coverPhoto_input"))

        userUpdate_req = requests.put("{}/user/{}".format(Variable.api_url(), current_user["username"]), json={"firstName" : new_first_name, "lastName" : new_last_name, "username" : new_username, "email" : new_email, "password" : new_password, "contactNo" : new_contact_no, "profPhotoFilename" : new_user_profPhoto_filename, "coverPhotoFilename" : new_user_coverPhoto_filename}, headers={"authorization" : session["booped_in"]})
        
        return json.loads(userUpdate_req.text)

    @staticmethod
    def get_all_users():
        allUsers_req = requests.get("{}/user/all".format(Variable.api_url()), headers={"authorization": session["booped_in"]})

        return json.loads(allUsers_req.text)

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

        pet_profPhoto_filename = Helper.save_image(fileForm.get("pet_profPic_input"))
        pet_coverPhoto_filename = Helper.save_image(fileForm.get("pet_coverPic_input"))

        addPet_req = requests.post("{}/pet/".format(Variable.api_url()), json={"petName" : pet_name, "bio" : bio, "birthday" : birthday, "sex" : sex, "profPhotoFilename" : pet_profPhoto_filename, "coverPhotoFilename" : pet_coverPhoto_filename, "specieId" : specie_id, "breedId" : breed_id}, headers={"authorization" : session["booped_in"]})

        return json.loads(addPet_req.text)

    @staticmethod
    def get_a_pet(public_id):
        getPet_req = requests.get("{}/pet/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(getPet_req.text)

    @staticmethod
    def get_user_pets(username):
        getUserPets_req = requests.get("{}/pet/user/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getUserPets_req.text)

        
    @staticmethod
    def delete_pet(public_id):
        deleteUserPets_req = requests.delete("{}/pet/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(deleteUserPets_req.text)

    @staticmethod
    def update_pet(public_id, data):
        form = data.form
        
        updateUserPets_req = requests.put("{}/pet/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(updateUserPets_req.text)

class Specie:
    @staticmethod
    def get_all_specie():
        getAllSpecie_req = requests.get("{}/specie/all".format(Variable.api_url()), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getAllSpecie_req.text)

class Breed:
    @staticmethod
    def get_dog_breeds(specie_id):
        getDogBreeds_req = requests.get("{}/breed/specie/{}".format(Variable.api_url(), specie_id), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getDogBreeds_req.text)

class Post:
    @staticmethod
    def new_post(data):
        form = data.form
        content = form.get("shareContent_input")
        newPost_req= requests.post("{}/post/".format(Variable.api_url()), json={"content" : content}, headers={"authorization" : session["booped_in"]})
        return json.loads(newPost_req.text)


    @staticmethod
    def get_user_posts(username):
        getUserPost_req = requests.get("{}/post/user/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})

        return json.loads(getUserPost_req.text)


    @staticmethod
    def get_a_post(post_id):
        getPost_req = requests.get("{}/post/{}".format(Variable.api_url(), post_id), headers={"authorization" : session["booped_in"]})

        return json.loads(getPost_req.text)

    @staticmethod
    def delete_post(post_id):
        deleteUserPosts_req = requests.delete("{}/post/{}".format(Variable.api_url(), post_id), headers={"authorization" : session["booped_in"]})

        return json.loads(deleteUserPosts_req.text)

    @staticmethod
    def get_all_posts():
        allPosts_req = requests.get("{}/post/all".format(Variable.api_url()), headers={"authorization": session["booped_in"]})

        return json.loads(allPosts_req.text)

class Comment:
    @staticmethod
    def new_comment(data, post_id):
        form = data.form
        comment = form.get("commentPost_input")
        newComment_req= requests.post("{}/comment/{}".format(Variable.api_url(), post_id), json={"comment" : comment}, headers={"authorization" : session["booped_in"]})
        return json.loads(newComment_req.text)

    @staticmethod
    def get_a_comment(public_id):
        getComment_req = requests.get("{}/comment/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})
        return json.loads(getComment_req.text)

    @staticmethod
    def get_rel_comment(post_id):
        getRelation_req = requests.get("{}/comment/post/{}".format(Variable.api_url(), post_id), headers={"authorization" : session["booped_in"]})
        return json.loads(getRelation_req.text)

    @staticmethod
    def get_all_comments():
        getAllComments_req = requests.get("{}/comment/all".format(Variable.api_url()), headers={"authorization" : session["booped_in"]})
        return json.loads(getAllComments_req.text)

class Deal:
    @staticmethod
    def new_deal(data, pet_id):
        form = data.form
        price = form.post("pricePet_input")
        newDeal_req = requests.get("{}/deal/{}".format(Variable.api_url(), pet_id),  json={"deal" : comment},headers={"authorization" : session["booped_in"]})
        return json.loads(newDeal_req.text)
    
    @staticmethod
    def get_all_deals(data):
        
        getAllDeals_req = requests.get("{}/deal/{}".format(Variable.api_url()), headers={"authorization" : session["booped_in"]})
        return json.loads(getAllDeals_req.text)

    @staticmethod
    def get_a_deal(public_id):
        
        getADeal_req = requests.get("{}/deal/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})
        return json.loads(getADeal_req.text)

    @staticmethod
    def delete_deal(public_id):
        deleteDeal_req = requests.delete("{}/deal/{}".format(Variable.api_url(), public_id), headers={"authorization" : session["booped_in"]})

        return json.loads(deleteUserPosts_req.text)

    @staticmethod
    def get_user_deals(username):
        
        getUserDeal_req = requests.get("{}/deal/user/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})
        return json.loads(getUserDeal_req.text)


    @staticmethod
    def get_all_posts():
        allPosts_req = requests.get("{}/post/all".format(Variable.api_url()), headers={"authorization": session["booped_in"]})

        return json.loads(allPosts_req.text)
    
class Photo:
    @staticmethod
    def add_a_photo():
        addPhoto_req = requests.post("{}/photo/")
"""
    -----GET CONTENT----
    @staticmethod
    def get_a_content(data):
        getContent_req = requests.get("{}/content/{}".format(Variable.api_url(), username), headers={"authorization" : session["booped_in"]})
        
        return json.loads(getUserPets_req.text)

"""



