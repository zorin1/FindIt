# Introduction  
Findit.py is a Python 3 program, no extra packages need to be installed to execute the program.

Findit.py is a simple program that combines finding files and lists out the contents of a directory.

You can pass it multiple directories and multiple regular expressions (-e).  This is very powerful if you understand how regex works.  When you pass multiple regexs it is doing an AND so it reduces the result sets. It did not make sense to do an OR since you can always do that in a regular expression 'house|home|apartment' and this would find any of those words.

For the most part if you capitalize the flags this mean turn it off.  If use the -l flag this will display the bunch of options by default but it you wanted to turn off the the date and time of the file you would do -D -T or shorthand -DT.

Please take a look at the help page for more information.

I hope that you find this somewhat useful.

# Help Page
```
usage: findit.py [-h] [-a] [-c] [--column] [--COLUMN] [-i] [-I] [-e EREGS [EREGS ...]] [-l] [-L] [-f] [-n] [-p] [-P] [--PermOct] [--progress] [--PROGRESS] [-s] [-S] [-o] [-O] [-g] [-G]
                 [-d] [-D] [-t] [-T] [-m MAXDEPTH] [--COLOR] [--color] [--version] [-R] [-od] [-os]
                 [Dirs ...]

findit.py version: 4.6 date: 6/24/2022
This is basically a simple ls and find built into one.
Run it with no arguments is the same as doing -e "." -m1.
The -e "." mean match everything, -m1 just show one level, so the current dir.
You can pass it multiple dirs or files, and with the -e you can pass it mutiple regex.
If you wanted to search for a file that has the name "hello" in it that might be located in 2 dirs:
findit.py ~/Downloads ~/Documents -e "hello"
If you wanted to find the words "hello" and "hi" you would do:
findit.py ~/Downloads ~/Documents -e "hello|hi"

positional arguments:
  Dirs                  List of directories or files to search, default is the current dir

options:
  -h, --help            show this help message and exit
  -a, --absolute        Expand dir.
  -c, --case            Case sensitivity.
  --column              Display in columns if possible.
  --COLUMN              Do not display in columns.
  -i, --info            Display info footer.
  -I, --INFO            Do not Display info footer.
  -e EREGS [EREGS ...], --eregs EREGS [EREGS ...]
                        Multiple regular expressions, default is '.' match everything
  -l, --long            Long output, same as --column -i -m -s -o -g -d -t --progress.
  -L, --LONG            Turn off --COLUMN -I -M -S -O -G -D -T --PROGRESS.
  -f, --full            Search on full path dir + name
  -n, --name            Display name without path.
  -p, --permission      Display mode (permissions) of a file.
  -P, --PERMISSION      Do not display mode (permissions) of a file.
  --PermOct             Display permission as octal, but also add the first char from the mode (-p) ie. -0666, d0666 (dir).
  --progress            Display progress spinner.
  --PROGRESS            Do not display progress spinner.
  -s, --size            Display file size.
  -S, --SIZE            Do not display file size.
  -o, --owner           Display owner of a file.
  -O, --OWNER           Do not display owner of a file.
  -g, --group           Display group user of a file.
  -G, --GROUP           Do not display group user of a file.
  -d, --date            Display modified date of a file.
  -D, --DATE            Do not modified display date a file.
  -t, --time            Display modified time of file.
  -T, --TIME            Do not display modified time of a file.
  -m MAXDEPTH, --maxdepth MAXDEPTH
                        How many directory levels to show. If not set then show all.
  --COLOR               Do not display color.
  --color               Display color.
  --version             show the version number and exit
  -R, --reverse         reverse the sort order.
  -od, --orderdate      Order by date.
  -os, --ordersize      Order by size.
  -Dir, --Dir           Display Directories only.
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

Find the word 'dog' or 'house' starting from your current directory.
```
findit.py -e 'dog|house'
```

Example 4:

Find the word 'dog' and then the word 'house' from root.  This will first find all the files with the word 'dog' in it, then it will filter that list with a match of 'house'.  So both the words have to be in the file name.
```
findit.py / -e 'dog' 'house'
```

Example 5:

Find the word 'dog' and it can also be part of the directory like ~/home/Pictures/Dog/mypet.jpg.  Also notice that by default it is not case sensitive.  If you care about case you can use the -c flag.
```
findit.py ~ -f -e 'dog'
```

Example 6:

Find all python programs from your current directory.
```
findit.py -e '\.py$'
```

Example 7:

You want to get the full path of a program so you can cut and paste this for some reason.
```
findit.py -a -e 'findit.py'
```

# Why did I create findit.py
I just wanted a simple way to list files and find files without having to use the find command.  I also wanted to learn Python and thought it would be fun to be able to pass regular expressions.

The code is not the best and it is not that fast but for simple searches it’s fine for my needs.

