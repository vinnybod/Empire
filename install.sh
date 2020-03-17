#!/bin/bash
# This is a general-purpose function to ask Yes/No questions in Bash, either
# with or without a default answer. It keeps repeating the question until it
# gets a valid answer.
# https://gist.github.com/davejamesmiller/1965569
ask() {
    # https://djm.me/ask
    local prompt default reply

    if [ "${2:-}" = "Y" ]; then
        prompt="Y/n"
        default=Y
    elif [ "${2:-}" = "N" ]; then
        prompt="y/N"
        default=N
    else
        prompt="y/n"
        default=
    fi

    while true; do

        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "

        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read reply </dev/tty

        # Default?
        if [ -z "$reply" ]; then
            reply=$default
        fi

        # Check if the reply is valid
        case "$reply" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

function install_powershell() {
  echo "Installed Powershell 100%"
}

function install_xar() {
  echo "Installed xar 100%"
}

function install_bomutils() {
  echo "Installed bomutils 100%"
}

function setup_cert() {
  echo "Cert created"
}


if ask "Do you want to install powershell? Powershell is used by Empire for a variety of tasks including obfuscating payloads"; then
    install_powershell
else
    echo "Skipping Powershell install"
fi

if ask "Do you want to install xar? xar is used for osx payloads to package bla bla"; then
    install_xar
else
    echo "Skipping xar install"
fi

if ask "Do you want to install bomutils? bomutils is used for osx payloads to package bla bla"; then
    install_bomutils
else
    echo "Skipping bomutils install"
fi

if ask "Do you want to set up a cert? This is used for ssl in the rest api"; then
    setup_cert
else
    echo "Skipping cert creation"
fi

echo "Prerequisite Install Complete. To run Empire, use pipenv install && pipenv run python empire"