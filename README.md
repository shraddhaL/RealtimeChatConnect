# RealtimeChatConnect

This project serves as the backend logic (providing webservices) for application providing functionality to facilitate group chat, manage user and group data, and enable real-time group chat between users. 
It leverages HTTP calls documented using Swagger, ensuring clear communication and understanding of the available APIs. 

Server-side framework used: Django

The backend logic includes features for user and group management, allowing users to create, join, and interact within groups. Additionally, the project incorporates real-time communication capabilities, enabling users to engage in group chat in real-time

Steps to setup this project in your local machine:

1. You need to have MySQL installed
2. Create a schema named 'chatapp'. You can use below query.
   ```python
   CREATE SCHEMA `chatapp` ;
   ```
3. Create and apply migrations
   You can use below commands
   ```python
    python manage.py makemigrations
    python manage.py migrate
   ```
   If these commands do not work, you can use the ones below. Also, I recommend to drop and re-create the schema
   ```python
   DROP SCHEMA `chatapp` ;
   CREATE SCHEMA `chatapp` ;
   ```
   Then on the terminal run
   ```python
    python manage.py makemigrations users
    python manage.py migrate users
    python manage.py makemigrations groupchat
    python manage.py migrate groupchat
    python manage.py makemigrations
    python manage.py migrate
   ```
4. Load the Data for admin user with below command.
   ```python
   python manage.py loaddata initial_data
   ```
5. Start a Daphne server for our ASGI (Asynchronous Server Gateway Interface) application named ChatConnect
   ```python
   daphne -p 8080 ChatConnect.asgi:application
   ```
6. To test the Consumer for RealTime Chat run
   ```python
   python manage.py test ChatConnect.tests.GroupChatConsumerTestCase
   ```
7. To run all the e2e tests in the application run
   ```python
   python manage.py test
   ```
8. To run the application
   ```python
   python manage.py runserver
   ```

Admin User:

username: admin

password: admin
