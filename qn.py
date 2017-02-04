import os
import sys
from subprocess import Popen,PIPE, call
import pickle
from datetime import datetime
import mimetypes
from stat import ST_CTIME, ST_ATIME, ST_MTIME, ST_SIZE
from operator import itemgetter

# TO IMPLEMENT
# * open note's directory in ranger

# User-defined Globals
QNDIR = os.path.join(os.path.expanduser("~"), "syncthing/smalldocs/quicknotes")
SORTBY='cdate'
SORTREV=False

QNTERMINAL='urxvt'
QNEDITOR='nvim'

# Globals
QNDATA = os.path.join(QNDIR, '.qn')
QNTRASH = os.path.join(QNDATA, 'trash')
TAGF_PATH = os.path.join(QNDATA, 'tags.pickle')
TERM_INTER = False
TAGS = True

DEFAULT_OPTIONS = {}
DEFAULT_OPTIONS['title'] = 'qn:'
DEFAULT_OPTIONS['help'] = None
DEFAULT_OPTIONS['position'] = None
DEFAULT_OPTIONS['filter'] = None
DEFAULT_OPTIONS['sortby'] = SORTBY
DEFAULT_OPTIONS['sortrev'] = SORTREV

BASE_COMMAND ={}
BASE_COMMAND['rofi'] = ['rofi', '-dmenu', '-i', '-width', '50', '-lines', '15'
                        , '-kb-custom-1', 'Alt+Shift+1'
                        , '-kb-custom-1', 'Alt+Shift+1' #remove previous bindings
                        , '-kb-custom-2', 'Alt+Shift+2' #remove previous bindings
                        , '-kb-custom-3', 'Alt+Shift+3' #remove previous bindings
                        , '-kb-custom-4', 'Alt+Shift+4' #remove previous bindings
                        ]

BASE_COMMAND['fzf'] = ['fzf']

IMPLEMENTED_APPS = ['rofi', 'fzf']

def generate_options(appname):


    qn_options = {}
    qn_options['title'] = 'qn:'
    qn_options['help'] = None
    qn_options['position'] = None
    qn_options['filter'] = None
    qn_options['sortby'] = SORTBY
    qn_options['sortrev'] = SORTREV


    if appname not in IMPLEMENTED_APPS:
        raise ValueError('App "%r" not implemented.' % (appname))
    if appname == 'rofi':
        qn_options['app'] = 'rofi'
        qn_options['interactive'] = False 
        qn_options['help'] = ''
        qn_options['command'] = ['rofi', '-sep', '\\0', '-columns', '1'
                        , '-dmenu', '-i', '-width', '50', '-lines', '15'
                        , '-kb-custom-1', 'Alt+Shift+1'
                        , '-kb-custom-1', 'Alt+Shift+1' #remove previous bindings
                        , '-kb-custom-2', 'Alt+Shift+2' #remove previous bindings
                        , '-kb-custom-3', 'Alt+Shift+3' #remove previous bindings
                        , '-kb-custom-4', 'Alt+Shift+4' #remove previous bindings
                        ]
        qn_options['hotkeys'] = {
                    'forcenew'  :['forcenew'  ,'Alt+Return' , 'Force Create New Note'],
                    'delete'    :['delete'    ,'Alt+r'      , 'Delete Note'],
                    'rename'    :['rename'    ,'Alt+space'  , 'Rename Note'],
                    'addtag'    :['addtag'    ,'Alt+n'      , 'Add Tag to Note'],
                    'grep'      :['grep'      ,'Alt+s'      , 'Grep Notes'],
                    'showtrash' :['showtrash' ,'Alt+t'      , 'Show Trash'],
                    'showtagb'  :['showtagb'  ,'Alt+i'      , 'Show Note Tags'],
                    'showtagm'  :['showtagm'  ,'Alt+u'      , 'Filter By Tags'],
                    'showhelp'  :['showhelp'  ,'Alt+h'      , 'Show Help'],
                    'sortname'  :['sortname'  ,'Alt+1'      , 'Sort By Name'],
                    'sortcdate' :['sortcdate' ,'Alt+2'      , 'Sort by Creation Date'],
                    'sortmdate' :['sortmdate' ,'Alt+3'      , 'Sort by Modificatin Date'],
                    'sortsize'  :['sortsize'  ,'Alt+4'      , 'Sort by Size']
                    }



    elif appname == 'fzf':
        qn_options['app'] = 'fzf'
        qn_options['interactive'] = True 
        qn_options['help'] = ''
        qn_options['title'] = 'qn > '
        qn_options['command'] = ['fzf'
                   ,'--read0'
                   ,'--print-query'
                   ,'--print0'
                   ,'--exact'
                   ,'--expect', 'alt-t'
                    ]
        qn_options['hotkeys'] = {
                    'forcenew'  :['forcenew'  ,'alt-return' , 'Force Create New Note'],
                    'delete'    :['delete'    ,'alt-r'      , 'Delete Note'],
                    'rename'    :['rename'    ,'alt-space'  , 'Rename Note'],
                    'addtag'    :['addtag'    ,'alt-n'      , 'Add Tag to Note'],
                    'grep'      :['grep'      ,'alt-g'      , 'Grep Notes'],
                    'showtrash' :['showtrash' ,'alt-t'      , 'Show Trash'],
                    'showtagb'  :['showtagb'  ,'alt-j'      , 'Show Note Tags'],
                    'showtagm'  :['showtagm'  ,'alt-k'      , 'Filter By Tags'],
                    'showhelp'  :['showhelp'  ,'alt-h'      , 'Show Help'],
                    'sortname'  :['sortname'  ,'alt-1'      , 'Sort By Name'],
                    'sortcdate' :['sortcdate' ,'alt-2'      , 'Sort by Creation Date'],
                    'sortmdate' :['sortmdate' ,'alt-3'      , 'Sort by Modificatin Date'],
                    'sortsize'  :['sortsize'  ,'alt-4'      , 'Sort by Size']
                    }
    return(qn_options)


def gen_instance_args(qn_options, instance, alt_help=None, alt_title=None):


    if alt_help:
        helpn = alt_help
    else:
        helpn = qn_options['help']
    if alt_title:
        titlen = alt_title
    else:
        titlen = qn_options['title']

    appname = qn_options['app']
    arguments = []
    if instance == 'default':
        if appname == 'rofi':
            arguments.extend(['-mesg', helpn
                             , '-format', 'f;s;i'
                             ,'-p', titlen])
            if qn_options['filter']:
                arguments.extend(['-filter', qn_options['filter']])
            if qn_options['position']:
                arguments.extend(['-selected-row', qn_options['position']])

        elif appname == 'fzf':
            arguments.extend(['--header', helpn
                             ,'--prompt', titlen])
            if qn_options['filter']:
                arguments.extend(['-filter', qn_options['filter']])

    return(arguments)


# Check if program exists - linux only
def cmd_exists(cmd):


    return call("type " + cmd, shell=True, 
        stdout=PIPE, stderr=PIPE) == 0


# Define application launcher
if cmd_exists('rifle'):
    file_launcher = 'rifle'
else:
    file_launcher = 'xdg-open'


def file_mime_type(filename):

    mtype,menc = mimetypes.guess_type(filename)
    # If type is not detected, just open as plain text
    if not mtype:
        mtype = 'None/None'
    return(mtype)


# Right now it includes hidden files - this needs to be fixed
def list_files(path):


    file_l = [] 
    file_full_l = []
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            fp = os.path.join(root, name)
            fp_rel = os.path.relpath(fp, path)
            # Ignore dotfiles
            if (fp_rel[0] == '.'):
                continue
            file_l.append(fp_rel)
            file_full_l.append(fp)
    return(file_l, file_full_l)


class FileRepo:
    def __init__(self, dirpath=None):
        self.path = dirpath
        self.file_list = []
        self.sorttype = "none"
        self.sortrev = False
        self.filecount = 0

        self.tags = None

        self.lineformat = ['name', 'cdate']
        self.linebs = {}
        self.linebs['name'] = 40
        self.linebs['adate'] = 18
        self.linebs['cdate'] = 18
        self.linebs['mdate'] = 18
        self.linebs['size'] = 15
        self.linebs['misc'] = 100
        self.linebs['tags'] = 50



    def scan_files(self):
        self.filecount = 0
        for root, dirs, files in os.walk(self.path, topdown=True):
            for name in files:
                fp = os.path.join(root, name)
                fp_rel = fp[len(self.path)+1:]

                if (fp_rel[0] == '.'):
                    continue
                try:
                    stat = os.stat(fp)
                except:
                    continue

                file_props = {}
                file_props['size'] = stat[ST_SIZE]
                file_props['adate'] = stat[ST_ATIME]
                file_props['mdate'] = stat[ST_MTIME]
                file_props['cdate'] = stat[ST_CTIME]
                file_props['name'] = fp_rel
                file_props['fullpath'] = fp
                file_props['misc'] = None
                file_props['tags'] = None

                self.file_list.append(file_props)
                self.filecount += 1


    def add_file(self, filepath, misc_prop=None):
        if not os.path.isfile(filepath):
            print(filepath + " is not a file.")
            return

        fp_rel = filepath[len(self.path)+1:]

        try:
            stat = os.stat(filepath)
        except:
            return

        file_props = {}
        file_props['size'] = stat[ST_SIZE]
        file_props['adate'] = stat[ST_ATIME]
        file_props['mdate'] = stat[ST_MTIME]
        file_props['cdate'] = stat[ST_CTIME]
        file_props['name'] = fp_rel
        file_props['fullpath'] = filepath
        file_props['misc'] = misc_prop

        self.file_list.append(file_props)
        self.filecount += 1

    def sort(self, sortby='name', sortrev=False):
        if sortby not in ['size', 'adate', 'mdate', 'cdate', 'name']:
            print("Key '" + sortby + "' is not valid.")
            print("Choose between size, adate, mdate, cdate or name.")

        self.file_list = sorted(self.file_list, 
                            key=itemgetter(sortby), reverse=not sortrev)
        self.sorttype=sortby
        self.sortrev=sortrev

    def get_property_list(self, prop='name'):
        return(list(itemgetter(prop)(filen) for filen in self.file_list))

    def filenames(self):
        return(self.get_property_list('name'))

    def filepaths(self):
        return(self.get_property_list('fullpath'))

    def lines(self, format_list=None):
        lines = []
        if not format_list:
            format_list = self.lineformat
        for filen in self.file_list:
            line = ""
            for formatn in format_list:
                if formatn in ['adate', 'mdate', 'cdate']:
                    block = datetime.utcfromtimestamp(filen[formatn])
                    block = block.strftime('%d/%m/%Y %H:%M')
                else:
                    block = str(filen[formatn])

                blocksize = self.linebs[formatn]
                if len(block) >= blocksize:
                    block = block[:blocksize-2] + '…'

                block = block.ljust(blocksize)
                line += block

            lines.append(line)

        return(lines)


    def grepfiles(self, filters_string):
        if not self.file_list:
            print("No files added to file repo")
            return(1)

        proc = Popen(['grep', '-i', '-I', filters_string] + self.filepaths() 
                     , stdout=PIPE)
        answer = proc.stdout.read().decode('utf-8')
        exit_code = proc.wait()

        grep_file_repo = FileRepo(self.path)
        temp_files = []
        if answer == '':
            return(None)

        for ans in answer.split("\n"):
            if ans:
                ans = ans.split(':', 1)
                if not ans[0] in temp_files:
                    grep_file_repo.add_file(ans[0], ans[1])
                    temp_files.append(ans[0])

        return(grep_file_repo)



def move_note(name1, name2, dest1=QNDIR, dest2=QNDIR, move_tags=False):


    has_sp1 = False
    has_sp2 = False

    if ( '/' in name1):
        has_sp1 = True
        sd1,sn1 = name1.rsplit('/',1)
        td1 = os.path.join(dest1, sd1)
    else:
        sn1 = name1
        td1 = dest1

    if ( '/' in name2):
        has_sp2 = True
        sd2,sn2 = name2.rsplit('/',1)
        td2 = os.path.join(dest2, sd2)
    else:
        sn2 = name2
        td2 = dest2

    full_dir1 = os.path.join(td1, sn1)
    full_dir2 = os.path.join(td2, sn2)
    if (full_dir1 == full_dir2):
        print('Source and destination are the same. Doing nothing.')
        sys.exit(0)

    # check if destination already exists
    if os.path.exists(full_dir2):
        print('Note with same name found, creating conflict.')
        appended = "-conflict-" 
        appended += datetime.now().strftime('%Y%m%d_%H%M%S')
        full_dir2 +=  appended
        name2 += appended

    if has_sp2:
        if not ( os.path.isdir(td2)):
            print('creating ' + td2)
            os.makedirs(td2)
    # move the file
    try:
        os.rename(full_dir1, full_dir2)
        if move_tags:
            tagsdict = load_tags()
            if name1 in tagsdict:
                tagsdict[name2] = tagsdict[name1]
                tagsdict.pop(name1)
                save_tags(tagsdict)
        print('Moved ' + full_dir1 + ' to ' + full_dir2)
    except OSError:
        sys.exit(1)

    if has_sp1:
        try:
            os.rmdir(td1)
            print('deleted ' + td1)
        except OSError:
            print('not deleted ' + td1)
            sys.exit(0)

    sys.exit(0)


def delete_note(note):


    move_note(note, note, dest1=QNDIR, dest2=QNTRASH)


def undelete_note(note):


    move_note(note, note, dest1=QNTRASH, dest2=QNDIR)


def open_note(note, inter=False):


    fulldir = os.path.join(QNDIR, note)
    if os.path.isfile(fulldir):
        mime = file_mime_type(note).split("/")

        if (mime[0] == 'text' or mime[0] == 'None'):
            if inter:
                os.system(QNEDITOR + " " + fulldir)
            else:
                os.system(QNTERMINAL + " -e " + QNEDITOR + " " + fulldir)
        elif (mime[1] == 'x-empty'):
            if inter:
                os.system(QNEDITOR + " " + fulldir)
            else:
                os.system(QNTERMINAL + " -e " + QNEDITOR + " " + fulldir)
        else:
            os.system(file_launcher + " " + fulldir)
    else:
        print(fulldir + " is not a note")
        sys.exit(1)


def new_note(note, inter=False):


    if '/' in note:
        note_dir = note.rsplit('/',1)[0]
        if not os.path.isdir(note_dir):
            os.makedirs(os.path.join(QNDIR, note_dir), exist_ok=True)
    if inter:
        os.system(QNEDITOR + " " + os.path.join(QNDIR, note))
    else:
        os.system(QNTERMINAL + " -e " + QNEDITOR + " " + os.path.join(QNDIR, note))
    return(0)


def force_new_note(note, inter=False):
    filepath = os.path.join(QNDIR, note.strip())
    if os.path.isfile(filepath):
        open_note(note, inter)
    else:
        new_note(note, inter)
    return(0)


def find_in_notes(file_list, f_string):


    grep_path = os.path.join(QNDIR, '*')
    filt = f_string.strip().split(" ") 
    filtered_list = file_list
    for f in filt:
        keyword =  f 
        proc = Popen(['grep', '-i', '-I',  keyword] + filtered_list, stdout=PIPE)
        answer = proc.stdout.read().decode('utf-8')
        exit_code = proc.wait()
        if answer == '':
            return(None, None, None)

        filtered_list = []
        filtered_content = []
        raw_lines = []
        
        for ans in answer.split('\n'):
            if ans.strip() == '':
                continue
            raw_lines.append(ans)
            note_name, note_content = ans.split(':', 1)
            if note_name in filtered_list:
                continue
            else:
                filtered_list.append(note_name)
                filtered_content.append(note_content)
    # this return is a bit messy, but for now it affords current functionality.
    return(raw_lines, filtered_list, filtered_content)


def check_environment(in_rofi=False):


    # Make sure everything is ready for qn
    if not os.path.isdir(QNDIR):
        HELP_MSG = " Do you want to create the qn directory: " + QNDIR + "?"

        s = input(HELP_MSG + " (y/N) ")
        if s and (s[0] == "Y" or s[0] == "y"):
            print("Creating directory: " + QNDIR + "...")
            os.makedirs(QNDIR)
        else:
            print("qn directory" + QNDIR + " does not exist. Exiting...")
            sys.exit(1)

    if not os.path.exists(QNDATA):
        print("Creating directory: " + QNDATA + "...")
        os.makedirs(QNDATA, exist_ok=True)
    if not os.path.exists(QNTRASH):
        print("Creating directory: " + QNTRASH + "...")
        os.makedirs(QNTRASH, exist_ok=True)
    if not os.path.isfile(TAGF_PATH):
        tagfile = open(TAGF_PATH, 'wb')
        pickle.dump({'__taglist':[]}, tagfile)
        tagfile.close()


# FOR TAG SUPPORT
def load_tags():


    tagfile = open(TAGF_PATH, 'rb')
    tagdict = pickle.load(tagfile)
    tagfile.close()

    return(tagdict)


def save_tags(newdict):


    tagfile = open(TAGF_PATH, 'wb')
    pickle.dump(newdict, tagfile)
    tagfile.close()


def list_tags():


    tagslist = load_tags()['__taglist']
    return(tagslist)


def create_tag(tagname):


    tagsdict = load_tags()
    if not tagname in tagsdict['__taglist']:
        tagsdict['__taglist'].append(tagname)
        save_tags(tagsdict)

    return(tagsdict)


def add_note_tag(tagname, notename, tagsdict=None):


    if not os.path.isfile(os.path.join(QNDIR, notename)):
        print('Note does not exist. No tag added.')
        sys.exit(0)
    tagsdict = create_tag(tagname)
    if notename in tagsdict:
        if tagname in tagsdict[notename]:
            print('Note already has tag. Doing nothing')
        else:
            tagsdict[notename].append(tagname)
            save_tags(tagsdict)
    else:
        tagsdict[notename] = [tagname]
        save_tags(tagsdict)

    return(tagsdict)


def del_note_tag(tagname, notename, tagsdict=None):


    if not os.path.isfile(os.path.join(QNDIR, notename)):
        print('Note does not exist. No tag removed.')
        sys.exit(0)

    if not tagsdict:
        tagsdict = load_tags()
    
    if notename in tagsdict:
        if tagname in tagsdict[notename]:
            tagsdict[notename].remove(tagname)
            if not list_notes_with_tags(tagname, tagsdict):
                tagsdict['__taglist'].remove(tagname)
            save_tags(tagsdict)
    else:
        pass

    return(tagsdict)


def clear_note_tags(notename, tagsdict=None):


    if not os.path.isfile(os.path.join(QNDIR, notename)):
        print('Note does not exist. Doing nothing.')
        sys.exit(0)
    if not tagsdict:
        tagsdict = load_tags()
    tagsdict.pop(notename, None)

    return(tagsdict)


def list_note_tags(notename):


    if not os.path.isfile(os.path.join(QNDIR, notename)):
        print('Note does not exist.')
        sys.exit(0)

    tagsdict = load_tags()
    if notename in tagsdict:
        return(tagsdict[notename])
    else:
        return([])


def list_notes_with_tags(tagname, tagsdict=None):


    if not tagsdict:
        tagsdict = load_tags()
    
    filtered_list = []
    for key,value in tagsdict.items():
        if key == '__taglist':
            continue
        if tagname in value:
            filtered_list.append(key)

    return(filtered_list)


 

if __name__ == '__main__':
    check_environment()
    files, files_f = list_files(QNDIR)
    for note in files:
        print(note)

    print("\nNumber of files: " + str(len(files)) + ".")
