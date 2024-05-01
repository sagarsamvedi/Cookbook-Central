from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from .models import Dish
from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.warning(request, "Please fill out all required fields.")
            return render(request, 'user/login.html')
        
        user = authenticate(request, username= username,password= password)
        if user is not None:
            login(request,user)
            messages.success(request, "Login successful.")
            return redirect('/home/')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'user/login.html')

def signup_page(request):
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not name or not email or not password:
            messages.warning(request, "Please fill out all required fields.")
            return render(request, 'user/signup.html')

        if User.objects.filter(username = email).exists():
            messages.error(request, "Email Already Taken")
            return render(request, 'user/signup.html')

        user_obj = User.objects.create(username=email, email=email, first_name=name)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, "User created successfully. Please log in.")
        return redirect('/login/')  # Redirect to the login page after successful registration
        
    return render(request, 'user/signup.html')

@login_required
def home_page(request):
    query = request.GET.get('query')  # Get the search query from the request parameters
    print(query)
    if query:
        # Perform a case-insensitive search for dishes by name or user (username)
        dishes = Dish.objects.filter(name__icontains=query) | Dish.objects.filter(user__username__icontains=query)
    else:
        dishes = Dish.objects.all()
    context = {
        'dishes' : dishes
    }
    return render(request, 'dishes/dishes.html',context)

@login_required  # Apply login_required decorator to ensure only authenticated users can access this view
def add(request):    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_file = request.FILES.get('image')

        
        if name and description:
            # Create a new Dish object with the provided data and associate it with the logged-in user
            new_dish = Dish.objects.create(
                user=request.user,
                name=name,
                description=description,
                image=image_file if image_file else None  # Assign image_file or None if no image was uploaded
            )
            new_dish.save()
            return redirect('/home/')  # Redirect to a view showing a list of dishes

    return render(request, 'dishes/add.html')

def update(request,id):
    #Retrieve the existing Dish object using the primary key (pk)
    dish = Dish.objects.get(id = id)
    if request.user != dish.user:
        messages.warning(request,"This dish does not belong to you. Can't UPDATE")
        return redirect('/home/')  
    elif request.method == 'POST':
        # Retrieve updated data from the request
        name = request.POST.get('name')
        description = request.POST.get('description')
        image_file = request.FILES.get('image')

        # Update the Dish object with the new data
        if name and description:
            dish.name = name
            dish.description = description
            if image_file:
                dish.image = image_file
            dish.save()
            return redirect('/home/')  # Redirect to the home page or a relevant view

    return render(request, 'dishes/update.html', {'dish': dish})

def delete(request,id):
    if request.user == Dish.objects.get(id=id).user:
        dish = Dish.objects.get(id=id)
        dish.delete()
        return redirect('/home/')
    else:
        messages.warning(request,"This dish does not belong to you. Can't DELETE")
        return redirect('/home/')
    
def logout_page(request):
    logout(request)
    messages.warning(request,"Logged Out")
    return redirect('/login/')

def send_dish_email(request, dish_id):
    if request.method == 'POST':
        email = request.POST.get('email')
        dish = Dish.objects.get(pk=dish_id)

        subject = f"Dish Details: {dish.name}"
        message = f"Name: {dish.name}\n\nDescription: {dish.description}\n\nChef: {dish.user.first_name.capitalize()}"
        sender =  settings.EMAIL_HOST_USER
        recipient_list = [email]

        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=sender,
            to=recipient_list
        )
        if dish.image:
            mail.attach_file(dish.image.path)
        # Send the email
        mail.send()

        messages.success(request, f"Email sent successfully to {email}.")
        return redirect('/home/')

    # If the request method is not POST, render your template with the dish object
    dish = Dish.objects.get(pk=dish_id)
    return render(request, 'your_template.html', {'dish': dish})