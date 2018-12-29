Book Catlog is a web app for organising Books. Users can view a list of categories of books and books under each category. Users an log-in using their Google authentication. Logged-in users can add, edit and delete book details.

* Pre-requisites:
	- Install and set up the Virtual Machine
		- Set up a terminal. If you are using a Mac or Linux system, you can use your regular terminal program. On Windows, you can download Git from git-scm.com and use the Git Bash terminal.
		- Install virtual box platform package for your operating system from https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
		- Install Vagrant version for your operating system from https://www.vagrantup.com/downloads.html.
		- Unzip 'Item Catalog Project.zip' to the location where you want to run the application from.
		- Open terminal at the Catalog App directory and navigate to vagrant directory 
		- Start virtual machine using command $vagrant up
		- Log into virtual machine using command $vagrant ssh
	- Set up data
		- from the command line, excute the command
			$  python model.py
		- from the command line, excute the command
			$  python populatedb.py
* Running the server:
	- Open terminal at the Catalog App directory and navigate to vagrant directory 
	- Start virtual machine using command $vagrant up
	- Log into virtual machine using command $vagrant ssh
	- from the command line, excute the command
			$  python application.py

* Accessing the Book Catalog App:
	- Open your browser and go to url http://localhost:5000

* Accessing the Book Catalog App JSON endpoints:
	- following are the urls for the JSON APi endpoints:
		- http://localhost:5000/api/catalog/JSON
		- http://localhost:5000/api/catalog/category/<category_name>/JSON
		- http://localhost:5000/api/catalog/item/<item_name>/JSON


