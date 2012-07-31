=======
cronurl
=======

cronurl reads URL periodically and emails the results. It uses a cron-like
scheme to find out when a specific URL is read from. 

Features:

    * configuration stored in a database
    * gevent for a lightweight CPU usage

cronurl is meant to run as a daemon. Use other tools to daemonize the process, e.g.
supervisord, or upstart/init/start-stop-daemon.

