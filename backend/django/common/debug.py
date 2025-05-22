
import traceback
import os, sys, time

TRACEBACK_SEPARATOR = "--------------------------------\n"

def getTraceback(printFileName = True, hideFuncs = None, hideFiles = None):
    """
    Renvoie une chaine de caracteres avec la pile d'appels
    Les fonctions hideFuncs sont masquees
    """
    # Fonctions cachées
    if hideFuncs is None:
        hideFuncs = {'MainLoop', 'launchApp', 'launchSecurity2', 'launchSecurity1', 'main',
                     'notifyEvent', 'PostEvent', '<module>', 'psyco_thread_stub'}
    hideFuncs     = set(hideFuncs).union({"getTraceBack", "getTraceback"})
    # Fichiers cachés
    if hideFiles is None:
        hideFiles = {os.path.join("opl", "base", "wrapinit.py"), }
    hideFiles = set(hideFiles)
    # Récupération des informations
    currentFrame    = sys._getframe(0)
    tbData          = traceback.extract_stack(currentFrame)
    # Configuration de l'affichage
    res             = 52 * '=' + " Traceback: " + 52 * '=' + "\n"
    form            = "{prompt}{function: <30}"
    if printFileName:
        form        += " {filename: <75}{line: >5}"
    form            += "\n"
    res             += form.format(prompt = " " * 4, filename = "FILENAME", line = "LINE", function = "FUNCTION/METHOD")
    formKargs       = {"prompt" : "  > "}
    # Mise en forme des résultats
    for i in range(len(tbData) - 1, -1, -1) :
        tbLine  = tbData[i]
        filename, lineno, funcName, dummy = tbLine
        formKargs.update({"filename" : filename, "line" : lineno, "function" : funcName})
        if funcName in hideFuncs or any(filename.endswith(f) for f in hideFiles):
            continue
        res += form.format(**formKargs)
    return res + "=" * 116 + "\n"

getTraceBack = getTraceback # parceque marre de se tromper

def where(fcn):
    """
    Affiche le fichier et le n° de ligne de début d'une fonction
    """
    print('-> {fcn.co_name} @{fcn.co_filename} #{fcn.co_firstlineno}'.format(fcn = fcn.func_code))

import itertools, traceback, os
plopnum = itertools.count(0)

def plop(*args, **kargs):
    """
    Affiche les arguments convertis en chaines de caractères.

    Keywords possibles pour le format (à mette entre accolades):
        time:       date + heure
        file:       nom du fichier
        line:       numéro de ligne
        function:   nom de la fonction/méthode
        num:        compteur global autoincrémenté
        args:       arguments de la fonction séparés par des espaces
    """
    format  = kargs.get("format", "{time} ### {file}@{line} - {function}() ###\n {num} > {args}")
    stack   = traceback.extract_stack(limit=2)
    filename, line, funcname, dummy = stack[0]
    d = {"line" : line, "function" : funcname, "num" : "%5i" % plopnum.next()}
    try :
        d["file"] = os.path.split(filename)[1]
    except IndexError:
        d["file"] = filename
    if len(args) == 0:
        d["args"] = u"plop !"
    else:
        d["args"] = " ".join(tuple(str(a) for a in args))
    d["time"] = time.strftime("%d-%m-%Y %H:%M:%S")
    print(format.format(**d))

def printStackTraces():
    """
    Imprime sur la sortie standard les piles de tous les threads Python.
    """
    print(getStackTraces(bText = True))

def getStackTraces(bText = False, identifier = None):
    """
    Récupère les piles de tous les threads Python.
    """
    code = {}
    for threadId, stack in sys._current_frames().items():
        if identifier is not None and threadId != identifier:
            continue
        if threadId in code:
            print("Stacktraces error: same thread repported twice")
            code[threadId].append("-" * 50)
        else:
            code[threadId] = []
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code[threadId].append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code[threadId].append("  %s" % (line.strip()))

    if bText:
        header = u'=' * 30 + u' ThreadID: %s ' + u'=' * 30 + u'\n'
        res    = []
        for threadId, lines in code.iteritems():
            strLines = []
            for line in lines:
                try:    strLines.append(unicode(line))
                except: strLines.append(u"  <UNICODE ENCODE ERROR>")
            res.append(header % threadId + u'\n'.join(strLines))
        return u"\n".join(res)
    return code
