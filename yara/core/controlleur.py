#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:       Ivan Fontarensky
@license:      GNU General Public License 3.0
@contact:      ivan.fontarensky_at_gmail.com
"""


import os, sys
import string
import pickle
import logging

from yara.constante import *
from yara.core.highlighter import *

from PyQt4 import *
from PyQt4.QtCore import (QObject, Qt, SIGNAL, SLOT)



# Set the log configuration
logging.basicConfig( \
                filename=LOG_FILE, \
                level=logging.DEBUG, \
                format='%(asctime)s %(levelname)s - %(message)s', \
                datefmt='%d/%m/%Y %H:%M:%S', \
               )
logger = logging.getLogger(NAME)


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

if sys.platform.startswith('darwin'):
    rsrcPath = ":/images/mac"
else:
    rsrcPath = ":/images/win"

class Controlleur:
    index=-1
    def __init__(self,application,ui,mainwindow,fileName=None):

        self.app = application
        self.ui_yaraeditor = ui
        self.mainwindow = mainwindow

        mainwindow.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.setupFileActions()
        self.setupEditActions()
        self.setupHelpActions()


        #Create our YaraHighlighter derived from QSyntaxHighlighter
        self.yaraEdit = self.ui_yaraeditor.yaraEdit
        highlighter = YaraHighlighter(self.yaraEdit.document())


    def setupFileActions(self):
        tb = QtGui.QToolBar(self.mainwindow)
        tb.setWindowTitle("File Actions")
        self.mainwindow.addToolBar(tb)

        menu = QtGui.QMenu("&File", self.mainwindow)
        self.mainwindow.menuBar().addMenu(menu)

        self.actionNew = QtGui.QAction(
                QtGui.QIcon.fromTheme('document-new',
                        QtGui.QIcon(rsrcPath + '/filenew.png')),
                "&New", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.New, triggered=self.fileNew)
        tb.addAction(self.actionNew)
        menu.addAction(self.actionNew)

        self.actionOpen = QtGui.QAction(
                QtGui.QIcon.fromTheme('document-open',
                        QtGui.QIcon(rsrcPath + '/fileopen.png')),
                "&Open...", self.mainwindow, shortcut=QtGui.QKeySequence.Open,
                triggered=self.fileOpen)
        tb.addAction(self.actionOpen)
        menu.addAction(self.actionOpen)
        menu.addSeparator()

        self.actionSave = QtGui.QAction(
                QtGui.QIcon.fromTheme('document-save',
                        QtGui.QIcon(rsrcPath + '/filesave.png')),
                "&Save", self.mainwindow, shortcut=QtGui.QKeySequence.Save,
                triggered=self.fileSave, enabled=False)
        tb.addAction(self.actionSave)
        menu.addAction(self.actionSave)

        self.actionSaveAs = QtGui.QAction("Save &As...", self.mainwindow,
                priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_S,
                triggered=self.fileSaveAs)
        menu.addAction(self.actionSaveAs)
        menu.addSeparator()
 
        self.actionPrint = QtGui.QAction(
                QtGui.QIcon.fromTheme('document-print',
                        QtGui.QIcon(rsrcPath + '/fileprint.png')),
                "&Print...", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Print, triggered=self.filePrint)
        tb.addAction(self.actionPrint)
        menu.addAction(self.actionPrint)

        self.actionPrintPreview = QtGui.QAction(
                QtGui.QIcon.fromTheme('fileprint',
                        QtGui.QIcon(rsrcPath + '/fileprint.png')),
                "Print Preview...", self.mainwindow,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_P,
                triggered=self.filePrintPreview)
        menu.addAction(self.actionPrintPreview)

        self.actionPrintPdf = QtGui.QAction(
                QtGui.QIcon.fromTheme('exportpdf',
                        QtGui.QIcon(rsrcPath + '/exportpdf.png')),
                "&Export PDF...", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtCore.Qt.CTRL + QtCore.Qt.Key_D,
                triggered=self.filePrintPdf)
        tb.addAction(self.actionPrintPdf)
        menu.addAction(self.actionPrintPdf)
        menu.addSeparator()

        self.actionQuit = QtGui.QAction("&Quit", self.mainwindow,
                shortcut=QtGui.QKeySequence.Quit, triggered=self.mainwindow.close)
        menu.addAction(self.actionQuit)

    def setupEditActions(self):
        tb = QtGui.QToolBar(self.mainwindow)
        tb.setWindowTitle("Edit Actions")
        self.mainwindow.addToolBar(tb)

        menu = QtGui.QMenu("&Edit", self.mainwindow)
        self.mainwindow.menuBar().addMenu(menu)

        self.actionUndo = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-undo',
                        QtGui.QIcon(rsrcPath + '/editundo.png')),
                "&Undo", self.mainwindow, shortcut=QtGui.QKeySequence.Undo)
        tb.addAction(self.actionUndo)
        menu.addAction(self.actionUndo)

        self.actionRedo = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-redo',
                        QtGui.QIcon(rsrcPath + '/editredo.png')),
                "&Redo", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Redo)
        tb.addAction(self.actionRedo)
        menu.addAction(self.actionRedo)
        menu.addSeparator()

        self.actionCut = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-cut',
                        QtGui.QIcon(rsrcPath + '/editcut.png')),
                "Cu&t", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Cut)
        tb.addAction(self.actionCut)
        menu.addAction(self.actionCut)

        self.actionCopy = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-copy',
                        QtGui.QIcon(rsrcPath + '/editcopy.png')),
                "&Copy", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Copy)
        tb.addAction(self.actionCopy)
        menu.addAction(self.actionCopy)

        self.actionPaste = QtGui.QAction(
                QtGui.QIcon.fromTheme('edit-paste',
                        QtGui.QIcon(rsrcPath + '/editpaste.png')),
                "&Paste", self.mainwindow, priority=QtGui.QAction.LowPriority,
                shortcut=QtGui.QKeySequence.Paste,
                enabled=(len(QtGui.QApplication.clipboard().text()) != 0))
        tb.addAction(self.actionPaste)
        menu.addAction(self.actionPaste)

    def setupHelpActions(self):
        helpMenu = QtGui.QMenu("Help", self.mainwindow)
        helpMenu.addAction("About", self.about)
        helpMenu.addAction("About &Qt", QtGui.qApp.aboutQt)        

    def about(self):
        QtGui.QMessageBox.about(self, "About", 
                "Editor for Yara rules")

    def maybeSave(self):
        if not self.yaraEdit.document().isModified():
            return True

        ret = QtGui.QMessageBox.warning(self.mainwindow, "Application",
                "The document has been modified.\n"
                "Do you want to save your changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                        QtGui.QMessageBox.Cancel)

        if ret == QtGui.QMessageBox.Save:
            return self.fileSave()

        if ret == QtGui.QMessageBox.Cancel:
            return False

        return True

    def setCurrentFileName(self, fileName=''):
        self.fileName = fileName
        self.yaraEdit.document().setModified(False)

        if not fileName:
            shownName = 'untitled.yara'
        else:
            shownName = QtCore.QFileInfo(fileName).fileName()

        self.mainwindow.setWindowModified(False)

    def fileNew(self):
        if self.maybeSave():
            self.yaraEdit.clear()
            self.setCurrentFileName()

    def fileOpen(self):
        fn = QtGui.QFileDialog.getOpenFileName(self.mainwindow, "Open File...", "",
                "Yara files (*.yara);;HTML-Files (*.htm *.html);;All Files (*)")

        if fn:
            self.load(fn)

    def fileSave(self):
        if not self.fileName:
            return self.fileSaveAs()

        writer = QtGui.QTextDocumentWriter(self.fileName)
        success = writer.write(self.yaraEdit.document())
        if success:
            self.yaraEdit.document().setModified(False)

        return success

    def fileSaveAs(self):
        fn = QtGui.QFileDialog.getSaveFileName(self.mainwindow, "Save as...", "",
                "Yara files (*.yara);;HTML-Files (*.htm *.html);;All Files (*)")

        if not fn:
            return False

        lfn = fn.lower()
        if not lfn.endswith(('.yara', '.htm', '.html')):
            # The default.
            fn += '.yara'

        self.setCurrentFileName(fn)
        return self.fileSave()

    def filePrint(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        dlg = QtGui.QPrintDialog(printer, self.mainwindow)

        if self.yaraEdit.textCursor().hasSelection():
            dlg.addEnabledOption(QtGui.QAbstractPrintDialog.PrintSelection)

        dlg.setWindowTitle("Print Document")

        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.yaraEdit.print_(printer)

        del dlg

    def filePrintPreview(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        preview = QtGui.QPrintPreviewDialog(printer, self.mainwindow)
        preview.paintRequested.connect(self.printPreview)
        preview.exec_()

    def printPreview(self, printer):
        self.yaraEdit.print_(printer)

    def filePrintPdf(self):
        fn = QtGui.QFileDialog.getSaveFileName(self.mainwindow, "Export PDF", None,
                "PDF files (*.pdf);;All Files (*)")

        if fn:
            if QtCore.QFileInfo(fn).suffix().isEmpty():
                fn += '.pdf'

            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
            printer.setOutputFileName(fileName)
            self.yaraEdit.document().print_(printer)

    def load(self, f):
        if not QtCore.QFile.exists(f):
            return False

        fh = QtCore.QFile(f)
        if not fh.open(QtCore.QFile.ReadOnly):
            return False

        data = fh.readAll()
        codec = QtCore.QTextCodec.codecForHtml(data)
        unistr = codec.toUnicode(data)

        if QtCore.Qt.mightBeRichText(unistr):
            self.yaraEdit.setHtml(unistr)
        else:
            self.yaraEdit.setPlainText(unistr)

        self.setCurrentFileName(f)
        return True



# vim:ts=4:expandtab:sw=4
