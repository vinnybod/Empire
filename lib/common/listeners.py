"""

Listener handling functionality for Empire.

"""
from __future__ import absolute_import
from __future__ import print_function

import copy
import fnmatch
import hashlib
import imp
import json
import os
import pickle
from builtins import filter
from builtins import object
from builtins import str

from pydispatch import dispatcher
from sqlalchemy.sql.elements import or_

from lib.common.config import InternalConfig
from lib.database import models
from lib.database.base import Session
from . import helpers


class Listeners(object):
    """
    Listener handling class.
    """

    def __init__(self, MainMenu, args):

        self.mainMenu = MainMenu
        self.args = args

        # loaded listener format:
        #     {"listenerModuleName": moduleInstance, ...}
        self.loadedListeners = {}

        # active listener format (these are listener modules that are actually instantiated)
        #   {"listenerName" : {moduleName: 'http', options: {setModuleOptions} }}
        self.activeListeners = {}

        self.load_listeners()
        self.start_existing_listeners()

    def load_listeners(self):
        """
        Load listeners from the install + "/lib/listeners/*" path
        """

        root_path = "%s/lib/listeners/" % (InternalConfig.get('install_path'))
        pattern = '*.py'
        print(helpers.color("[*] Loading listeners from: %s" % root_path))

        for root, dirs, files in os.walk(root_path):
            for filename in fnmatch.filter(files, pattern):
                filePath = os.path.join(root, filename)

                # don't load up any of the templates
                if fnmatch.fnmatch(filename, '*template.py'):
                    continue

                # extract just the listener module name from the full path
                listenerName = filePath.split("/lib/listeners/")[-1][0:-3]

                # instantiate the listener module and save it to the internal cache
                self.loadedListeners[listenerName] = imp.load_source(listenerName, filePath).Listener(self.mainMenu, [])

    def set_listener_option(self, listenerName, option, value):
        """
        Sets an option for the given listener module or all listener module.
        """

        # for name, listener in self.listeners.iteritems():
        #     for listenerOption, optionValue in listener.options.iteritems():
        #         if listenerOption == option:
        #             listener.options[option]['Value'] = str(value)

        for name, listenerObject in self.loadedListeners.items():

            if (listenerName.lower() == 'all' or listenerName == name) and (option in listenerObject.options):

                # parse and auto-set some host parameters
                if option == 'Host':

                    if not value.startswith('http'):
                        parts = value.split(':')
                        # if there's a current ssl cert path set, assume this is https
                        if ('CertPath' in listenerObject.options) and (
                                listenerObject.options['CertPath']['Value'] != ''):
                            protocol = 'https'
                            defaultPort = 443
                        else:
                            protocol = 'http'
                            defaultPort = 80

                    elif value.startswith('https'):
                        value = value.split('//')[1]
                        parts = value.split(':')
                        protocol = 'https'
                        defaultPort = 443

                    elif value.startswith('http'):
                        value = value.split('//')[1]
                        parts = value.split(':')
                        protocol = 'http'
                        defaultPort = 80

                    # Added functionality to Port
                    # Unsure if this section is needed
                    if len(parts) != 1 and parts[-1].isdigit():
                        # if a port is specified with http://host:port
                        listenerObject.options['Host']['Value'] = "%s://%s" % (protocol, value)
                        if listenerObject.options['Port']['Value'] == '':
                            listenerObject.options['Port']['Value'] = parts[-1]
                    elif listenerObject.options['Port']['Value'] != '':
                        # otherwise, check if the port value was manually set
                        listenerObject.options['Host']['Value'] = "%s://%s:%s" % (
                            protocol, value, listenerObject.options['Port']['Value'])
                    else:
                        # otherwise use default port
                        listenerObject.options['Host']['Value'] = "%s://%s" % (protocol, value)
                        if listenerObject.options['Port']['Value'] == '':
                            listenerObject.options['Port']['Value'] = defaultPort
                    return True

                elif option == 'CertPath':
                    listenerObject.options[option]['Value'] = value
                    host = listenerObject.options['Host']['Value']
                    # if we're setting a SSL cert path, but the host is specific at http
                    if host.startswith('http:'):
                        listenerObject.options['Host']['Value'] = listenerObject.options['Host']['Value'].replace(
                            'http:', 'https:')
                    return True

                if option == 'Port':
                    listenerObject.options[option]['Value'] = value
                    # Check if Port is set and add it to host
                    parts = listenerObject.options['Host']['Value']
                    if parts.startswith('https'):
                        address = parts[8:]
                        address = ''.join(address.split(':')[0])
                        protocol = "https"
                        listenerObject.options['Host']['Value'] = "%s://%s:%s" % (
                            protocol, address, listenerObject.options['Port']['Value'])
                    elif parts.startswith('http'):
                        address = parts[7:]
                        address = ''.join(address.split(':')[0])
                        protocol = "http"
                        listenerObject.options['Host']['Value'] = "%s://%s:%s" % (
                            protocol, address, listenerObject.options['Port']['Value'])
                    return True

                elif option == 'StagingKey':
                    # if the staging key isn't 32 characters, assume we're md5 hashing it
                    value = str(value).strip()
                    if len(value) != 32:
                        stagingKeyHash = hashlib.md5(value.encode('UTF-8')).hexdigest()
                        print(helpers.color(
                            '[!] Warning: staging key not 32 characters, using hash of staging key instead: %s' % (
                                stagingKeyHash)))
                        listenerObject.options[option]['Value'] = stagingKeyHash
                    else:
                        listenerObject.options[option]['Value'] = str(value)
                    return True

                elif option in listenerObject.options:

                    listenerObject.options[option]['Value'] = value

                    # if option.lower() == 'type':
                    #     if value.lower() == "hop":
                    #         # set the profile for hop.php for hop
                    #         parts = self.options['DefaultProfile']['Value'].split("|")
                    #         self.options['DefaultProfile']['Value'] = "/hop.php|" + "|".join(parts[1:])

                    return True

                # if parts[0].lower() == 'defaultprofile' and os.path.exists(parts[1]):
                #     try:
                #         open_file = open(parts[1], 'r')
                #         profile_data_raw = open_file.readlines()
                #         open_file.close()

                #         profile_data = [l for l in profile_data_raw if not l.startswith('#' and l.strip() != '')]
                #         profile_data = profile_data[0].strip("\"")

                #         self.mainMenu.listeners.set_listener_option(parts[0], profile_data)

                #     except Exception:
                #         print helpers.color("[!] Error opening profile file %s" % (parts[1]))

                else:
                    print(helpers.color('[!] Error: invalid option name'))
                    return False

    def start_listener(self, module_name, listener_object):
        """
        Takes a listener module object, starts the listener, adds the listener to the database, and
        adds the listener to the current listener cache.
        """
        category = listener_object.info['Category']
        name = listener_object.options['Name']['Value']
        name_base = name

        if isinstance(name, bytes):
            name = name.decode('UTF-8')

        if not listener_object.validate_options():
            return

        # TODO: Took me a second to figure out what was going on here.
        #   We'd get stuck in an infinite loop, fixed with i +=1.
        #   I think we should just throw a 400 in the api if the name already exists?
        #   Not sure about the CLI
        i = 1
        while name in list(self.activeListeners.keys()):
            name = "%s%s" % (name_base, i)
            i += 1

        listener_object.options['Name']['Value'] = name

        try:
            print(helpers.color("[*] Starting listener '%s'" % (name)))
            success = listener_object.start(name=name)

            if success:
                listener_object_options = copy.deepcopy(listener_object.options)
                self.activeListeners[name] = {'moduleName': module_name, 'options': listener_object_options}

                Session().add(models.Listener(name=name,
                                              module=module_name, # todo is this duplicate? did i mess this up?
                                              listener_type=module_name,
                                              listener_category=category,
                                              enabled=True,
                                              options=pickle.dumps(listener_object_options)))
                Session().commit()
                # dispatch this event
                message = "[+] Listener successfully started!"
                signal = json.dumps({
                    'print': True,
                    'message': message,
                    'listener_options': listener_object_options
                })
                dispatcher.send(signal, sender="listeners/{}/{}".format(module_name, name))
            else:
                print(helpers.color('[!] Listener failed to start!'))

        except Exception as e:
            if name in self.activeListeners:
                del self.activeListeners[name]
            print(helpers.color("[!] Error starting listener: %s" % (e)))

    def start_existing_listeners(self):
        """
        Startup any listeners that are currently in the database.
        """
        enabled_listeners = Session().query(models.Listener).filter(models.Listener.enabled == True).all()

        for listener in enabled_listeners:
            listener_name = listener.name
            name_base = listener_name

            i = 1
            while listener_name in list(self.activeListeners.keys()):
                listener_name = "%s%s" % (name_base, i)
                i += 1

            # unpickle all the listener options
            options = pickle.loads(listener.options)

            try:
                listener_module = self.loadedListeners[listener.module]

                for option, value in options.items():
                    listener_module.options[option] = value

                print(helpers.color("[*] Starting listener '%s'" % listener_name))
                if listener.module == 'redirector':
                    success = True
                else:
                    success = listener_module.start(name=listener_name)

                if success:
                    listener_options = copy.deepcopy(listener_module.options)
                    self.activeListeners[listener_name] = {'moduleName': listener.module, 'options': listener_options}
                    # dispatch this event
                    message = "[+] Listener successfully started!"
                    signal = json.dumps({
                        'print': True,
                        'message': message,
                        'listener_options': listener_options
                    })
                    dispatcher.send(signal, sender="listeners/{}/{}".format(listener.module, listener_name))
                else:
                    print(helpers.color('[!] Listener failed to start!'))

            except Exception as e:
                if listener_name in self.activeListeners:
                    del self.activeListeners[listener_name]
                print(helpers.color("[!] Error starting listener: %s" % (e)))

    def enable_listener(self, listener_name):
        "Starts an existing listener and sets it to enabled"
        if listener_name in list(self.activeListeners.keys()):
            print(helpers.color("[!] Listener already running!"))
            return False

        result = Session().query(models.Listener).filter(models.Listener.name == listener_name).first()
        if not result:
            print(helpers.color("[!] Listener %s doesn't exist!" % listener_name))
            return False
        module_name = result.module
        options = pickle.loads(result.options)
        try:
            listener_module = self.loadedListeners[module_name]

            for option, value in options.items():
                listener_module.options[option] = value

            print(helpers.color("[*] Starting listener '%s'" % listener_name))
            if module_name == 'redirector':
                success = True
            else:
                success = listener_module.start(name=listener_name)

            if success:
                print(helpers.color('[+] Listener successfully started!'))
                listenerOptions = copy.deepcopy(listener_module.options)
                self.activeListeners[listener_name] = {'moduleName': module_name, 'options': listenerOptions}

                to_update = Session().query(models.Listener) \
                    .filter(models.Listener.name == listener_name) \
                    .filter(models.Listener.module != 'redirector') \
                    .first()
                to_update.enabled = True
                Session().commit()
            else:
                print(helpers.color('[!] Listener failed to start!'))
        except Exception as e:
            traceback.print_exc()
            if listener_name in self.activeListeners:
                del self.activeListeners[listener_name]
            print(helpers.color("[!] Error starting listener: %s" % (e)))

    def kill_listener(self, listenerName):
        """
        Shut down the server associated with a listenerName and delete the
        listener from the database.

        To kill all listeners, use listenerName == 'all'
        """

        if listenerName.lower() == 'all':
            listenerNames = list(self.activeListeners.keys())
        else:
            listenerNames = [listenerName]

        for listenerName in listenerNames:
            if listenerName not in self.activeListeners:
                print(helpers.color("[!] Listener '%s' not active!" % (listenerName)))
                return False

            # shut down the listener and remove it from the cache
            if self.mainMenu.listeners.get_listener_module(listenerName) == 'redirector':
                # remove the listener object from the internal cache
                del self.activeListeners[listenerName]

                to_delete = Session().query(models.Listener) \
                    .filter(models.Listener.name == listenerName) \
                    .first()
                Session().delete(to_delete)
                Session().commit()
                continue

            self.shutdown_listener(listenerName)

            to_delete = Session().query(models.Listener) \
                .filter(models.Listener.name == listenerName) \
                .first()
            Session().delete(to_delete)
            Session().commit()

    def delete_listener(self, listener_name):
        """
        Delete listener(s) from database.
        """
        try:
            listeners = Session().query(models.Listener).all()
            if listener_name.lower() == "all":
                for listener in listeners:
                    self.shutdown_listener(listener.name)
                    Session().delete(listener)
                Session.commit()
            else:
                if listener_name in map(lambda x: x.name, listeners):
                    Session().delete(list(filter(lambda x: x.name == listener_name, listeners))[0])
                    self.shutdown_listener(listener_name)
                    Session().commit()
                else:
                    print(helpers.color("[!] Listener '%s' does not exist!" % listener_name))
                    return False
        except Exception as e:
            print(helpers.color("[!] Error deleting listener '%s'" % listener_name))

    def shutdown_listener(self, listenerName):
        """
        Shut down the server associated with a listenerName, but DON'T
        delete it from the database.
        """

        if listenerName.lower() == 'all':
            listenerNames = list(self.activeListeners.keys())
        else:
            listenerNames = [listenerName]

        for listenerName in listenerNames:
            if listenerName not in self.activeListeners:
                print(helpers.color("[!] Listener '%s' doesn't exist!" % (listenerName)))
                return False

            # retrieve the listener module for this listener name
            activeListenerModuleName = self.activeListeners[listenerName]['moduleName']
            activeListenerModule = self.loadedListeners[activeListenerModuleName]

            if activeListenerModuleName == 'redirector':
                print(helpers.color(
                    "[!] skipping redirector listener %s. Start/Stop actions can only initiated by the user." % (
                        listenerName)))
                continue

            # signal the listener module to shut down the thread for this particular listener instance
            activeListenerModule.shutdown(name=listenerName)

            # remove the listener object from the internal cache
            del self.activeListeners[listenerName]

    def disable_listener(self, listenerName):
        "Wrapper for shutdown_listener(), also marks listener as 'disabled' so it won't autostart"

        active_listener_module_name = self.activeListeners[listenerName]['moduleName']

        if listenerName.lower() == "all":
            to_update = Session().query(models.Listener) \
                .filter(models.Listener.module != 'redirector') \
                .all()
            for listener in to_update:
                listener.enabled = False
            Session.commit()
        else:
            to_update = Session().query(models.Listener) \
                .filter(models.Listener.enabled == True) \
                .filter(models.Listener.module != 'redirector') \
                .first()
            to_update.enabled = False
            Session.commit()

            # TODO here we search with .lower() do we always store with .lower()?
            # cur.execute("UPDATE listeners SET enabled=? WHERE name=? AND NOT module=?",
            # [False, listenerName.lower(), "redirector"])
        self.shutdown_listener(listenerName)
        # dispatch this event
        message = "[*] Listener {} killed".format(listenerName)
        signal = json.dumps({
            'print': True,
            'message': message
        })
        dispatcher.send(signal, sender="listeners/{}/{}".format(active_listener_module_name, listenerName))

    def is_listener_valid(self, name):
        # todo use db?
        return name in self.activeListeners

    def get_listener_id(self, name):
        """
        Resolve a name to listener ID.
        TODO VR, this is called by the api after starting a listener to see if it was created.
          Should it hit self.activeListeners?
        """
        results = Session().query(models.Listener).filter(or_(
            models.Listener.name == name,
            models.Listener.id == name
        )).first()

        if results:
            return results.id
        else:
            return None

    def get_listener_name(self, listener_id):
        """
        Resolve a listener ID to a name.
        """
        results = Session().query(models.Listener).filter(or_(
            models.Listener.name == listener_id,
            models.Listener.id == listener_id
        )).first()

        if results:
            return results.name
        else:
            return None

    def get_listener_module(self, listener_name):
        """
        Resolve a listener name to the module used to instantiate it.
        """
        results = Session().query(models.Listener) \
            .filter(models.Listener.name == listener_name) \
            .first()

        if results:
            return results.module
        else:
            return None

    def get_listener_names(self):
        """
        Return all current listener names.
        """
        return list(self.activeListeners.keys())

    def get_inactive_listeners(self):
        """
        Returns any listeners that are not currently running
        """
        # TODO can we just manage from within the database?
        db_listeners = Session().query(models.Listener).all()

        # TODO Here we do not do a .lower() on the comparison. Inconsistency
        inactive_listeners = {}
        for listener in filter((lambda x: x.name not in list(self.activeListeners.keys())), db_listeners):
            inactive_listeners[listener.name] = {'moduleName': listener.module,
                                                 'options': pickle.loads(listener.options)}

        return inactive_listeners

    def update_listener_options(self, listener_name, option_name, option_value):
        "Updates a listener option in the database"

        try:
            listener = Session().query(models.Listener).filter(models.Listener.name == listener_name).first()
            options = pickle.loads(listener.options)
            if not option_name in list(options.keys()):
                print(helpers.color("[!] Listener %s does not have the option %s" % (listener_name, option_name)))
                return
            options[option_name]['Value'] = option_value
            pickled_options = pickle.dumps(options)

            listener.options = pickled_options
            Session.commit()
        except ValueError:
            print(helpers.color("[!] Listener %s not found" % listener_name))
