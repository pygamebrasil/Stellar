#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Emilio Coppola
#
# This file is part of Stellar.
#
# Stellar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Stellar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Stellar.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


import sys
import os
import shutil
import syntax

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerPython

from autocomplete import CompletionTextEdit

class SimplePythonEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(SimplePythonEditor, self).__init__(parent)

        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, 40)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.connect(self,
            SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
            self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#ee1111"),
            self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        #replacing tabs for 4 spaces
        self.setIndentationWidth(4)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        #self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        #self.setMinimumSize(600, 450)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)
            
class ScriptGUI(QtGui.QWidget):
  
    def __init__(self, main, FileName, dirname, parent):
        super(ScriptGUI, self).__init__(main)
        
        self.main = main
        self.parent = parent
        self.dirname = dirname
        self.FileName = FileName
        self.initUI()

    def initUI(self):
        self.ContainerGrid = QtGui.QGridLayout(self.main)
        self.ContainerGrid.setMargin (0)
        
        editor = self.textEdit = SimplePythonEditor()
        
        self.LblName = QtGui.QLabel('Name:')
        self.nameEdit = QtGui.QLineEdit(self.FileName)
        self.nameEdit.textChanged[str].connect(self.onChanged)
		
        saveAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'tick.png')), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveScript)
		
        exportAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'save.png')), 'Export', self)
        exportAction.triggered.connect(self.exportScript)
		
        importAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'folder.png')), 'Open', self)
        importAction.triggered.connect(self.openScript)

        self.undoAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'undo.png')), 'Undo', self)
        self.undoAction.triggered.connect(self.undo)
        
        self.redoAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'redo.png')), 'Redo', self)
        self.redoAction.triggered.connect(self.redo)
        
        self.whitespacevisAction = QtGui.QAction(QtGui.QIcon(os.path.join('Data', 'font.png')), 'White Space', self)
        self.whitespacevisAction.triggered.connect(self.whitespace)
        self.visible= False
		
        self.toolbar = QtGui.QToolBar('Script Toolbar')
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        self.toolbar.addAction(saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(exportAction)
        self.toolbar.addAction(importAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.undoAction)
        self.toolbar.addAction(self.redoAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.whitespacevisAction)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.LblName)
        self.toolbar.addWidget(self.nameEdit)


        self.ContainerGrid.setSpacing(0)
        self.ContainerGrid.addWidget(editor, 1, 0,1,15)
        self.ContainerGrid.addWidget(self.toolbar, 0, 0)
		
        self.startopen()
        
        self.main.setWindowTitle("Script Properties: "+ self.FileName)
        

        
        self.show()
        
     

    def onChanged(self, text):
        self.main.setWindowTitle("Script Properties: "+ text)
        self.main.setWindowIcon(QtGui.QIcon(os.path.join('Data', 'addscript.png')))
        fname = self.FileName + ".py"
        finalname = str(text) + ".py"

        #rename file in folder
        os.rename(os.path.join(self.dirname, "Scripts", str(self.FileName)) + ".py",
                  os.path.join(self.dirname, "Scripts", finalname))
        
        #rename file in tree widget
        self.parent.updatetree()
        self.FileName = text

    def whitespace(self):
        self.visible^= True
        self.textEdit.setWhitespaceVisibility(self.visible)

    def undo(self):
        self.textEdit.undo()
        
    def redo(self):
        self.textEdit.redo()
	
    def exportScript(self):
        #print str(self.dirname)+ ("/Scripts/") + str(self.FileName)+".py"
        fname = os.path.join(self.dirname, "Scripts", str(self.FileName))+ ".py"
        with open(fname, 'w') as f:    
            data = self.textEdit.text()
            f.write(data)
            f.close()

    def saveScript(self):
        #print str(self.dirname)+ ("/Scripts/") + str(self.FileName)+".py"
        fname = os.path.join(self.dirname, "Scripts", str(self.FileName)) + ".py"
        with open(fname, 'w') as f:    
            data = self.textEdit.text()
            f.write(data)
            f.close()
        self.main.close()
			
    def startopen(self):
        fname = os.path.join(self.dirname, "Scripts", str(self.FileName)) + ".py"

        with open(fname, 'r') as f:
            data = f.read()
            self.textEdit.setText(data)
            f.close()
			
    def openScript(self):

        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                str(os.getcwd()))

        if fname == '':
            return

        with open(fname, 'r') as f:
            data = f.read()
            self.textEdit.setText(data)