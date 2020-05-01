# livePoll
Interactive poll to use during youtube live sessions

This is a work in progress, but it gets the job done !

- first you have to type the questions and the answers inside the views.py file
- there are generic questions Yes/No, True/False, choices by default but you can change them
- run the python script (python 3.7 minimum with flask module) : `python3 views.py`

The web server listens to http://your_server:5000/

There are three web pages :
- http://your_server:5000/ : address to give to your students. The questions will appear there
- http://your_server:5000/admin.html : the admin page allows you to select the active question
- http://your_server:5000/bilan1 : to see the results of the polls. The green backgroud allows incrustation inside OBS

# usage
- The students's page refreshes automagically. They don't have anything else to do but answering the questions when the teacher pushes them.
- the teacher chooses the questions from the admin page.
- the bilan1 page is designed to be displayed within OBS. The green background allows transparency using the *chroma key* filter.
![screen1](screen1.png)

# Todo
Lots of things !
maybe first thing : restrict bilan and admin pages to localhost

enjoy
