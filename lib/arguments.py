"""
Parse arguments to be used in other modules.
"""
import argparse

parser = argparse.ArgumentParser()

generalGroup = parser.add_argument_group('General Options')
generalGroup.add_argument('--debug', nargs='?', const='1',
                          help='Debug level for output (default of 1, 2 for msg display).')
generalGroup.add_argument('-v', '--version', action='store_true', help='Display current Empire version.')
generalGroup.add_argument('-r', '--resource', nargs=1,
                          help='Run the Empire commands in the specified resource file after startup.')
generalGroup.add_argument('--db', default="empire.db", type=str,
                          help="An alternate database name. Useful for e2e testing.")

cliGroup = parser.add_argument_group('CLI Payload Options')
cliGroup.add_argument('-l', '--listener', nargs='?', const="list",
                      help='Display listener options. Displays all listeners if nothing is specified.')
cliGroup.add_argument('-s', '--stager', nargs='?', const="list",
                      help='Specify a stager to generate. Lists all stagers if none is specified.')
cliGroup.add_argument('-o', '--stager-options', nargs='*',
                      help="Supply options to set for a stager in OPTION=VALUE format. Lists options if nothing is specified.")

restGroup = parser.add_argument_group('RESTful API Options')
launchGroup = restGroup.add_mutually_exclusive_group()
launchGroup.add_argument('--rest', action='store_true', help='Run Empire and the RESTful API.')
launchGroup.add_argument('--headless', action='store_true',
                         help='Run Empire and the RESTful API headless without the usual interface.')
restGroup.add_argument('--restport', type=int, nargs=1, help='Port to run the Empire RESTful API on.')
restGroup.add_argument('--username', nargs=1,
                       help='Start the RESTful API with the specified username instead of pulling from empire.db')
restGroup.add_argument('--password', nargs=1,
                       help='Start the RESTful API with the specified password instead of pulling from empire.db')
restGroup.add_argument('--insecure', action="store_true", help="Run Empire's Api without ssl")

args = parser.parse_args()
