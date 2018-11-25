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
* A vocabulary_populator.py file to populate the database with a few users, languages and words.
* A morewords.py file with all views and json endpoints.  
* A /templates directory with all templates.  
* A /static directory containing a css directory with the css stylesheet.  

## Requirements
This app runs on a Udacity Virtual Machine.  
In order to run this code you need to install [Git](https://git-scm.com/downloads), [Virtual Box](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) and [Vagrant](https://www.vagrantup.com/downloads.html).  
Then you can fork the Virtual Machine at https://github.com/udacity/fullstack-nanodegree-vm and clone the remote to your local machine.  
To run your local VM go into the vagrant directory by typing `cd fullstack/vagrant` and launch the VM with `vagrant up` and once it's up `vagrant ssh`. To go into the shared folder type `cd /vagrant`. To log out just type `exit`.


## How to Run it
Download the project zip file and unzip it.  
Or clone this repository:  
https://github.com/lalluz/morewords.git

In your terminal, inside the up and running VM, navigate to the project root directory and type `python database_setup.py` to create the database structure.  

If you want you can optionally populate the database with a few data by typing `python vocabulary_populator.py`.  
You will find three test users:  
[user_1, user_1<span>@</span>example.com, password_1],  
[user_2, user_2<span>@</span>example.com, password_2],  
[user_3, user_3<span>@</span>example.com, password_3].  

Run the app by typing ` python morewords.py `.  
The app is now running on port 5000 and you can open it in your browser at this url: http://localhost:5000/.  
When you are done hit ` CTRL+C ` in your terminal to exit the server.

## MoreWords API
All endpoints use only the **GET** HTTP Method.  
The API responds with the application/jsoncontent­type.  
ENDPOINT URIs:
* **/api/v0/vocabulary** - List all words grouped by language.  
* **/api/v0/languages** - List all languages.  
* **/api/v0/words** - List all words.  
* **/api/v0/languages/[language_name]/words** - List all words in a given language.  
* **/api/v0/languages/[language_name]/words/[word_name]>** - List all entries for a given word in a given language.  
* **/api/v0/words/[word_name]>** - List all entries for a given word in any language.  

## Licence
MIT Licence.
