# Contributing guidelines


## Contents

1. [Reporting issues](#reporting-issues)
1. [Contributing a patch](#contributing-a-patch)
2. [Setup for development](#setup-for-development)
3. [Testing](#testing)
4. [Coding conventions](#coding-conventions)


## Reporting issues

Open an issue and fill each field of the issue template, unless you have a reason to not fill some field.


## Contributing a patch

1. Submit an issue describing your proposed change to the repo in question.
2. Some repo maintainer will respond to your issue promptly.
3. Fork the repo and [set your environment up](#set-up-for-development) for development.
4. Develop your changes following our [coding conventions](#coding-conventions), add tests to your change and
   [run](#testing) them locally.
5. Submit a pull request.


## Setup for development

Install virtualenvwrapper.

```
pip install virtualenv virtualenvwrapper
```

After installing virtualenvwrapper please add the following line to your shell startup file (e.g. ~/.zshrc, again if you haven't):

```
source /usr/local/bin/virtualenvwrapper.sh
```

Reset your terminal.

Clone this respository, create the virtual environment, install some dependencies and run:

```
$ GIHUB_USERNAME="your_username"
$ git clone https://github.com/$GITHUB_USERNAME/travieso
$ cd travieso
$ mkvirtualenv travieso
$ workon travieso
$ pip install -r requirements.txt
$ gem install foreman
$ foreman start
```


## Testing

To run the tests, you just do:

```
$ pip install tox
$ tox
```


## Coding conventions

We use `editorconfig` to define our coding style. Please [add editorconfig](http://editorconfig.org/#download)
to your editor of choice.

When running `tox` linting will also be run along with the tests. You can also run linting only by doing:

```
$ tox -e flake8
```
