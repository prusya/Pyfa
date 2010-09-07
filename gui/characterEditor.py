#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import wx
import wx.gizmos
from gui import bitmapLoader
import controller

class CharacterEditor (wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__ (self, parent, id=wx.ID_ANY, title=u"pyfa: Character Editor", pos=wx.DefaultPosition,
                            size=wx.Size(641, 450), style=wx.CAPTION | wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSizeHintsSz(wx.Size(640, 450), wx.DefaultSize)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.navSizer = wx.BoxSizer(wx.HORIZONTAL)

        cChar = controller.Character.getInstance()
        charList = cChar.getCharacterList()

        self.btnSave = wx.Button(self, wx.ID_SAVE)
        self.btnSave.Hide()
        self.btnSave.Bind(wx.EVT_BUTTON, self.processRename)

        self.characterRename = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.characterRename.Hide()
        self.characterRename.Bind(wx.EVT_TEXT_ENTER, self.processRename)

        self.skillTreeChoice = wx.Choice(self, wx.ID_ANY, style=wx.CB_READONLY)

        for i, info in enumerate(charList):
            id, name = info
            self.skillTreeChoice.Insert(name, i, id)

        self.skillTreeChoice.SetSelection(0)

        self.navSizer.Add(self.skillTreeChoice, 1, wx.ALL | wx.EXPAND, 5)

        buttons = (("new", wx.ART_NEW),
                   ("copy", wx.ART_COPY),
                   ("rename", bitmapLoader.getBitmap("rename", "icons")),
                   ("delete", wx.ART_DELETE))

        size = None
        for name, art in buttons:
            bitmap = wx.ArtProvider.GetBitmap(art) if isinstance(art, unicode) else art
            btn = wx.BitmapButton(self, wx.ID_ANY, bitmap)
            if size is None:
                size = btn.GetSize()

            btn.SetMinSize(size)
            btn.SetMaxSize(size)

            btn.SetToolTipString("%s character" % name.capitalize())
            btn.Bind(wx.EVT_BUTTON, getattr(self, name))
            setattr(self, "btn%s" % name.capitalize(), btn)
            self.navSizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        charID = self.getActiveCharacter()
        if cChar.getCharName(charID) == "All 0":
            self.btnDelete.Enable(False)
            self.btnRename.Enable(False)

        mainSizer.Add(self.navSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.viewsNBContainer = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        self.sview = SkillTreeView(self.viewsNBContainer)
        self.iview = ImplantsTreeView(self.viewsNBContainer)
        self.aview = APIView(self.viewsNBContainer)

        self.viewsNBContainer.AddPage(self.sview, "Skills")
        self.viewsNBContainer.AddPage(self.iview, "Implants")
        self.viewsNBContainer.AddPage(self.aview, "API")

        mainSizer.Add(self.viewsNBContainer, 1, wx.EXPAND | wx.ALL, 5)

        self.descriptionBox = wx.StaticBox(self, wx.ID_ANY, u"Description")
        sbSizerDescription = wx.StaticBoxSizer(self.descriptionBox, wx.HORIZONTAL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN)

        self.description = wx.StaticText(self, wx.ID_ANY, u"\n\n\n")
        self.description.Wrap(-1)
        sbSizerDescription.Add(self.description, 0, wx.ALL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 2)

        mainSizer.Add(sbSizerDescription, 0, wx.ALL | wx.EXPAND, 5)

        bSizerButtons = wx.BoxSizer(wx.HORIZONTAL)

        self.btnOK = wx.Button(self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerButtons.Add(self.btnOK, 0, wx.ALL, 5)

        self.btnCancel = wx.Button(self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizerButtons.Add(self.btnCancel, 0, wx.ALL, 5)

        mainSizer.Add(bSizerButtons, 0, wx.ALIGN_RIGHT, 5)


        self.SetSizer(mainSizer)
        self.Layout()

        self.description.Hide()

        self.Centre(wx.BOTH)

        self.registerEvents()

    def registerEvents(self):
        self.Bind(wx.EVT_CLOSE, self.closeEvent)
        self.skillTreeChoice.Bind(wx.EVT_CHOICE, self.charChanged)
        self.sview.skillTreeListCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.updateDescription)

    def closeEvent(self, event):
        pass

    def charChanged(self, event):
        event.Skip()
        self.sview.skillTreeListCtrl.DeleteChildren(self.sview.root)
        self.sview.populateSkillTree()
        cChar = controller.Character.getInstance()
        charID = self.getActiveCharacter()
        if cChar.getCharName(charID) in ("All 0", "All 5"):
            self.btnRename.Enable(False)
            self.btnDelete.Enable(False)
        else:
            self.btnRename.Enable(True)
            self.btnDelete.Enable(True)

    def updateDescription(self, event):
        root = event.Item
        tree = self.sview.skillTreeListCtrl
        cChar = controller.Character.getInstance()
        data = tree.GetPyData(root)
        if data == None:
            return

        if tree.GetChildrenCount(root) == 0:
            description = cChar.getSkillDescription(data)
        else:
            description = cChar.getGroupDescription(data)

        self.description.SetLabel(description)
        self.description.Wrap(620)
        self.description.Show()

    def getActiveCharacter(self):
        selection = self.skillTreeChoice.GetCurrentSelection()
        return self.skillTreeChoice.GetClientData(selection) if selection is not None else None

    def new(self, event):
        cChar = controller.Character.getInstance()
        charID = cChar.new()
        id = self.skillTreeChoice.Append(cChar.getCharName(charID), charID)
        self.skillTreeChoice.SetSelection(id)
        self.btnDelete.Enable(True)
        self.btnRename.Enable(True)
        self.rename(event)

    def rename(self, event):
        self.skillTreeChoice.Hide()
        self.characterRename.Show()
        self.navSizer.Replace(self.skillTreeChoice, self.characterRename)
        self.characterRename.SetFocus()
        for btn in (self.btnNew, self.btnCopy, self.btnRename, self.btnDelete):
            btn.Hide()
            self.navSizer.Remove(btn)

        self.btnSave.Show()
        self.navSizer.Add(self.btnSave, 0, wx.ALIGN_CENTER)
        self.navSizer.Layout()

        cChar = controller.Character.getInstance()
        currName = cChar.getCharName(self.getActiveCharacter())
        self.characterRename.SetValue(currName)
        self.characterRename.SetSelection(0, len(currName))

    def processRename(self, event):
        cChar = controller.Character.getInstance()
        newName = self.characterRename.GetLineText(0)
        charID = self.getActiveCharacter()
        cChar.rename(charID, newName)

        self.skillTreeChoice.Show()
        self.characterRename.Hide()
        self.navSizer.Replace(self.characterRename, self.skillTreeChoice)
        for btn in (self.btnNew, self.btnCopy, self.btnRename, self.btnDelete):
            btn.Show()
            self.navSizer.Add(btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        self.navSizer.Remove(self.btnSave)
        self.btnSave.Hide()
        self.navSizer.Layout()
        selection = self.skillTreeChoice.GetCurrentSelection()
        self.skillTreeChoice.Delete(selection)
        self.skillTreeChoice.Insert(newName, selection, charID)
        self.skillTreeChoice.SetSelection(selection)

    def copy(self, event):
        cChar = controller.Character.getInstance()
        charID = cChar.copy(self.getActiveCharacter())
        id = self.skillTreeChoice.Append(cChar.getCharName(charID), charID)
        self.skillTreeChoice.SetSelection(id)
        self.btnDelete.Enable(True)
        self.btnRename.Enable(True)
        self.rename(event)

    def delete(self, event):
        cChar = controller.Character.getInstance()
        cChar.delete(self.getActiveCharacter())
        sel = self.skillTreeChoice.GetSelection()
        self.skillTreeChoice.Delete(sel)
        self.skillTreeChoice.SetSelection(sel - 1)
        newSelection = self.getActiveCharacter()
        if cChar.getCharName(newSelection) in ("All 0", "All 5"):
            self.btnDelete.Enable(False)
            self.btnRename.Enable(False)

class SkillTreeView (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)

        pmainSizer = wx.BoxSizer(wx.VERTICAL)

        tree = self.skillTreeListCtrl = wx.gizmos.TreeListCtrl(self, wx.ID_ANY, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        pmainSizer.Add(tree, 1, wx.EXPAND | wx.ALL, 5)


        self.imageList = wx.ImageList(16, 16)
        tree.SetImageList(self.imageList)
        self.skillBookImageId = self.imageList.Add(bitmapLoader.getBitmap("skill_small", "icons"))

        tree.AddColumn("Skill")
        tree.AddColumn("Level")
        tree.SetMainColumn(0)

        self.root = tree.AddRoot("Skills")
        tree.SetItemText(self.root, "Levels", 1)

        tree.SetColumnWidth(0, 500)

        self.populateSkillTree()

        tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.expandLookup)

        self.SetSizer(pmainSizer)
        self.Layout()

    def populateSkillTree(self):
        cChar = controller.Character.getInstance()
        groups = cChar.getSkillGroups()
        imageId = self.skillBookImageId
        root = self.root
        tree = self.skillTreeListCtrl

        for id, name in groups:
            childId = tree.AppendItem(root, name, imageId)
            tree.SetPyData(childId, id)
            tree.AppendItem(childId, "dummy")

        tree.SortChildren(root)

    def expandLookup(self, event):
        root = event.Item
        tree = self.skillTreeListCtrl
        child, cookie = tree.GetFirstChild(root)
        if tree.GetItemText(child) == "dummy":
            tree.Delete(child)

            #Get the real intrestin' stuff
            cChar = controller.Character.getInstance()
            char = self.Parent.Parent.getActiveCharacter()
            for id, name in cChar.getSkills(tree.GetPyData(root)):
                iconId = self.skillBookImageId
                childId = tree.AppendItem(root, name, iconId, data=wx.TreeItemData(id))
                tree.SetItemText(childId, str(cChar.getSkillLevel(char, id)), 1)

            tree.SortChildren(root)

class ImplantsTreeView (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)

        pmainSizer = wx.BoxSizer(wx.VERTICAL)

        self.ImplantsTreeCtrl = wx.TreeCtrl(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)
        pmainSizer.Add(self.ImplantsTreeCtrl, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(pmainSizer)
        self.Layout()

class APIView (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL)

        pmainSizer = wx.BoxSizer(wx.HORIZONTAL)

        fgSizerInput = wx.FlexGridSizer(2, 2, 0, 0)
        fgSizerInput.AddGrowableCol(1)
        fgSizerInput.SetFlexibleDirection(wx.BOTH)
        fgSizerInput.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticIDText = wx.StaticText(self, wx.ID_ANY, u"ID", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticIDText.Wrap(-1)
        fgSizerInput.Add(self.m_staticIDText, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputID = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizerInput.Add(self.inputID, 1, wx.ALL | wx.EXPAND, 5)

        self.m_staticKeyText = wx.StaticText(self, wx.ID_ANY, u"API KEY", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticKeyText.Wrap(-1)
        fgSizerInput.Add(self.m_staticKeyText, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.inputKey = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizerInput.Add(self.inputKey, 0, wx.ALL | wx.EXPAND, 5)

        pmainSizer.Add(fgSizerInput, 1, wx.EXPAND, 5)

        self.btnUpdate = wx.Button(self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        pmainSizer.Add(self.btnUpdate, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.SetSizer(pmainSizer)
        self.Layout()

