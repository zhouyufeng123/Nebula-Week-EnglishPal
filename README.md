EnglishPal - Learn English Words Smartly
==========================================


Hui Lan <hui.lan@cantab.net>

1 November 2019


What is it?
-----------------

EnglishPal allows the user to build his list of new English words
picked from articles selected for him according his vocabulary level.


Run it on a local machine
-------------------------

python3 main.py



Run it within Docker
--------------------

Assuming that docker has been installed and that you are a sudoer ...

ssh to ubuntu@118.25.96.118

cd to /home/lanhui/englishpal

\#  Stop all docker service

sudo service docker restart

\#  If you know the container ID, then the above comamnd is an overkill.  Use the following command instead.

sudo docker stop ContainerID

\#  You could get all container ID with the following command.

sudo docker ps 

\#  Rebuild container. Run this after modifying the source code.

sudo docker build -t englishpal .

\#  Run the application

sudo docker run -d -p 90:80 -v /home/lanhui/englishpal/app/static/frequency:/app/static/frequency -t englishpal  \#  for permanently saving data

sudo docker run -d -p 90:80 -t englishpal \#  data will be lost after existing

\#  Save space.  Run it after sudo docker run

sudo docker system prune -a -f


\#  Other commands

sudo docker ps -a

sudo docker logs image_name, where image name could be obtained from sudo docker ps.

build.sh contains all the above commands.  Run "sudo ./build.sh" to rebuild the web application.



Update articles
---------------

All articles are stored in the `article` table in a SQLite file called
`app/static/wordfreqapp.db`.

### Adding new articles

To add articles, open and edit `app/static/wordfreqapp.db` using DB Browser for SQLite (https://sqlitebrowser.org).

Export wordfreqapp.db to wordfreqapp.sql using the following commands:

- sqlite3 wordfreqapp.db

- .output wordfreqapp.sql

- .dump

- .exit

Put wordfreqapp.sql (not wordfreqapp.db) under version control.

### Creating SQLite file from wordfreqapp.sql

Create wordfreqapp.db using this command: `cat wordfreqapp.sql |
sqlite3 wordfreqapp.db`.  Delete wordfreqapp.db first if it exists.

### Uploading wordfreqapp.db

pscp wordfreqapp.db lanhui@118.25.96.118:/home/lanhui/englishpal/app/static



Feedback
---------


### Respondent 1 -- Tianhua


Need a phone app.  I use phone a lot.  You cannot ask students to use computers.

Can take a picture for text.  Automatic translation.

### Respondent 2 --- Paid 10 yuan


“成为会员”改成“注册”

“登出”改成“退出”

“收集生词吧”改成“生词收集栏”

***不要自动显示下一篇

需要有“上一篇”、“下一篇”

### TODO


Fix Bug: Internal server error when register using email address.

Usability testing


Improvements made by contributors
-----------------------------------

- 朱文绮

在生词簿每个单词后面，加上两个按钮，熟悉与不熟悉:

1.如果点熟悉，就将生词簿中该单词后面记录的添加次数减一，直至减为0，就将该单词从生词簿中移除。

2.如果点不熟悉，就将生词簿中该单词后面记录的添加次数加一。

- 李康恬

Add the function of "Delete already known and well-known words from
the words' library", on the one hand, it can conform to the usage
habits of some users, who do not like that their words' libraries have
too many words that they already know, on the other hand, it can
reduce unnecessary memory occupied by the database, in addition, it
can also improve the simplicity of the page.

More information at: http://118.25.96.118/kanboard/?controller=TaskViewController&action=readonly&task_id=736&token=81a561da57ff7a172da17a480f0d421ff3bc69efbd29437daef90b1b8959


- 占健豪

Click the Familiar or Unfamiliar button (current word frequency>1), the current word position is displayed at the top of the page;

Click the Familiar or Unfamiliar button (current word frequency is 1), and the page will be displayed as the top of the entire page.

Demo video link: https://b23.tv/QuB77m

- 张小飞

修复了以下漏洞。

漏洞：用****这段字符可以作为任何账号的密码登录。

Bug report: http://118.25.96.118/bugzilla/show_bug.cgi?id=215


*Last modified on 2021-07-16*