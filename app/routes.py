import requests, json
from app import boop
from flask import Flask, render_template, request, session, redirect, url_for, flash, abort
from app.forms import *
from app.decorators import *
from app.services import *
from datetime import datetime

@boop.route("/", methods=["GET", "POST"])
@boop.route("/welcome", methods=["GET", "POST"])
@inaccesible_if_authenticated
def welcome():
    loginForm = LoginForm()

    if request.method == "POST":
        if loginForm.validate_on_submit():
            form = request.form

            loginUser_json = Auth.login_user(form)
            
            if loginUser_json["status"] == "success":
                Variable.store_session(loginUser_json["authorization"])

                flash(loginUser_json["payload"], "success")
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))

            else:
                flash(loginUser_json["payload"], "danger")

                return redirect(url_for("login"))

    return render_template("welcome.html", title="Welcome", loginForm=loginForm)

@boop.route("/about", methods=["GET", "POST"])
@inaccesible_if_authenticated
def about():
    return render_template("about.html", title="Welcome")

@boop.route("/signup", methods=["GET", "POST"])
@inaccesible_if_authenticated
def signup_part_one():
    signupPartOneForm = SignupPartOneForm()
    
    if request.method == "POST":
        if signupPartOneForm.validate_on_submit():
            data = request.form

            return redirect(url_for("signup_part_two", firstName=data.get("firstName_input"), lastName=data.get("lastName_input"), email=data.get("email_input"), username=data.get("username_input")))

    return render_template("signup_part_one.html", title="Sign up", signupPartOneForm=signupPartOneForm)

@boop.route("/signup/p2/fname=<firstName>&lname=<lastName>&email=<email>&username=<username>", methods=["GET", "POST"])
@inaccesible_if_authenticated
def signup_part_two(firstName, lastName, email, username):
    signupPartTwoForm = SignupPartTwoForm()

    if request.method == "POST":
        if signupPartTwoForm.validate_on_submit():
            data = {"first_name" : firstName, "last_name" : lastName, "email" : email, "username" : username, "contact_no" : request.form.get("contactNo_input"), "password" : request.form.get("password_input")}
            
            signupUser_json = Auth.signup_user_part_two(data)

            if signupUser_json["status"] == "success":
                Variable.store_session(signupUser_json["authorization"])

                flash(signupUser_json["payload"], "success")

                return redirect(url_for("home"))

            else:
                flash(signupUser_json["payload"], "danger")

                return redirect(url_for("login"))

    return render_template("signup_part_two.html", title="Sign up", signupPartTwoForm=signupPartTwoForm)
    
@boop.route("/login", methods=["GET", "POST"])
@inaccesible_if_authenticated
def login():
    loginForm = LoginForm()

    if request.method == "POST":
        if loginForm.validate_on_submit():
            form = request.form

            loginUser_json = Auth.login_user(form)
            
            if loginUser_json["status"] == "success":
                Variable.store_session(loginUser_json["authorization"])

                flash(loginUser_json["payload"], "success")

                return redirect(url_for("home"))

            else:
                flash(loginUser_json["payload"], "danger")

                return redirect(url_for("login"))
            
    return render_template("login.html", title="Welcome", loginForm=loginForm)

@boop.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = ShareContentForm()
    current_user_page = False
    current_user = User.get_current_user()
    
    posts = Post.get_all_posts()["data"]
    
    display_posts = []

    for x, post in enumerate(posts):
        author = User.get_a_user(post["post_author"])

        dict = {}

        dict["public_id"] = post["public_id"]
        dict["content"] = post["content"]
        dict["posted_on"] = post["posted_on"]
        dict["author_firstName"] =  author["first_name"]
        dict["author_lastName"] = author["last_name"]
        dict["author_username"] = author["username"]
        dict["author_profPhoto_filename"] = author["profPhoto_filename"]
        display_posts.append(dict)

    return render_template("home.html", title="Home", current_user=current_user, all_posts=display_posts, shareContentForm=form, username=current_user["username"] )

@boop.route("/admin/users/all", methods=["GET"])
@login_required
def all_users():
    current_user = User.get_current_user()

    users = User.get_all_users()["data"]

    return render_template("manage_user.html", title="All Users", current_user=current_user, users=users)

@boop.route("/<username>/pets", methods=["GET", "POST"])
@login_required
def user_profile_pets(username):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)

    user_existence = Helper.user_existence_check(user_json)
    if user_existence is False:
        abort(404)

    userPets = Pet.get_user_pets(username)["data"]

    addPetForm = AddPetForm()
    updateUserForm = UpdateUserForm()

    if username == current_user["username"]:
        current_user_page = True

        Helper.modify_addPetForm(addPetForm)

        if request.method == "POST":
            addPetForm.breed_input.choices = [(request.form.get("breed_input"), "")]

            if addPetForm.validate_on_submit():
                addPet_json = Pet.add_a_pet(request)

                if addPet_json["status"] == "success":
                    flash(addPet_json["payload"], "success")

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))

                else:
                    flash(addPet_json["payload"], "danger")

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))
            
            if updateUserForm.validate_on_submit():
                updateUser_json = User.update_user(request)
                
                if updateUser_json["status"]  == "success":
                    flash(updateUser_json["payload"], "success")

                    current_user = User.get_current_user()

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))
                
                else:
                    flash(updateUser_json["payload"], "danger")

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_pets", username=current_user["username"]))
        
        elif request.method == "GET":
            updateUserForm.firstName_input.default = current_user["firstName"]
            updateUserForm.lastName_input.default = current_user["lastName"]
            updateUserForm.email_input.default = current_user["email"]
            updateUserForm.username_input.default = current_user["username"]
            updateUserForm.contactNo_input.default = current_user["contactNo"]

            updateUserForm.process()

    return render_template("user_profile.html", title="Account", current_user_page=current_user_page, current_user=current_user, user=user_json, user_pets=userPets, addPetForm=addPetForm, updateUserForm=updateUserForm, petsNavActivate="3px #00002A solid")

@boop.route("/<username>/posts", methods=["GET", "POST"])
@login_required
def user_profile_posts(username):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)
    post_json = Post.get_user_posts(username)
    posts = Post.get_all_posts()["data"]
    comments = Comment.get_all_comments()["data"]

    if user_existence is False:
        abort(404)


    posts = Post.get_user_posts(username)["data"]

    display_posts = []

    for x, post in enumerate(posts):
        author = User.get_a_user(post["post_author"])

        dict = {}

        dict["public_id"] = post["public_id"]
        dict["content"] = post["content"]
        dict["posted_on"] = post["posted_on"]
        dict["author_firstName"] =  author["first_name"]
        dict["author_lastName"] = author["last_name"]
        dict["author_username"] = author["username"]

        display_posts.append(dict)

    updateUserForm = UpdateUserForm()
    commentPostForm = CommentPostForm()
    shareContentForm = ShareContentForm()

    if username == current_user["username"]:
        current_user_page = True

        userPets_json = Pet.get_user_pets(username)

        if request.method == "POST":
            
            if shareContentForm.validate_on_submit():
                shareContent_json = Post.new_post(request)
                
                if shareContent_json["status"] == "success":
                    
                    flash(shareContent_json["payload"], "success")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))

                else:
                    flash(shareContent_json["payload"], "danger")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_posts", username=current_user["username"]))

    return render_template("user_profile.html", title="Account", commentPostForm = commentPostForm, updateUserForm=updateUserForm, post_json=post_json, current_user_page=current_user_page, current_user=current_user, user=user_json, user_posts=display_posts, shareContentForm=shareContentForm, comments=comments, postsNavActivate="3px #00002A solid")

@boop.route("/<username>/gallery", methods=["GET", "POST", "PUT"])
@login_required
def user_profile_gallery(username):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)
    post_json = Post.get_user_posts(username)
    posts = Post.get_all_posts()["data"]
    comments = Comment.get_all_comments()["data"]

    if user_existence is False:
        abort(404)

    userGallery = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]
    
    updateUserForm = UpdateUserForm()

    if username == current_user["username"]:
        current_user_page = True

        userPets_json = Pet.get_user_pets(username)

        if request.method == "POST":
            
            if shareContentForm.validate_on_submit():
                shareContent_json = Post.new_post(request)
                
                if shareContent_json["status"] == "success":
                    
                    flash(shareContent_json["payload"], "success")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))

                else:
                    flash(shareContent_json["payload"], "danger")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_posts", username=current_user["username"]))

    return render_template("user_profile.html", title="Account", updateUserForm=updateUserForm, post_json=post_json, current_user_page=current_user_page, current_user=current_user, user=user_json, user_gallery=userGallery, galleryNavActivate="3px #00002A solid")

@boop.route("/<username>/likes", methods=["GET", "POST", "PUT"])
@login_required
def user_profile_likes(username):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)

    if user_existence is False:
        abort(404)

    updateUserForm = UpdateUserForm()

    if username == current_user["username"]:
        current_user_page = True

        Helper.modify_addPetForm(addPetForm)

        if request.method == "POST":
            addPetForm.breed_input.choices = [(request.form.get("breed_input"), "")]
            if addPetForm.validate_on_submit():
                addPet_json = Pet.add_a_pet(request)

                if addPet_json["status"] == "success":
                    flash(addPet_json["payload"], "success")

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))

                else:
                    flash(addPet_json["payload"], "danger")

                    return redirect(url_for("user_profile_pets", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_pets", username=current_user["username"]))

    return render_template("user_profile.html", title="Account", current_user_page=current_user_page, current_user=current_user, user=user_json, user_pets=userPets, addPetForm=addPetForm, updateUserForm=updateUserForm, likesNavActivate="3px #00002A solid")

@boop.route("/<username>/posts/<post_id>/comment", methods=["GET", "POST"])
@login_required
def comment(username, post_id):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)
    post_json = Post.get_user_posts(username)

    if user_existence is False:
        abort(404)

    userPosts = Post.get_user_posts(username)["data"]
    commentPostForm = CommentPostForm()

    if username == current_user["username"]:
        current_user_page = True

    if request.method == "POST":
            if commentPostForm.validate_on_submit():
                commentPost_json = Comment.new_comment(request,post_id)
                

                if commentPost_json["status"] == "success":
                    
                    flash(commentPost_json["payload"], "success")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))

                else:
                    flash(commentPost_json["payload"], "danger")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_posts", username=current_user["username"]))

    return redirect(url_for("user_profile_posts", username=current_user["username"]))
   

@boop.route("/<username>/posts/<post_id>/delete", methods=["GET","POST","DELETE"])
@login_required
def delete_post(post_id, username):
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    post_json = Post.get_user_posts(username)

    if username == current_user["username"]:
        current_user_page = True
        
        Post.delete_post(post_id)


    return redirect(url_for('user_profile_posts',username=current_user["username"]))

@boop.route("/<username>/pets/<public_id>", methods=["GET", "POST"])
@boop.route("/<username>/pets/<public_id>/wall", methods=["GET", "POST"])
@login_required
def pet_profile_wall(username, public_id):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)

    if user_existence is False:
        abort(404)

    pet_json = Pet.get_a_pet(public_id)
    pet_existence = Helper.pet_existence_check(pet_json)
    
    if pet_existence is False:
        abort(404)

    owner_list = User.get_pet_owners(pet_json["public_id"])["data"]

    for user in owner_list:
        if current_user["username"] == user["username"]:
            current_user_page = True

    pet_json["birthday"] = Helper.datetime_str_to_datetime_obj(pet_json["birthday"])  

    return render_template("pet_profile.html", title="Account", public_id=public_id, current_user_page=current_user_page, current_user=current_user, user=user_json, pet=pet_json, owner_list=owner_list, postsNavActivate="3px #00002A solid")


@boop.route("/<username>/pets/<public_id>/delete", methods=["GET","POST","DELETE"])
@login_required
def delete_pet(public_id, username):
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    pet_json = Pet.get_a_pet(public_id)
    pet_existence = Helper.pet_existence_check(pet_json)

    if pet_existence is False:
        abort(404)
    
    if username == current_user["username"]:
        current_user_page = True
        
        Pet.delete_pet(public_id)
     
    pet_json["birthday"] = Helper.datetime_str_to_datetime_obj(pet_json["birthday"])  

    return redirect(url_for('user_profile_pets',username=current_user["username"]))
'''
@boop.route("/<username>/pet/<pet_id>/deal", methods=["GET", "POST"])
@login_required
def deal_pet(username, pet_id):
    current_user_page = False
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    user_existence = Helper.user_existence_check(user_json)

    if user_existence is False:
        abort(404)

    dealPetForm = DealPetForm()

    if username == current_user["username"]:
        current_user_page = True

    if request.method == "POST":
            print('comment bitchhh')
            if dealPetForm.validate_on_submit():
                dealPet_json = Deal.new_deal(request,pet_id)
                
                print('deal routes')
                if dealPet_json["status"] == "success":
                    
                    flash(dealPet_json["payload"], "success")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))

                else:
                    flash(dealPet_json["payload"], "danger")
                    
                    return redirect(url_for("user_profile_posts", username=current_user["username"]))
            
            else:
                flash("Try again.", "danger")
                
                return redirect(url_for("user_profile_posts", username=current_user["username"]))

    return redirect(url_for("pet_profile_wall",username=current_user["username"]))
'''   

@boop.route("/<username>/pets/<public_id>/update", methods=["GET","PUT","DELETE"])
@login_required
def update_pet(public_id, username):
    current_user = User.get_current_user()
    user_json = User.get_a_user(username)
    pet_json = Pet.get_a_pet(public_id)
    pet_existence = Helper.pet_existence_check(pet_json)


    if pet_existence is False:
        abort(404)
    
    if username == current_user["username"]:
        current_user_page = True
        
        Pet.update_pet(public_id)
     
    pet_json["birthday"] = Helper.datetime_str_to_datetime_obj(pet_json["birthday"])  

    return redirect(url_for('pet_profile_wall',username=username, public_id=public_id))

@boop.route("/post/<public_id>", methods=["GET", "POST"])
@login_required
def display_post(public_id):
    current_user_page = False
    current_user = User.get_current_user()
    post = Post.get_a_post(public_id)
    post_owner = User.get_a_user(post["post_author"])

    comments = Comment.get_rel_comment(public_id)
    display_comments = []
    print(comments)
    if comments:
        for x, comment in enumerate(comments):
            author = User.get_a_user(comment["posted_by"])

            dict = {}

            dict["content"] = comment["comment"]
            dict["author_username"] = comment["posted_by"]
            dict["author_firstName"] = author["first_name"]
            dict["author_lastName"] = author["last_name"]
            dict["posted_on"] = comment["posted_on"]
            dict["profPhoto_filename"] = author["profPhoto_filename"]

            display_comments.append(dict)

    commentPostForm = CommentPostForm()

    if request.method == "POST":
        if commentPostForm.validate_on_submit():
            commentPost_json = Comment.new_comment(request, public_id)
            
            if commentPost_json["status"] == "success":
                
                flash(commentPost_json["payload"], "success")
                
                return redirect(url_for("display_post", public_id=public_id))

            else:
                flash(commentPost_json["payload"], "danger")
                
                return redirect(url_for("display_post", public_id=public_id))
        
        else:
            flash("Try again.", "danger")
            
            return redirect(url_for("user_profile_posts", username=current_user["username"]))

    return render_template("post.html", title="Post", commentPostForm=commentPostForm, post=post, display_comms=display_comments, post_owner=post_owner, current_user=current_user)

@boop.route("/<username>/pets/<public_id>/media", methods=["GET", "POST"])
@login_required
def pet_profile_media(username, public_id):
    return redirect(url_for("pet_profile_wall", username=username, public_id=public_id))

@boop.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.pop("booped_in")

    return redirect(url_for("welcome"))