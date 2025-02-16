import argparse
from s4_gen import Site, Config

def build(args):
    # Remove any unset arguments
    args = {k:v for k, v in vars(args).items() if v is not None}

    #Create the site with any additional arguments
    site = Site(Config(args=args))

    #If specified, remove old output directory
    if args['clean']:
        site.clean()

    #Build site
    site.build()

def serve(args):
    # Remove any unset arguments
    args = {k:v for k, v in vars(args).items() if v is not None}

    #Create the site with any additional arguments
    site = Site(Config(args=args))

    #If specified, remove old output directory
    if args['clean']:
        site.clean()

    #Build and serve site locally
    site.build()
    site.serve()

def clean(args):
    # Remove any unset arguments
    args = {k:v for k, v in vars(args).items() if v is not None}

    #Create the site with any additional arguments
    site = Site(Config(args=args))

    #Remove old output directory
    site.clean()

#Create parser
parser = argparse.ArgumentParser(
    prog = 'S4 Gen',
    description = 'A super simple static site generator.'
)

#Set global arguments
subparsers = parser.add_subparsers()
parser.set_defaults(func=parser.print_help)
parser.add_argument('-c', '--config', help='Path of the S4 config file.')
parser.add_argument('-s', '--source', help='Directory to search for source files.')
parser.add_argument('-o', '--output', help='Directory to output built site files.')
parser.add_argument('-r', '--clean', action='store_true', help='Delete output directory before building.')

#Create parser for build subcommand
build_parser = subparsers.add_parser('build')
build_parser.set_defaults(func=build)

#Create parser for serve subcommand
serve_parser = subparsers.add_parser('serve')
serve_parser.set_defaults(func=serve)

#Create parser for clean subcommand
clean_parser = subparsers.add_parser('clean')
clean_parser.set_defaults(func=clean)

#Run argument parser
def run():
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()
