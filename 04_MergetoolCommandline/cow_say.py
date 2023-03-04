import cmd, shlex, cowsay


class CowsayShell(cmd.Cmd):

    prompt = '(cowsay) '
    eyes_variants = ['00', '@@', '==']
    tongue_variants = ['U', 'T', 'V']


    def CowsayCowthinkComplete(self, text, line, startidx, endidx):
        words_printed = len(shlex.split(line[:startidx]))
        if words_printed == 2:
            variants_list = cowsay.list_cows()
        elif words_printed == 3:
            variants_list = self.eyes_variants
        elif words_printed == 4:
            variants_list = self.tongue_variants
        else:
            variants_list = []
        if not text:
            return variants_list
        else:
            return [var for var in variants_list
                    if var.startswith(text)]


    def CowsayCowthinkParams(self, args):
        func_args = {}
        func_args_names = ['cow', 'eyes', 'tongue']
        for i in range(len(func_args_names)):
            if len(args) >= i + 1:
                func_args[func_args_names[i]] = args[i]
        return func_args
    
    
    def do_list_cows(self, args):
        'Prints list of available cows.\n' \
        'Usage: list_cows'
        print(', '.join(cowsay.list_cows()))


    def do_cowsay(self, args):
        'Prints cow saying message.\n' \
        'Usage: cowsay message [cow [eyes [tongue]]]'
        args = shlex.split(args)
        if len(args) < 1:
            print('message not specified')
            return
        message = args[0]
        func_args = CowsayCowthinkParams(self, args[1:])
        print(cowsay.cowsay(message, **func_args))


    def complete_cowsay(self, text, line, startidx, endidx):
        return CowsayCowthinkComplete(self, text, line, startidx, endidx)


    def do_cowthink(self, args):
        'Prints cow thinking message.\n' \
        'Usage: cowsay message [cow [eyes [tongue]]]'
        args = shlex.split(args)
        if len(args) < 1:
            print('message not specified')
            return
        message = args[0]
        func_args = self.CowsayCowthinkParams(args[1:])
        print(cowsay.cowthink(message, **func_args))


    def complete_cowthink(self, text, line, startidx, endidx):
        return self.CowsayCowthinkComplete(text, line, startidx, endidx)


    def do_make_bubble(self, args):
        'Prints bubble with text.\n' \
        'Usage: make_bubble text'
        print(cowsay.make_bubble(args))


    def do_EOF(self, args):
        'Ends session'
        print('bye!')
        return True


if __name__ == '__main__':
    CowsayShell().cmdloop()
