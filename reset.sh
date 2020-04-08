#!/bin/bash

# reset the database
if [ -e data/empire.db ]
then
	rm data/empire.db
fi

pipenv run python ./setup_database.py

# remove the debug file if it exists
if [ -e empire.debug ]
then
	rm empire.debug
fi

# remove the download folders
if [ -d ./downloads/ ]
then
	rm -rf ./downloads/
fi
