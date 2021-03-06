
import os

## Memory map.
class Memory(object):

    ## Constractor.
    def __init__(self, args):
        self.directory = args.directory

    ## Memory  map maker.
    def mem_list(self):
        mem = []
        for root, directories, filenames in os.walk(self.directory):
            for filename in filenames:
                mem.append({'root': root, 'filename': filename})
        return mem

    ## Name search in memory.
    def find_name(self, mem, name):
        files = []
        ids = []
        for i in range(len(mem)):
                if name in mem[i]['filename']:
                    files.append(mem[i]['filename'])
                    ids.append(i)
        return files, ids
