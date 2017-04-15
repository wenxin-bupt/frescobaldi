# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
LilyPond preferences page
"""


import os
import sys

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QCheckBox, QDialog, QDialogButtonBox, QFileDialog,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidgetItem,
    QPushButton, QRadioButton, QTabWidget, QVBoxLayout, QWidget, QTabWidget)

import app
import userguide
import qutil
import icons
import preferences
import lilypondinfo
import qsettings
import widgets.listedit
import widgets.urlrequester


def settings():
    s = QSettings()
    s.beginGroup("openlilylib_settings")
    return s


class OpenLilyLibPrefs(preferences.ScrolledGroupsPage):
    def __init__(self, dialog):
        super(OpenLilyLibPrefs, self).__init__(dialog)

        layout = QVBoxLayout()
        self.scrolledWidget.setLayout(layout)
        
        layout.setAlignment(Qt.AlignTop)

        self.subs = {
            'oll_root': OllRoot(self), 
            'packages': Packages(self), 
            'config': Config(self)
        }
        layout.addWidget(self.subs['oll_root'])
        layout.addWidget(self.subs['packages'])
        layout.addWidget(self.subs['config'])
        
        self.changed.connect(self.updatePage)
        
    def updatePage(self):
        oll_root = self.subs['oll_root'].directory.path()
        for s in self.subs:
            if not s == 'oll_root':
                self.subs[s].setEnabled(True if oll_root else False)


class OllRoot(preferences.Group):
    """Basic openLilyLib installation"""
    def __init__(self, page):
        super(OllRoot, self).__init__(page)

        layout = QGridLayout()
        self.setLayout(layout)
        
        self.label = QLabel()
        self.directory = widgets.urlrequester.UrlRequester()
        self.directory.changed.connect(page.changed)
        # TODO: Check installation upon change
        
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.directory, 0, 1)

        app.translateUI(self)

    def translateUI(self):
        self.setTitle(_("openLilyLib Installation directory:"))
        self.label.setText(_("Root directory:"))
        tt = (_("Root directory below which openLilyLib packages are installed."))
        self.label.setToolTip(tt)
        self.directory.setToolTip(tt)

    def loadSettings(self):
        s = settings()
        self.directory.setPath(s.value("oll-root", "", str))

    def saveSettings(self):
        s = settings()
        s.setValue('oll-root', self.directory.path())
    
    def changedRoot(self):
        pass
        # TODO: Check for proper openLilyLib installation


class Packages(preferences.Group):
    def __init__(self, page):
        super(Packages, self).__init__(page)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.instances = PackageList(self)
        self.instances.changed.connect(self.changed)
        layout.addWidget(self.instances)
        app.translateUI(self)
        userguide.openWhatsThis(self)

    def translateUI(self):
        self.setTitle(_("Installed openLilyLib packages"))

    def loadSettings(self):
        s = settings()

    def saveSettings(self):
        s = settings()


class PackageList(widgets.listedit.ListEdit):
    def __init__(self, group):
        self.updateButton = QPushButton(icons.get('document-edit'), '')
        #TODO: handle enabled state of it
        self.updateButton.setEnabled(False)
        super(PackageList, self).__init__(group)
        #self.layout().addStretch(3, 1)
        self.layout().addWidget(self.updateButton, 7, 1)

    def connectSlots(self):
        super(PackageList, self).connectSlots()
        self.listBox.itemSelectionChanged.connect(self._selectionChanged)
        self.updateButton.clicked.connect(self.updateAll)

    def addClicked(self, button):
        items = self.addPackages()
        if items:
            for i in items:
                self.addItem(i)

    def editClicked(self, button):
        item = self.listBox.currentItem()
        item and self.updatePackage(item)

    def removeClicked(self, item):
        item = self.listBox.currentItem()
        if item:
            self.removePackage(item)

    def itemDoubleClicked(self, item):
        # TODO: Make this open the package's config tab
        pass

    def _selectionChanged(self):
        # TODO: check if the package has a dedicated config tab and load it
        # otherwise load the generic one that simply displays some information
        # (from the \declarePackage command)
        pass

    def translateUI(self):
        super(PackageList, self).translateUI()
        self.editButton.setText(_("&Update..."))
        self.updateButton.setText(_("&Update all"))
        
    def createItem(self, package_name):
        return InfoItem(package_name)

    def loadSettings(self):
        s = settings()
        # TODO: 
        # Check if the packages are still installed
        # if not: deactivate (not delete)

    def saveSettings(self):
        s = settings()

    def addPackages(self):
        # Check for oll-core
        # Read manifest
        # Open dialog allowing selection of one or multiple packages
        # Determine dependencies and add them to the list of to-be-added packages
        # Depending on the presence of Git:
        # - git clone
        # - download ZIP
        # Create item for each selected list
        # - read name and description
        # - is it possible to set a tooltip for the item, with long description?
        # - set an icon if the package provides one
        items = []
        dummy = self.createItem('oll-core')
        items.append(dummy)
        dummy = self.createItem('scholarLY')
        items.append(dummy)
        return items
    
    def updatePackage(self, item):
        # Depending on the presence of Git
        # - Y
        #   - run git status (ask if anything is to be done)
        #   - ask if master should be checked out
        #   - run git pull
        #   - optionally reset to original state (maybe we have saved a stash?)
        # - N
        #   - look for the zip and compare version
        #   - if newer, download and replace
        # Note that this may take time, so it should be done with feedback (look into lilypond-version-testing)
        pass

    def removePackage(self, item):
        self.removeItem(item)
        # TODO:
        # Ask if the package really should be deleted
        # - delete from disk
        # - update list
        
    def updateAll(self, item):
        # for each installed package:
        # do updatePackage
        pass
        
    def itemChanged(self, item):
        item.display()
        self.setCurrentItem(item)


class InfoItem(QListWidgetItem):
    def __init__(self, package_name):
        super(InfoItem, self).__init__()
        self._name = package_name
        # TODO: Retrieve data based on name from an openlilylib module

    def display(self):
        text = self._name
        self.setText(text)
        # TODO: Given the info object, set name, icon, short description, tooltip (long description)


class Config(preferences.Group):
    def __init__(self, page):
        super(Config, self).__init__(page)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.tabs = QTabWidget()
        # TODO: Create tabs for each installed package
        # If the package is explicitly supported there will be a dedicated Class
        # Otherwise show a generic tab just showing the info
        # (Alternative: Only show tab when package is explicitly supported and rely on the list's tooltip otherwise
        
        layout.addWidget(self.tabs)

        app.translateUI(self)

    def translateUI(self):
        self.setTitle(_("Package configuration"))

    def loadSettings(self):
        s = settings()

    def saveSettings(self):
        s = settings()


