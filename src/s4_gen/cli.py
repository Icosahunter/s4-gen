import argparse
from s4_gen import Site, Config

def build(args):
    args = {k:v for k, v in vars(args).items() if v is not None}
    site = Site(Config(args=args))
    if args['clean']:
        site.clean()
    site.build()

def serve(args):
    args = {k:v for k, v in vars(args).items() if v is not None}
    site = Site(Config(args=args))
    if args['clean']:
        site.clean()
    site.build()
    site.serve()

def clean(args):
    args = {k:v for k, v in vars(args).items() if v is not None}
    site = Site(Config(args=args))
    site.clean()

parser = argparse.ArgumentParser(
    prog = 'S4 Gen',
    description = 'A super simple static site generator.'
)

subparsers = parser.add_subparsers()
parser.set_defaults(func=parser.print_help)
parser.add_argument('-c', '--config', help='Path of the S4 config file.')
parser.add_argument('-s', '--source', help='Directory to search for source files.')
parser.add_argument('-o', '--output', help='Directory to output built site files.')
parser.add_argument('-r', '--clean', action='store_true', help='Delete output directory before building.')

build_parser = subparsers.add_parser('build')
build_parser.set_defaults(func=build)

clean_parser = subparsers.add_parser('clean')
clean_parser.set_defaults(func=clean)

serve_parser = subparsers.add_parser('serve')
serve_parser.set_defaults(func=serve)

def run():
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()
