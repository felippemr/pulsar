import os
import fcntl
import resource
import grp
import pwd
import signal

from .base import *


import select
if hasattr(select,'epoll'):
    IOpoll = select.epoll
else:
    IOpoll = IOselect


SIGQUIT = signal.SIGQUIT

def get_parent_id():
    return os.getppid()


def chown(path, uid, gid):
    try:
        os.chown(path, uid, gid)
    except OverflowError:
        os.chown(path, uid, -ctypes.c_int(-gid).value)
        
        
def close_on_exec(fd):
    try:
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
    except:
        pass
    
    
def __set_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)
    

def get_uid(user):
    if not user:
        return os.geteuid()
    elif user.isdigit() or isinstance(user, int):
        return int(user)
    else:
        return pwd.getpwnam(user).pw_uid
    
def get_gid(group):
    if not group:
        return os.getegid()
    elif group.isdigit() or isinstance(group, int):
        return int(group)
    else:
        return grp.getgrnam(group).gr_gid
    

def setpgrp():
    os.setpgrp()


    
def daemonize():
    """\
    Standard daemonization of a process. Code is based on the
    ActiveState recipe at:
        http://code.activestate.com/recipes/278731/
    """
    if os.fork() == 0: 
        os.setsid()
        if os.fork() != 0:
            os.umask(0) 
        else:
            os._exit(0)
    else:
        os._exit(0)
    
    maxfd = MAXFD

    # Iterate through and close all file descriptors.
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:    # ERROR, fd wasn't open to begin with (ignored)
            pass
    
    os.open(REDIRECT_TO, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)