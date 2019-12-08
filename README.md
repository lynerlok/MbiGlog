# MbiGlog

## The server depends of virtualenvwrapper ( see https://pypi.org/project/virtualenvwrapper/)
 
Here all instructions to install and run the server :

1. Install virtualenvwrapper (e.g `pip install virtualenvwrapper` or `pip install --user virtualenvwrapper`)

3. Export your env variable (e.g `export WORKON_HOME=/<path>/<to>/<MbiGlog>/`)

4. Save the env var in your system (e.g `echo export WORKON_HOME=/<path>/<to>/<MbiGlog> >> ~/.bashrc`)
 
5. Activate virtualenvwrapper (e.g `source /usr/local/bin/virtualenvwrapper.sh`)

5. Change directory to the root of the project (e.g `cd MbiGlog`)

6. Create the python virtual environment (e.g `mkvirtualenv PythonVenv`)

7. The first time the python virtual environment is activated automaticaly, then activate manualy (e.g `workon PythonVenv`)

8. You are in the venv (you can see `(PythonVenv)` before prompt $)

9. Modify PythonVenv/bin/postactivate and put these lines :
	
	`export DATABASE_NAME='djangoDev'`<br />
	`export DATABASE_USER='DBdev'`<br />
	`export DATABASE_PASSWORD='NohJah8o'`<br />
	`export SECRET_KEY=<put your secret key generated with https://miniwebtool.com/django-secret-key-generator/ for example>'`

10. Modify PythonVenv/bin/predeactivate and put these lines :

	`unset DATABASE_NAME` <br />
	`unset DATABASE_USER` <br />
	`unset DATABASE_PASSWORD` <br />
	`unset SECRET_KEY`

11. Now, install all dependancies (or just your dependancies in this case comments in requirments.txt undesired deps) (e.g `pip install -r requirments.txt`)

12. Take a coffee, it can take a long time.

13. Deactivate the venv (e.g `deactivate`)

14. Edit startServer.sh with your IP addr and your PORT.

15. Run startServer.sh (e.g `./startServer.sh`)

16. Connect to the server using your web browser (http://<IP>:<PORT>)

17. Perform your test !

18. OPTIONAL : To use the main database server rename DjangoProjects/glogServer/settings.py.prod into settings.py (make your backup before)

19. Make a pull request on Github if your test is conclusive.

20. Be patient, I will process your request as soon as possible.

21. Your request is added to the main code !

## NOTE : TO update forked repository please make a pull request between this repo and your repo !
## AT THIS TIME the databases server reject connection (port 5432) so be patient I debug (please no flooding in issue)

