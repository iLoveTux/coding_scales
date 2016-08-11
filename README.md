# coding_scales
A typing tutor focusing on programming. 

## What is it?

coding_scales is a web app written in flask designed to provide a new and novel way to practice both
typing and computer programming. It is released as open source under the GNU Afero Public license
and provided as a web app available under a $1 per month membership fee. I think this is a good way
to improve ones craft whatever their role in computing.

## Why charge for it?

coding_scales is released as open source so you can do pretty much what you want with it, but
since I think this is a good idea I would like to continue to develop it. The $1 monthly fee is
to make sure that it doesn't get left behind. Also, I would like to someday use a portion of the
proceeds to host competitions.

## So whats the big idea?

If you wish to become impressive to a non-developer the number one thing you can do is increase
your typing speed. This is not to say that programming ability is somehow linked to typing speed,
I am meerly saying that to an outside observer fast typing speed is impressive. Not only that, but
I have found that by increasing my typing speed has vastly improved my development process. The
faster I can express myself the better able I am to do so.

## How does it work?

Well there is an api to retrieve collections of exercises exposed through a HTTP based REST interface.
This REST interface is built with flask, flask\_restful, flask\_sqlalchemy and flask_login. On the client
side is a web app built with JQuery, Mustache.js, codemirror and bootstrap.

When you log in you can select a single exercise or a collection of exercises you can perform in series. An
exercise has a snippit of code which is displayed on the left and an empty codemirror editor into which
you must type the snippit. Once the value matches, the exercise is complete and your words per minute, total time
and other statistics will be displayed.

## Contributing

All the code is available on Github, so you can do all the normal Github stuff. Please make sure that any
contributions in the form of code should be presentable and acompanied by tests. All forms of contributions
are greatly appreciated, please consider submitting issues in our issue tracker for any improvements.

## Running the tests.

You can run the tests with the following command executed in the repository root:

```
$ python setup.py test
```

or alternately

```
nosetests
```

## The documentation

Check us out on readthedocs

Check out the wiki

look through past issues

current issues
