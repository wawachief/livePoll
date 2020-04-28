# livePoll
Interactive poll to use during youtube live sessions

This is more a Proof of Concept rather than a finished product, but it gets the job done !

- first you have to type the questions and the answers inside the views.py file
- run the python script (python 3.7 minimum with flask module)

The web server listens to http://your_server:5000/

There are three web pages :
- http://your_server:5000/index.html : address to give to your students. The questions will appear there
- http://your_server:5000/admin.html : the admin page allows you to select the active question
- http://your_server:5000/bilan.html : to see the results of the polls. The green backgroud allows incrustation inside OBS

# Todo
Lots of things !
maybe first thing : restrict bilan and admin pages to localhost

enjoy
