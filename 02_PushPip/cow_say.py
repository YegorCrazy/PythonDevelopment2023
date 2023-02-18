from cowsay import cowsay, list_cows
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--cow')
parser.add_argument('-e', '--eyes')
parser.add_argument('-T', '--tongue')
parser.add_argument('-W', '--width', type=int)
parser.add_argument('-n', '--wrap_text', action='store_true')
parser.add_argument('-l', '--list', action='store_true')
parser.add_argument('-b', dest='preset', action='append_const', const='b')
parser.add_argument('-d', dest='preset', action='append_const', const='d')
parser.add_argument('-g', dest='preset', action='append_const', const='g')
parser.add_argument('-p', dest='preset', action='append_const', const='p')
parser.add_argument('-s', dest='preset', action='append_const', const='s')
parser.add_argument('-t', dest='preset', action='append_const', const='t')
parser.add_argument('-w', dest='preset', action='append_const', const='w')
parser.add_argument('-y', dest='preset', action='append_const', const='y')
parser.add_argument('message')
args = parser.parse_args()

if args.__dict__['list']:
    print(*list_cows())
else:
    cowsay_args = args.__dict__.copy()
    del cowsay_args['list']
    delete_if_none = ['cow', 'eyes', 'tongue']
    for arg_name in delete_if_none:
        if not cowsay_args[arg_name]:
            del cowsay_args[arg_name]
    if cowsay_args['preset']:
        cowsay_args['preset'] = cowsay_args['preset'][0]
    else:
        del cowsay_args['preset']
    message = cowsay_args['message']
    del cowsay_args['message']

    print(cowsay(message, **cowsay_args))
