import argparse


class Arguments(argparse.ArgumentParser):
    def __init__(self):
        super(Arguments, self).__init__(description='Backup controller')
        self.add_argument('-b', '--background', help='Run the script in background', action='store_true')
