# Introduction  
Findit.py is a Python 3 program, no extra packages need to be installed to execute the program.

Findit.py is a simple program that combines finding files and lists out the contents of a directory.

You can pass it multiple directories and multiple regular expressions (-e).  This is very powerful if you understand how regex works.  When you pass multiple regexs it is doing an AND so it reduces the result sets. It did not make sense to do an OR since you can always do that in a regular expression 'house|home|apartment' and this would find any of those words.

For the most part if you capitalize the flags this mean turn it off.  If use the -l flag this will display the bunch of options by default but it you wanted to turn off the the date and time of the file you would do -D -T or shorthand -DT.

Please take a look at the help page for more information.

I hope that you find this somewhat useful.

# Help Page
```
usage: findit.py [-h] [-a] [-b] [-c] [--column] [-i] [--ids] [-e EREGS [EREGS ...]] [-l] [-f] [-n] [-p] [--PermOct] [--progress] [-s] [-o] [-g] [-d] [-t] [-m MAXDEPTH] [--color] [-x] [--version] [-R] [-od] [-os] [-Dir] 
                [Dirs ...] 

findit.py version: 4.13 date: 3/23/2024 
This is basically a simple ls and find built into one. 
Run it with no arguments is the same as doing -e "." -m1. 
The -e "." mean match everything, -m1 just show one level, so the current dir. 
You can pass it multiple dirs or files, and with the -e you can pass it multiple regex. 
If you wanted to search for a file that has the name "hello" in it that might be located in 2 dirs: 
findit.py ~/Downloads ~/Documents -e "hello"
If you wanted to find the words "hello" and "hi" you would do: 
findit.py ~/Downloads ~/Documents -e "hello|hi" 

positional arguments: 
 Dirs                  List of directories or files to search, default is the current dir 

options: 
 -h, --help            show this help message and exit 
 -a, --absolute        Expand dir. 
 -b, --bytes           Display file size in bytes. 
 -c, --case            Case sensitivity. 
 --column, --COLUMN    Display in columns if possible. (use --COLUMN to turn off) 
 -i, -I                Display info footer. (use -I to turn off) 
 --ids                 Display UID and GID instead of user and group names. Takes precedence over -x. Best if used with -o and/or -g. 
 -e EREGS [EREGS ...], --eregs EREGS [EREGS ...] 
                       Multiple regular expressions, default is '.' match everything 
 -l, -L                Long output, same as --column -i -m -s -o -g -d -t --progress. (use -L to turn off) 
 -f, --full            Search on full path dir + name 
 -n, --name            Display name without path. 
 -p, -P                Display mode (permissions) of a file. (use -P to turn off) 
 --PermOct             Display permission as octal, but also add the first char from the mode (-p) ie. -0666, d0666 (dir). 
 --progress, --PROGRESS 
                       Display progress spinner. (use --PROGRESS to turn off) 
 -s, -S                Display file size. (use -S to turn off) 
 -o, -O                Display owner of a file. (use -O to turn off) 
 -g, -G                Display group user of a file. (use -P to turn off) 
 -d, -D                Display modified date of a file. (use -D to turn off) 
 -t, -T                Display modified time of file. (use -T to turn off) 
 -m MAXDEPTH, --maxdepth MAXDEPTH 
                       How many directory levels to show. If not set then show all. 
 --color, --COLOR      Display color. (use --COLOR to turn off) 
 -x, --truncate_names  Truncate user and group names to remove domain part. Best if used with -o and/or -g. 
 --version             show the version number and exit 
 -R, --reverse         reverse the sort order. 
 -od, --orderdate      Order by date. 
 -os, --ordersize      Order by size. 
 -Dir, --Dir           Display Directories only.
```

# Usage:

I would copy findit.py and put it into your ~/bin directory so it shows up in your PATH and then create an alias f=’findit.py -l’

Example 1:

List out files in current directory:
```
findit.py
```

Example 2: 

List files in /tmp and ~/
```
findit.py /tmp ~/
```

Example 3:

Find the word ‘dog’ or ‘house’ starting from your current directory.
```
findit.py -e ‘dog|house’
```

Example 4:

Find the word ‘dog’ and then the word ‘house’ from root.  This will first find all the files with the word ‘dog’ in it, then it will filter that list with a match of ‘house’.  So both the words have to be in the file name.
```
findit.py / -e ‘dog’ ‘house’
```

Example 5:

Find the word ‘dog’ and it can also be part of the directory like ~/home/Pictures/Dog/mypet.jpg.  Also notice that by default it is not case sensitive.  If you care about case you can use the -c flag.
```
findit.py ~ -f -e ‘dog’
```

Example 6:

Find all python programs from your current directory.
```
findit.py -e ‘\.py$’
```

Example 7:

You want to get the full path of a program so you can cut and paste this for some reason.
```
findit.py -a -e 'findit.py'
```

# Why did I create findit.py
I just wanted a simple way to list files and find files without having to use the find command.  I also wanted to learn Python and thought it would be fun to be able to pass regular expressions.

The code is not the best and it is not that fast but for simple searches it’s fine for my needs.

