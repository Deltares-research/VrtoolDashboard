Grant access to testers/users BEFORE deploying phase, locally:
1. Make repository public and they run the dashboard locally.
2. If repo is private, make a distribution wheel of the dashboard and have the user install it locally.
3. If repo is private, make a docker image of the dashboard and have the user run it locally.
4. If repo is private, have a standalone executable of the dashboard and have the user run it locally.


Grant access to testers/users AFTER deploying phase, remotely:
5. Deploy a staging environment on a dummy platform. (e.g. Heroku)
