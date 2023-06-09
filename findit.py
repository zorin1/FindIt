#!/usr/bin/python3
'''
Version 4.9 - 6/9/2023  - Fixed an issue in the code because os.DirEntry.stat() returns 0 for st_dev.  You need to call os.stat().  This caused on windows that the
                          Free space was not correct.
Version 4.8 - 7/19/2022 - Change the header and footer bar to be the same length as the output line.  If the output line is longer
                          than the number columns in the terminal then limit it to column length.
Version 4.7 - 6/25/2022 - Got rid of duplicate files if you Dirs overlap like / /home, home would be listed twice. 
Version 4.6 - 6/24/2022 - Fixed a bug where it would not display the directory root that is passed to it.
Version 4.5 - 6/17/2022 - Fixed a display issue when there is not enough files per column.
Version 4.4 - 6/16/2022 - Changed when the column separator is printed. 
                          Added a top line and better graphic line chars.
Version 4.3 - 6/11/2022 - Added -Dir which will display only directories.  If you combine this with -e then it only matches on the top most directory.
Version 4.2 - 6/11/2022 - Fixed an issue where the os.sep was left out when you run findit on a given file.
Version 4.1 - 5/29/2022 - Speed improvements now filter on get_files.  Fixed an issues where it throws an error when you don't have access to a dir.
                          Added commas to number of files and directories. 
                          Add a progress bar so that you know things are not stuck.
                          Added two new options --progress and --PROGRESS and added --progress to -l.
Version 4.0 - 5/18/2022 - Speed improvements when getting a list of files, slower when you filter the list.
Version 3.2 - 5/9/2022  - Fixed an issue where sometimes it would not display the last file in the list.  Added size and free space.
Version 3.1 - 5/7/2022  - Fixed an issue where you don't have access a directory.
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
Version 2.2 - Rewrote the print results, now split the dir into left and right parts and print them.
Version 2.1 - add -f for full path search
Version 2 - added -o -t -m'''
import os
import sys
import shutil
from pathlib import Path
import argparse
import re
import stat
import datetime
import platform
import unicodedata

class style():
  redirect = False
  BLACK = '\033[30m'; RED = '\033[31m'; GREEN = '\033[32m'; YELLOW = '\033[33m'
  BLUE = '\033[34m'; MAGENTA = '\033[35m'; CYAN = '\033[36m'; WHITE = '\033[37m'; GRAY = '\033[90m'
  RED2 = '\033[91m'; GREEN2 = '\033[92m'; YELLOW2 = '\033[93m'; BLUE2 = '\033[94m'
  MAGENTA2 = '\033[95m'; CYAN2 = '\033[96m'; WHITE2  = '\033[97m'
  UNDERLINE = '\033[4m'; RESET = '\033[0m'

def clear_style():
  style.redirect = True
  style.BLACK = ''; style.RED = ''; style.GREEN = ''; style.YELLOW = ''
  style.BLUE = ''; style.MAGENTA = ''; style.CYAN = ''; style.WHITE = ''; style.GRAY = ''
  style.RED2 = ''; style.GREEN2 = ''; style.YELLOW2 = ''; style.BLUE2 = ''
  style.MAGENTA2 = ''; style.CYAN2 = ''; style.WHITE2  = ''
  style.UNDERLINE = ''; style.RESET = ''

class spinner():
  spinner = '\|/-'
  counter = 0
  index = 0
  prev_title = ''
  display_spinner = False

  def get_count():
    spinner.counter += 1
    if (spinner.counter >= 500):
      spinner.counter = 0
      if (spinner.index == 4):
        spinner.index = 0
      ret = spinner.index
      spinner.index += 1
    else:
      ret  = -1
    return(ret)

  def spin(title = ''):
    index = spinner.get_count()
    if (index != -1 and spinner.display_spinner == True):
      #remove previous title
      if (title != spinner.prev_title):
        t = len(spinner.prev_title) + 1
        out = t * ' ' + t * '\b' 
        print(out , end = '', flush =True)
        spinner.prev_title = title

      t = len(title)
      print(title + spinner.spinner[index] + (t + 1) * '\b' , end = '', flush =True)

def msg(msg1, clr=''):
  print(f'{clr}{msg1}{style.RESET}')

class FileInfo:
  '''
  full is the main element, this is what the hash is based off of.
  Set the values that we get from the scandir so that we don't have to get this info
  more than once.

  full: str 
  dir: str 
  name: str  
  isdir: bool  
  stat: os.stat_result 
  '''
  __slots__ = ('full', 'dir', 'name', 'isdir', 'stat')

  def __init__(self, file):
    '''
    Takes either a Path or os.DirEntry
    '''
    if (type(file) == os.DirEntry):
      self.full = os.path.abspath(file.path)
      self.name = file.name
      try:
        self.isdir = file.is_dir()
        if (self.isdir == True):
          self.dir = file.path + os.sep
        else:
          self.dir =  file.path.rsplit(file.name,1)[0]
      except:
        self.full = None

      try:
        if (WINDOWS == True):
          self.stat = os.stat(file)
        else:
          self.stat = file.stat()
      except:
        self.full = None
    else:
      self.full = os.path.abspath(file)
      self.name = file.name
      self.isdir = file.is_dir()
      if (self.isdir == True):
        self.dir = f'{file}{os.sep}'
      else:
        self.dir = f'{file.parent}{os.sep}'
      try:
        if (file.is_symlink() == True):
          self.stat = file.lstat()
        else:
          self.stat = file.stat()
      except: 
        self.full = None

  def __repr__(self):
    return (f'{self.full}')

  def __eq__(self, other):
    return(isinstance(other, FileInfo) and self.full == other.full)
  
  def __hash__(self):
    return(hash(self.full))

def scantree(path, depth, dir):
  """Recursively yield DirEntry objects for given directory."""
  if (depth is not None):
    depth -= 1
  try:
    for entry in os.scandir(path):
      spinner.spin('Getting Files Names: ')
      #only get direcotries
      if (dir == True):
        if (entry.is_dir(follow_symlinks=False) and (depth is None or depth >= 0)):
          yield entry
          yield from scantree(entry.path, depth, dir) 
      else:
        if (entry.is_dir(follow_symlinks=False) and (depth is None or depth > 0)):
          yield from scantree(entry.path, depth, dir) 
        else:
          yield entry
  except:
    pass

def get_files(sourceDir, maxdepth, args):
  """Get a list of file"""
  retset = set()
  if (maxdepth < 1 ):
    maxdepth = None

  if (args.Dir == False):
    for file in { Path(x) for x in sourceDir if Path(x).is_file() }:
      if (match_file(file, args.eregs, args.full) == True):
        fileinfo = FileInfo(file)
        #print(f'{fileinfo.isdir=} {fileinfo.dir=} {fileinfo.name=}')
        if (fileinfo.full is not None ):
          retset.add(fileinfo)
  for sdir in { Path(x) for x in sourceDir if Path(x).is_dir() }:
    if (maxdepth == 1):
      if (match_file(sdir, args.eregs, args.full) == True):
        fileinfo = FileInfo(sdir)
        if (fileinfo.full is not None):
          retset.add(fileinfo)

      if (str(Path.cwd()) == str(sdir.resolve())):
        predir = str(sdir) + os.sep + '..'
        if (match_file(Path(predir), args.eregs, args.full) == True):
          fileinfo = FileInfo(Path(predir))
          if (fileinfo.full is not None):
              retset.add(fileinfo)

    for entry in scantree(sdir, maxdepth, args.Dir):
      if (match_file(entry, args.eregs, args.full) == True):
        fileinfo = FileInfo(entry)
        if (fileinfo.full is not None):
          retset.add(fileinfo)
          #print(f'{fileinfo.isdir=} {fileinfo.dir=} {fileinfo.name=}')

  return (retset)

def match_file(file, cregex, full):
  if (type(file) == os.DirEntry):
      full_name = file.path
      name = file.name
  else:
    full_name = (f'{file}')
    name = file.name
    if (name == ''):
      name = full_name
  if (full == True):
    f = full_name
  else:
    f = name

  match = True
  for ccregex in cregex:
    x = ccregex.search(f) 
    if (x is None):
      match = False
      break
  return(match)



def filter_list(flist, args):
  retset = set()
  for file in flist:
    # full means directory and file name
    if (args.full == True):
      f = f"{str(file.full)}"
    else:
      f = f"{file.name}"
    if (str(file) == '.'):
      f = f"{str(file)}"

    if (match_file(f, args.eregs, args.full) == True):
      retset.add(file)

  return(retset)

def sizeof_fmt(num, suffix="B"):
  for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
    if abs(num) < 1024.0:
      return f"{num:3.1f} {unit}{suffix}"
    num /= 1024.0
  return f"{num:.1f} Y{suffix}"

def sizeof_fmt_suffix(num, suffix="B"):
  for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
    if abs(num) < 1024.0:
      return f"{unit}{suffix}"
    num /= 1024.0
  return f"Y{suffix}"
  
def print_args(args):
  '''
  print out the args'''

  print (args)

def get_file_info(filelist):

  dic_file_info={}
  owner_max_len=0
  group_max_len=0
  size_max_len=0
  total_size_used=0
  free_space=0
  st_dev = set()
  dic_owner = {}
  dic_group = {}


  for x in filelist:
    temp_dic={}
    spinner.spin('Getting File Info: ')
    fstat = x.stat
    imode = f'{stat.filemode(fstat.st_mode)}'
    imodeoct = f'{oct(fstat.st_mode & 0o7777)[2:].zfill(4)}'
    isize = fstat.st_size
    total_size_used += isize
    isizefmt = f'{sizeof_fmt(isize)}'
    imtime = fstat.st_mtime
    imtime_date = f"{datetime.datetime.fromtimestamp(imtime).strftime('%m/%d/%Y')}"
    imtime_time = f"{datetime.datetime.fromtimestamp(imtime).strftime('%I:%M.%S %p')}"
    try:
      if (fstat.st_uid not in dic_owner):
        dic_owner[fstat.st_uid] = Path(str(x)).owner()

      iowner = f'{dic_owner[fstat.st_uid]}'
      iowner_max = len(iowner)
    except:
      iowner = f'{fstat.st_uid}'
      iowner_max = len(iowner)

    try: 
      if (fstat.st_gid not in dic_group):
        dic_group[fstat.st_gid] = Path(str(x)).group()

      igroup = f'{dic_group[fstat.st_gid]}'
      igroup_max = len(igroup)
    except:
      igroup = f'{fstat.st_gid}'
      igroup_max = len(igroup)
    
    if (x.isdir == True):
      idir = x.dir
      iname = ''
      #msg(f'is_dir: dir:{x.parent} name:{x.name}', style.RED2)
    else:
      idir = x.dir
      iname = x.name
    if (iowner_max > owner_max_len):
      owner_max_len = iowner_max
    if (igroup_max > group_max_len):
      group_max_len = igroup_max
    if (len(isizefmt) > size_max_len):
      size_max_len = len(isizefmt)

    #get free space by st_dev
    if (fstat.st_dev not in st_dev):
      st_dev.add(fstat.st_dev)
      total, used, free = shutil.disk_usage(idir)
      free_space += free

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
  temp_dic['total_size_used'] = total_size_used
  temp_dic['free_space'] = free_space
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
    if (regx == re.compile('.', flags=flags)):
      continue
    lastMatch = 0
    formattedText = ''
    for match in regx.finditer(s):
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
    total_size_used = dic_file_info['--:--MAX--:--']['total_size_used']
    free_space = dic_file_info['--:--MAX--:--']['free_space']

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
      spinner.spin('Formating Output: ')
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
        if (args.full == True or y["name"] == ''):
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
    #print(f'output_lines: {output_lines} coluns: {columns} lines_per_column: {lines_per_column}')
    if (lines_per_column * columns < output_lines):
      lines_per_column += 1
    if (lines_per_column == 0 and output_lines > 0):
      lines_per_column = 1

    #print(f'output_lines: {output_lines} coluns: {columns} lines_per_column: {lines_per_column}')
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
      #print(f'lines_per_column: {lines_per_column} columns: {int(columns)} output_lst: {len(output_lst)}')
    #print top line
    #*****************************
    #get the number of files for total line
    files =len([x['name'] for x in dic_file_info.values() if x['name'] != ''])
    #get the number of dirs for total line
    dirs = len(dir_set)

    if (ainfo == True):
      #info1 = f'Files: {files}     Dirs: {dirs}    Used:{sizeof_fmt(total_size_used)}    Free:{sizeof_fmt(free_space)}'
      info = f'Files: {files:,}    Dirs: {dirs:,}    Used: {total_size_used:,}({sizeof_fmt_suffix(total_size_used)})    Free: {free_space:,}({sizeof_fmt_suffix(free_space)})'
      #strips out any color codes and then counts
      out_size = len(re.sub('\033\[[0-9]*m', '', out))
      if (columns > 1):
        out_size = term_columns
      else:
        #Figure out how long to make the header and footer line
        #print(f'{out_size=} {len(info)=} {max_output=} {term_columns=}')
        if ( max_output < len(info) ):
            out_size = len(info)
        elif ( max_output < term_columns):
            out_size = max_output
        else:
          out_size = term_columns
          

      #string = string[:position] + new_character + string[position+1:]
      if (columns > 1):
        line_break_top = ''
        line_break_bottom = ''
        for x in (range(int(columns -1))):
          if (x < output_lines):
            line_break_top += u'\u2500' * (max_output + extra + 1)
            line_break_top += u'\u252C\u2500'

            line_break_bottom += u'\u2500' * (max_output + extra + 1)
            line_break_bottom += u'\u2534\u2500'

        line_break_top += u'\u2500' * (term_columns - len(line_break_top))
        line_break_bottom += u'\u2500' * (term_columns - len(line_break_bottom))
      else:
        line_break_top =  u'\u2500' * out_size
        line_break_bottom =  u'\u2500' * out_size
      msg(line_break_top)


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
            s += f'{output_lst[inx]:<{max_output +lendiff}}'
            if (col < columns -1):
              #Added 3 spaces between columns plus left over
              s += f'{style.RESET}{add_spaces} \u2502 '
      msg(s)

    
    # print(f'term_columns: {term_columns} max_output: {max_output} columns: {columns} tmp_length: {tmp_length} output_lines: {output_lines}')

    #get the number of files for total line
    files =len([x['name'] for x in dic_file_info.values() if x['name'] != ''])
    #get the number of dirs for total line
    dirs = len(dir_set)

    if (ainfo == True):
      msg(line_break_bottom)
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
  parser.add_argument('-l', '--long', help="Long output, same as --column -i -m -s -o -g -d -t --progress.", action='store_true')
  parser.add_argument('-L', '--LONG', help="Turn off --COLUMN -I -M -S -O -G -D -T --PROGRESS.", action='store_true')
  parser.add_argument('-f', '--full', help='Search on full path dir + name', action='store_true')
  parser.add_argument('-n', '--name', help='Display name without path.', action='store_true')
  parser.add_argument('-p', '--permission', help='Display mode (permissions) of a file.', action='store_true')
  parser.add_argument('-P', '--PERMISSION', help='Do not display mode (permissions) of a file.', action='store_true')
  parser.add_argument('--PermOct', help='Display permission as octal, but also add the first char from the mode (-p) ie. -0666, d0666 (dir).', action='store_true')
  parser.add_argument('--progress',  help='Display progress spinner.', action='store_true')
  parser.add_argument('--PROGRESS',  help='Do not display progress spinner.', action='store_true')
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
  parser.add_argument('-Dir', '--Dir', help='Display Directories only.', action='store_true')

  args = parser.parse_args()
  #in windows when you pass -e with 'find' it wrappes it with "" so need to strip off ' from the front and back of string
  if (platform.system() == 'Windows'):
    for i in range(len(args.eregs)):
      x = args.eregs[i]
      if (x[0:1] == "'" and x[-1:] == "'"):
        args.eregs[i] = x[1:-1]


  #print_args(args)

  if (args.long == True):
    spinner.display_spinner = True
  if (args.LONG == True):
    spinner.display_spinner = False

  if (args.progress == True):
    spinner.display_spinner = True
  if (args.PROGRESS == True):
    spinner.display_spinner = False

  if (((os.fstat(0) != os.fstat(1)) or args.COLOR == True ) and args.color == False):
    clear_style()
    spinner.display_spinner = False


  if (args.case == True):
    flags = 0
  else:
    flags = re.IGNORECASE

  ceregs = []
  for x in args.eregs:
    try:
      tst = re.compile(x, flags=flags)
      ceregs.append(tst)
    except:
      msg(f'Bad regex: {x}', style.RED2)
      msg('Please try again...', style.RED2)
      exit()

  mdepth = 0
  if (args.eregs == '.' and args.maxdepth == -1):
    mdepth = 1
  else:
    mdepth = args.maxdepth

  args.eregs = ceregs

  #start_time = datetime.datetime.now()
  retset = get_files(args.Dirs, mdepth, args)
  #a1 = f'get_files: {datetime.datetime.now() - start_time}'

  #start_time = datetime.datetime.now()
  #retset = filter_list(retset, args)
  #a2 = f'filter_list: {datetime.datetime.now() - start_time}'

  #start_time = datetime.datetime.now()
  # with cProfile.Profile() as pr:
  #   dic_file_info = get_file_info(retset)

  # stats = pstats.Stats(pr)
  # stats.sort_stats(pstats.SortKey.TIME)
  # stats.dump_stats(filename='f2_profiling.prof')

  dic_file_info = get_file_info(retset)


  #a3 = f'get_file_info: {datetime.datetime.now() - start_time}'

  retset = set()

  # for x in dic_file_info:
  #   print(x)
  #   if (x != '--:--MAX--:--'):
  #     print(f"dir: {dic_file_info[x]['dir']:15s} name: {dic_file_info[x]['name']}")

  print_results(dic_file_info, args)
  #print(a1)
  #print(a2)
  #print(a3)




if __name__ == "__main__":
  __version__ = '4.9 date: 6/9/2023'
  WINDOWS = False
  if (platform.system() == 'Windows'):
    WINDOWS = True
    sys.argv.append('-l')
    os.system('color')
  main()
