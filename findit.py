#!/usr/bin/python3
'''
Version 3.0 - 5/7/2022  - Switched out get_files function.
Version 2.9 - 5/6/2022  - Now you can pass it files as well as directories
Version 2.8 - 4/29/2022 - Now the max file length takes in the fact of 2 chars for one visible display, added a date to the --version.
Version 2.7 - 4/27/2022 - Fixed an issue where unicode where the len is counting 2 for one char that is combined and displayed as one char.
Version 2.6 - 4/23/2022 - Now split up extra spaces between columns.
Version 2.5 - 4/22/2022 - Now display in column if you use the --column, which was added to the -l.
Version 2.4 - 4/19/2022 - Now works if you parse -e with '' around the search results in windows.
                          In windows, now if you do a -a it does the split by changing everything to lower, because the Drive letter
                          will not change case so d:\GIT is not the same as D:\GIT when you do the resolve. 
                          Added sorting for date, size, and the default of dir/name.
                          Changed defaults for -l when run from windows turn of -G -O since they don't make sense.
Version 2.3 - 4/19/2022 - rewrote the dir split into left and right parts, added -PermOct, Changed first char color of both modes.  
                          Now prints in color in windows.
Version 2.2 - Rewrote the printresults, now split the dir into left and right parts and print them.
Version 2.1 - add -f for full path search
Version 2 - added -o -t -m'''
import os
import sys
from pathlib import Path
import argparse
import re
import stat
import datetime
import platform
import unicodedata

class style():
  BLACK = '\033[30m'; RED = '\033[31m'; GREEN = '\033[32m'; YELLOW = '\033[33m'
  BLUE = '\033[34m'; MAGENTA = '\033[35m'; CYAN = '\033[36m'; WHITE = '\033[37m'; GRAY = '\033[90m'
  RED2 = '\033[91m'; GREEN2 = '\033[92m'; YELLOW2 = '\033[93m'; BLUE2 = '\033[94m'
  MAGENTA2 = '\033[95m'; CYAN2 = '\033[96m'; WHITE2  = '\033[97m'
  UNDERLINE = '\033[4m'; RESET = '\033[0m'

def clear_style():
  style.BLACK = ''; style.RED = ''; style.GREEN = ''; style.YELLOW = ''
  style.BLUE = ''; style.MAGENTA = ''; style.CYAN = ''; style.WHITE = ''; style.GRAY = ''
  style.RED2 = ''; style.GREEN2 = ''; style.YELLOW2 = ''; style.BLUE2 = ''
  style.MAGENTA2 = ''; style.CYAN2 = ''; style.WHITE2  = ''
  style.UNDERLINE = ''; style.RESET = ''


def msg(msg1, clr=''):
  print(f'{clr}{msg1}{style.RESET}')

def scantree(path, depth):
  """Recursively yield DirEntry objects for given directory."""
  if (depth is not None):
    depth -= 1
  for entry in os.scandir(path):
    if (entry.is_dir(follow_symlinks=False) and (depth is None or depth > 0)):
       yield from scantree(entry.path, depth)  # see below for Python 2.x
    else:
      yield entry

def get_files(sourceDir, maxdepth):
  """Get a list of file"""
  retset = set()
  if (maxdepth < 1 ):
    maxdepth = None

  for file in { Path(x) for x in sourceDir if Path(x).is_file() }:
    retset.add(file)
  for sdir in { Path(x) for x in sourceDir if Path(x).is_dir() }:
    if (maxdepth == 1):
      retset.add(sdir)
      if (str(Path.cwd()) == str(sdir.resolve())):
        predir = str(sdir) + os.sep + '..'
        retset.add(Path(predir))

    for entry in scantree(sdir, maxdepth):
      retset.add(Path(entry))

  return (retset)


def filter_list(flist, args):
  if (args.case == True):
    flags = 0
  else:
    flags = re.IGNORECASE
  retset = set(flist)
  for ereg in args.eregs:
    flist = retset
    retset = set()
    for file in flist:
      # full means directory and file name
      if (args.full == True):
        f = f"{str(file)}"
        eereg = ereg
      else:
        f = f"{file.name}"
        eereg = ereg
        if (str(file) == '.'):
          f = f"{str(file)}"
      x = re.search(eereg, f, flags = flags)
      if (x is not None):
        retset.add(file)

  return(retset)

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Y{suffix}"


def print_args(args):
  '''
  print out the args'''

  print (args)

def get_file_info(filelist):

  dic_file_info={}
  owner_max_len=0
  group_max_len=0
  size_max_len=0
  for x in filelist:
    temp_dic={}
    try:
      if (x.exists() == False):
        continue 
    except:
      continue
    if (x.is_symlink() == True):
      fstat = x.lstat()
    else:
      fstat = x.stat()
    imode = f'{stat.filemode(fstat.st_mode)}'
    imodeoct = f'{oct(fstat.st_mode & 0o7777)[2:].zfill(4)}'
    isize = fstat.st_size
    isizefmt = f'{sizeof_fmt(isize)}'
    imtime = fstat.st_mtime
    imtime_date = f"{datetime.datetime.fromtimestamp(imtime).strftime('%m/%d/%Y')}"
    imtime_time = f"{datetime.datetime.fromtimestamp(imtime).strftime('%I:%M.%S %p')}"
    try:
      iowner = f'{x.owner()}'
      iowner_max = len(iowner)
    except:
      iowner = f'{fstat.st_uid}'
      iowner_max = len(iowner)

    try: 
      igroup = f'{x.group()}'
      igroup_max = len(igroup)
    except:
      igroup = f'{fstat.st_gid}'
      igroup_max = len(igroup)
    
    if (x.is_dir() == True):
      idir = f'{str(x)}{os.sep}'
      iname = ''
    else:
      idir = f'{x.parent}{os.sep}'
      iname = f'{x.name}'
    if (iowner_max > owner_max_len):
      owner_max_len = iowner_max
    if (igroup_max > group_max_len):
      group_max_len = igroup_max
    if (len(isizefmt) > size_max_len):
      size_max_len = len(isizefmt)
    #create dictionary
    temp_dic['dir'] = idir 
    temp_dic['name'] = iname
    temp_dic['mode'] = imode
    temp_dic['modeoct'] = imodeoct
    temp_dic['size'] = isize
    temp_dic['sizefmt'] = isizefmt
    temp_dic['owner'] = iowner
    temp_dic['owner_len'] = iowner_max
    temp_dic['group'] = igroup
    temp_dic['group_len'] = igroup_max
    temp_dic['mtime'] = imtime
    temp_dic['mtime_date'] = imtime_date
    temp_dic['mtime_time'] = imtime_time
    dic_file_info[f'{str(x)}'] = temp_dic
  temp_dic = {}

  temp_dic['owner_max'] = owner_max_len
  temp_dic['group_max'] = group_max_len
  temp_dic['size_max'] = size_max_len
  dic_file_info['--:--MAX--:--'] = temp_dic

  return(dic_file_info)

def highlight_match(regxs,s, casesensitivity,colr):
  colourStr = style.RED
  resetStr = style.RESET
  if (casesensitivity == True):
    flags = 0
  else:
    flags = re.IGNORECASE

  for regx in regxs:
    if (regx == '.'):
      continue
    lastMatch = 0
    formattedText = ''
    for match in re.finditer(regx, s, flags=flags):
      start, end = match.span()
      formattedText += s[lastMatch: start]
      formattedText += colourStr
      formattedText += s[start: end]
      formattedText += resetStr + colr
      lastMatch = end
    formattedText += s[lastMatch:]
    s = formattedText
  return(s)

def print_results(dic_file_info, args):
  amode = False
  amodeoct = False
  asize = False
  aowner = False
  agroup = False
  adate = False
  atime = False
  ainfo = False
  acolumn = False
  if (platform.system() == 'Windows'):
    if (args.long == True):
      amode = True
      asize = True
      aowner = False
      agroup = False
      adate = True
      atime = True
      ainfo = True
      acolumn = True
  else:
    if (args.long == True):
      amode = True
      asize = True
      aowner = True
      agroup = True
      adate = True
      atime = True
      ainfo = True
      acolumn = True
  if (args.LONG == True):
    amode = False
    amodeoct = False
    asize = False
    aowner = False
    agroup = False
    adate = False
    atime = False
    ainfo = False
    acolumn = False

  if (args.permission == True):
    amode = True
  if (args.PermOct == True):
    amodeoct = True
  if (args.size == True):
    asize = True
  if (args.owner == True):
    aowner = True
  if (args.group == True):
    agroup = True
  if (args.date == True):
    adate = True
  if (args.time == True):
    atime = True
  if (args.info == True):
    ainfo = True
  if (args.column == True):
    acolumn = True

  if (args.PERMISSION == True):
    amode = False
  if (args.SIZE == True):
    asize = False
  if (args.OWNER == True):
    aowner = False
  if (args.GROUP == True):
    agroup = False
  if (args.DATE == True):
    adate = False
  if (args.TIME == True):
    atime = False
  if (args.INFO == True):
    ainfo = False
  if (args.COLUMN == True):
    acolumn = False

  if (args.reverse == True):
    reverse = True
  else:
    reverse = False
  if (len(dic_file_info) <= 1):
    msg('Nothing found.', style.BLUE)
  else:
    owner_max = dic_file_info['--:--MAX--:--']['owner_max']
    group_max = dic_file_info['--:--MAX--:--']['group_max']
    owner_group_max = owner_max + group_max + 1
    size_max = dic_file_info['--:--MAX--:--']['size_max']

    del dic_file_info['--:--MAX--:--']

    #get the max output length
    max_output = 0
    #create a list to print out
    output_lst = []
    #create a set to hold the number of directories
    dir_set = set()

    if (args.orderdate == True):
      k = lambda k:(dic_file_info[k]['mtime'], dic_file_info[k]['dir'].lower(), dic_file_info[k]['name'].lower())
    elif (args.ordersize == True):
      k = lambda k:(dic_file_info[k]['size'], dic_file_info[k]['dir'].lower(), dic_file_info[k]['name'].lower())
    else:
      k = lambda k:(dic_file_info[k]['dir'].lower(), dic_file_info[k]['name'].lower())
    for x in sorted(dic_file_info, key = k, reverse=reverse): 
      y = dic_file_info[x]

      if (args.name == True):
        #if name is blank then it must be a dir, so print out dir
        if (y["name"] == ''):
          name = f'{style.YELLOW}{highlight_match(args.eregs,y["dir"], args.case, style.YELLOW)}'
        else:
          name = f'{style.YELLOW2}{highlight_match(args.eregs,y["name"], args.case, style.YELLOW2)}'
      else:
        #display the dir
        # ./ and ../ should return at ''
        dir = y["dir"]

        rdir = '' #right side of dir
        #get right side of dir
        if ( dir[0:2] == f'.{os.sep}'):
          rdir = dir[2:]
        elif (dir[0:3] == f'..{os.sep}'):
          rdir = dir[3:]
        else:
          rdir = dir

        ldir = '' #left side of dir
        #find left side dir
        if (args.absolute == True):
          adir = str(Path(dir).resolve()) + os.sep
          if (rdir == ''):
            ldir =  adir
          else:
            if (platform.system() == 'Windows'):
              dirsplit = adir.lower().rsplit(rdir.lower(), 1)
            else:
              dirsplit = adir.rsplit(rdir, 1)
            ldir = dirsplit[0]

        #did they search on full path if so highlight rdir
        if (args.full == True):
          rdir = highlight_match(args.eregs, rdir, args.case, style.YELLOW)

        if (y["name"] == '' and rdir == '' and ldir == ''):
          aname = f'{style.YELLOW}{highlight_match(args.eregs,y["dir"], args.case, style.YELLOW)}'
        else:
          aname = f'{style.YELLOW2}{highlight_match(args.eregs,y["name"], args.case, style.YELLOW2)}'

        name = f'{style.YELLOW}{ldir}{rdir}{style.YELLOW2}{aname}'

      mode = f'{style.WHITE}{y["mode"][0:1]}{style.GREEN}{y["mode"][1:]} '
      modeoct = f'{style.WHITE}{y["mode"][0:1]}{style.GREEN}{y["modeoct"]} '
      size = f'{style.GREEN2}{y["sizefmt"]:>{size_max}} '
      owner = f'{style.CYAN}{y["owner"]:>{owner_max}} '
      group = f'{style.CYAN2}{y["group"]:>{group_max}} '
      owner_group = f'{style.CYAN}{y["owner"]:>{owner_max}}:{style.CYAN2}{y["group"]:<{group_max}}'
      fowner = f'{style.GREEN2}{owner_group:^{owner_group_max}} '
      fdate = f'{style.BLUE}{y["mtime_date"]} '
      ftime = f'{style.BLUE2}{y["mtime_time"]} '

      out=''
      if (amode == True):
        out = out + mode
      if (amodeoct == True):
        out = out + modeoct
      if (asize == True):
        out = out + size
      if (aowner == True and agroup == True):
        out = out + fowner
      elif (aowner == True):
        out = out + owner
      elif (agroup == True):
        out = out + group
      if (adate == True): 
        out = out + fdate
      if (atime == True):
        out = out + ftime
        
      dir_set.add(y['dir'])

      out1 = out + name 

      out_size = len(re.sub('\033\[[0-9]*m', '', out1))
      answer = sum(1 for ch in out1 if unicodedata.combining(ch) != 0)
      out_size -= answer
      if (max_output <= out_size):
        max_output = out_size
      
      output_lst.append(out1)

    try:
      #figure out how many columns we have with a 3 space gap
      term_columns, term_lines = os.get_terminal_size()
    except:
      term_columns = max_output

    columns = 0
    
    output_lines = len(output_lst)
    tmp_length = max_output
    while ( tmp_length <= term_columns):
      columns += 1
      tmp_length += max_output + 3
    
    if (columns == 0):
      columns = 1
    
    lines_per_column = int(output_lines / columns)
    if (lines_per_column * columns > output_lines):
      lines_per_column -= 1
    if (lines_per_column == 0 and output_lines > 0):
      lines_per_column = 1

    #print everything in one column
    if (acolumn == False):
      columns = 1
      lines_per_column =  output_lines
    
    #figure out extra spaces and divide it up between the columns
    add_spaces = ''
    if (columns > 1):
      #spaces between columns
      spaces_btwn_columns = (columns - 1) * 3
      column_len = (columns * max_output) + spaces_btwn_columns
      extra_spaces = int(term_columns - column_len) 
      #max_output += extra_spaces
      extra = int(extra_spaces / columns )
      add_spaces = ' ' * extra
      #print(f'term_columns: {term_columns} max_output: {max_output} spaces_btwn_columns: {spaces_btwn_columns} column_len: {column_len} extra_spaces: {extra_spaces} extra: {extra}')


    for lin in range(lines_per_column):
      s = ''
      if (columns == 1):
        s = f'{output_lst[lin]}'
      else:
        for col in (range(int(columns))):
          inx = (col * lines_per_column) + lin 
          if (inx < output_lines):
            lendiff = 0
            colors = re.findall('\033\[[0-9]*m', output_lst[inx])
            for i in colors:
              lendiff += len(i)
            #d = re.sub('\033\[[0-9]*m', '', output_lst[inx])
            answer = sum(1 for ch in output_lst[inx] if unicodedata.combining(ch) != 0)
            lendiff += answer
            if (col > 0 and col < columns):
              #Added 3 spaces between columns plus left over
              s += f'{style.RESET}{add_spaces} \u2502 '
            s = s + f'{output_lst[inx]:<{max_output +lendiff}}'
      msg(s)

    
    # print(f'term_columns: {term_columns} max_output: {max_output} columns: {columns} tmp_length: {tmp_length} output_lines: {output_lines}')

    #get the number of files for total line
    files =len([x['name'] for x in dic_file_info.values() if x['name'] != ''])
    #get the number of dirs for total line
    dirs = len(dir_set)

    if (ainfo == True):
      info = f'Files: {files}     Dirs: {dirs}'
      #strips out any color codes and then counts
      out_size = len(re.sub('\033\[[0-9]*m', '', out))
      if (columns > 1):
        out_size = term_columns
      else:
        if (out_size < len(info)):
          out_size = len(info)
        else:
          out_size -= 1
      msg( u'\u2500' * out_size)
      msg(info)


def main():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=f'%(prog)s version: {__version__}\n' +
                f'This is basically a simple ls and find built into one.\n' +
                f'Run it with no arguments is the same as doing -e "." -m1.\n' +
                f'The -e "." mean match everything, -m1 just show one level, so the current dir.\n' +
                f'You can pass it multiple dirs or files, and with the -e you can pass it mutiple regex.\n' +
                f'If you wanted to search for a file that has the name "hello" in it that might be located in 2 dirs:\n' +
                f'findit.py ~/Downloads ~/Documents -e "hello"\n' +
                f'If you wanted to find the words "hello" and "hi" you would do:\n' +
                f'findit.py ~/Downloads ~/Documents -e "hello|hi"\n' 
                ,
    epilog=""
  )
  parser.add_argument("Dirs", help="List of directories or files to search, default is the current dir", nargs='*', default='.')
  parser.add_argument('-a', '--absolute', help='Expand dir.', action='store_true')
  parser.add_argument('-c', '--case', help='Case sensitivity.', action='store_true')
  parser.add_argument('--column', help='Display in columns if possible.', action='store_true')
  parser.add_argument('--COLUMN', help='Do not display in columns.', action='store_true')
  parser.add_argument('-i', '--info', help='Display info footer.', action='store_true')
  parser.add_argument('-I', '--INFO', help='Do not Display info footer.', action='store_true')

  parser.add_argument('-e', '--eregs', help="Multiple regular expressions, default is '.' match everything", nargs='+', default='.')
  parser.add_argument('-l', '--long', help="Long output, same as --column -i -m -s -o -g -d -t.", action='store_true')
  parser.add_argument('-L', '--LONG', help="Turn off --COLUMN -I -M -S -O -G -D -T.", action='store_true')
  parser.add_argument('-f', '--full', help='Search on full path dir + name', action='store_true')
  parser.add_argument('-n', '--name', help='Display name without path.', action='store_true')
  parser.add_argument('-p', '--permission', help='Display mode (permissions) of a file.', action='store_true')
  parser.add_argument('-P', '--PERMISSION', help='Do not display mode (permissions) of a file.', action='store_true')
  parser.add_argument('--PermOct', help='Display permission as octal, but also add the first char from the mode (-p) ie. -0666, d0666 (dir).', action='store_true')
  parser.add_argument('-s', '--size', help='Display file size.', action='store_true')
  parser.add_argument('-S', '--SIZE', help='Do not display file size.', action='store_true')
  parser.add_argument('-o', '--owner', help='Display owner of a file.', action='store_true')
  parser.add_argument('-O', '--OWNER', help='Do not display owner of a file.', action='store_true')
  parser.add_argument('-g', '--group', help='Display group user of a file.', action='store_true')
  parser.add_argument('-G', '--GROUP', help='Do not display group user of a file.', action='store_true')
  parser.add_argument('-d', '--date', help='Display modified date of a file.', action='store_true')
  parser.add_argument('-D', '--DATE', help='Do not modified display date  a file.', action='store_true')
  parser.add_argument('-t', '--time', help='Display modified time of file.', action='store_true')
  parser.add_argument('-T', '--TIME', help='Do not display modified time of a file.', action='store_true')
  parser.add_argument('-m', '--maxdepth', type=int, help='How many directory levels to show.  If not set then show all.', default=-1)
  parser.add_argument('--COLOR', help='Do not display color.', action='store_true')
  parser.add_argument('--color', help='Display color.', action='store_true')
  parser.add_argument('--version', action='version', version=(f'%(prog)s version: {__version__}'), help = 'show the version number and exit')
  parser.add_argument('-R', '--reverse', help='reverse the sort order.', action='store_true')
  parser.add_argument('-od', '--orderdate', help='Order by date.', action='store_true')
  parser.add_argument('-os', '--ordersize', help='Order by size.', action='store_true')

  args = parser.parse_args()
  #in windows when you pass -e with 'find' it wrappes it with "" so need to strip off ' from the front and back of string
  if (platform.system() == 'Windows'):
    for i in range(len(args.eregs)):
      x = args.eregs[i]
      if (x[0:1] == "'" and x[-1:] == "'"):
        args.eregs[i] = x[1:-1]


  #print_args(args)

  if (((os.fstat(0) != os.fstat(1)) or args.COLOR == True ) and args.color == False):
    clear_style()

  for x in args.eregs:
    try:
      tst = re.compile(x)
    except:
      msg(f'Bad regex: {x}', style.RED2)
      msg('Please try again...', style.RED2)
      exit()

  mdepth = 0
  if (args.eregs == '.' and args.maxdepth == -1):
    mdepth = 1
  else:
    mdepth = args.maxdepth

  retset = get_files(args.Dirs, mdepth)

  retset = filter_list(retset, args)

  dic_file_info = get_file_info(retset)

  retset = set()

  # for x in dic_file_info:
  #   if (x != '--:--MAX--:--'):
  #     print(f"dir: {dic_file_info[x]['dir']:15s} name: {dic_file_info[x]['name']}")

  print_results(dic_file_info, args)



if __name__ == "__main__":
  __version__ = '3.0 date: 5/7/2022'
  if (platform.system() == 'Windows'):
    sys.argv.append('-l')
    os.system('color')
  main()
  # columns, lines = os.get_terminal_size()
  # print(os.get_terminal_size())
  # msg(f'columns: {style.BLUE2}{columns}{style.RESET} lines: {style.BLUE2}{lines}')
