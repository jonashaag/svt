from os.path import expanduser
from random import sample
from collections import namedtuple, defaultdict

VOCFILE = expanduser('~/.svtvocs')

Word = namedtuple('Word', ['foreign', 'native'])

def take_threesomes(iterable):
    iterator = iter(iterable)
    while True:
        try:
            first = iterator.next()
        except StopIteration:
            return
        else:
            yield first, iterator.next(), iterator.next()

def parse_file(file):
    lines = file.read().strip().split('\n')
    for foreign, natives, level in take_threesomes(lines):
        for native in natives.split(';'):
            yield int(level), Word(foreign.strip(), native.strip())

def save_file(groups):
    with open(VOCFILE, 'w') as vocfile:
        for group_index, words in groups.iteritems():
            for word in words:
                vocfile.write('%s\n%s\n%d\n' % (word.foreign, word.native, group_index))

def group_by_level(words):
    groups = defaultdict(set)
    for level, word in words:
        groups[level].add(word)
    return groups

def select_words(groups, n=20):
    if groups[0]:
        for word in sample(groups[0], min(len(groups[0]), n)):
            yield 0, word
        return

    groups = iter(sorted(groups.iteritems()))
    seen = set()
    while n >= 1:
        try:
            group_index, group = groups.next()
        except StopIteration:
            return
        smpl = sample(group, min(len(group), int(n*0.5)))
        n -= len(smpl)
        for word in smpl:
            if not word in seen:
                yield group_index, word
                seen.add(word)

def take():
    with open(VOCFILE) as vocfile:
        groups = group_by_level(parse_file(vocfile))
    for group_index, word in select_words(groups):
        try:
            answer = raw_input('(%d) %s: ' % (group_index, word.native))
        except (KeyboardInterrupt, EOFError):
            break
        if answer != word.foreign:
            print "Sorry man, the correct answer would've been %r" % word.foreign
            delta = -1
        else:
            delta = 1
        groups[group_index].remove(word)
        groups[group_index+delta].add(word)
    save_file(groups)

if __name__ == '__main__':
    import sys
    methods = {'take' : take}
    methods.get(sys.argv[1], lambda: exit(1))()
