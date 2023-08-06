#!/usr/bin/expect -f
set timeout -1
spawn /root/EndoFI/gdb
expect "(gdb)"
send "source /root/EndoFI/main.py\n"
expect "(gdb)"
# send "q\n