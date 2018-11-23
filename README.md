# MoreWords
A [Udacity Full Stack Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) project.  
A multi-user Flask application to store and review words in different languages.

## What it Does
This responsive app is a personal vocabulary that lets users add languages, words, translations, notes and review them.  
Not registered users will see all languages and words present in the app, but they won't be able to create, edit or delete any of them.  
A user can signup and signin with Google, Facebook or directly in the app and create, edit, delete and review his/her own words.  
Once a word has been learned the user can check the 'learned' checkbox in the word detail page and the word will be no longer displayed in the review.  
This app also has an API that lets developers query the database. See [MoreWords API](#MoreWords-API).

## Project Contents

This project contains:
* A database_setup.py file with the model classes to set up the database.
* A morewords.py file with all views and json endpoints.
* A /templates directory with all templates.
* A /static directory containing a css directory with the css stylesheet.

## Requirements
This app runs on a Udacity Virtual Machine.  
In order to run this code you need to install Git, Virtual Box and Vagrant.  
Then you can fork the Virtual Machine at https://github.com/udacity/fullstack-nanodegree-vm and clone the remote to your local machine.  
To run your local VM go into the vagrant directory by typing `cd fullstack/vagrant` and launch the VM with `vagrant up` and once it's up `vagrant ssh`. To go into the shared folder type `cd /vagrant`. To log out just type `exit`.


## How to Run it
Download the project zip file and unzip it.  
Or clone this repository:  
https://github.com/lalluz/morewords.git

In your terminal, inside the up and running VM, navigate to the project root directory and type `python database_setup.py` to create the database structure.  
Now run the app by tiping ` python morewords.py `.  
The app is now running on port 5000 and you can open it in your browser at this url: http://localhost:5000/.  
When you are done hit ` CTRL+C ` in your terminal to exit the server.

## MoreWords API
All endpoints use only the **GET** HTTP Method.  
The API responds with the application/jsoncontent­type.  
ENDPOINT URIs:
* /api/v0/vocabulary
* /api/v0/languages
* /api/v0/words
* /api/v0/languages/[language_name]/words
* /api/v0/languages/[language_name]/words/[word_name]>
* /api/v0/words/[word_name]>

## Licence
MIT Licence.
