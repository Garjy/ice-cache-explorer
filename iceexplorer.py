###############################################################################
# ICE Cache Explorer: A viewer and reader for ICE cache data
# Copyright (C) 2010  M.A. Belzile
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# This is only needed for Python v2 but is harmless for Python v3.
#import sip
#sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

from iceviewer import ICEViewer
from icereader import get_files_from_cache_folder
from iceexporter import ICEExporter
from playback import PlaybackWidget

class ICECacheExplorerWindow(QtGui.QMainWindow):
    def __init__(self):
        super(ICECacheExplorerWindow, self).__init__()

        self.setWindowTitle("ICE Cache Explorer")

        self.viewer = ICEViewer(self)
        self.viewer.cacheLoaded.connect(self.on_cache_loaded)
        self.setCentralWidget(self.viewer)

        self.exporter_thread = ICEExporter(self)
        
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_statusbar()
        self.create_dock_windows()
                
    def load_cache_folder(self):
        folder =QtGui.QFileDialog.getExistingDirectory(self, "Select ICECache folder", ".", QtGui.QFileDialog.ShowDirsOnly)
        if not folder:
            return
        
        self.treeWidget.clear()
        self.viewer.load_folder( folder )
        
    def load_cache(self):
        fname =QtGui.QFileDialog.getOpenFileName(self, caption="Select ICECache File", directory=".", filter="ICECACHE (*.icecache)")
        if not fname:
            return

        self.statusBar().showMessage( 'Loading "%s"' % fname, 2000)
        
        self.treeWidget.clear()
        self.viewer.load_file( fname )

    def load_cache_data(self):
        item = self.treeWidget.currentItem() 
        
        if item.parent() == None:
            # top level item: load all attribute data            
            cacheindex = int( item.text(0).split(' ')[1] )
            for i in range(item.childCount()):
                attribitem = item.child(i)
                if attribitem.text(0) == 'Attribute':
                    self.load_attribute_data( attribitem, cacheindex )
            
        elif item.text(0) == 'Attribute':
            # load this attribute data
            cacheitem = item.parent()
            cacheindex = int( cacheitem.text(0).split(' ')[1] )
            self.load_attribute_data( item, cacheindex )

    def load_attribute_data( self, item, cacheindex ):
            values = []
            try:
                values = self.viewer.get_data( item.text(1), cacheindex )
            except:
                pass

            nCount = item.childCount()
            dataitem = item.child( nCount -1 )
            for i,val in enumerate(values):
                value = QtGui.QTreeWidgetItem( dataitem )
                value.setText( 0, str(i) )
                value.setText( 1, str(val) )        

    def about(self):
        QtGui.QMessageBox.about(self, "About ICE Cache Explorer",
                "<b>ICE Cache Explorer</b> Copyright (C) 2010  M.A.Belzile <br>"
                "A tool for viewing and browsing ICE cache data.<br><br>"
                "This program comes with ABSOLUTELY NO WARRANTY; for details see the GNU General Public License. "
                "This is free software, and you are welcome to redistribute it under certain conditions; see the GNU General Public License for details.")

    def close( self ):
        sys.exit()

    def export_selected_cache( self ):
        pass

    def export_cache_folder( self ):
        """ Convert all cache files from dir to ascii """
        folder =QtGui.QFileDialog.getExistingDirectory(self, "Select ICECache Folder", ".", QtGui.QFileDialog.ShowDirsOnly)
        if not folder:
            return

        self.exporter_thread.export_folder( folder, r'c:\temp', ('Color___', 'Size___' ) )
        
    def export_cache( self ):
        fname =QtGui.QFileDialog.getOpenFileName(self, caption="Select ICECache File", directory=".", filter="ICECACHE (*.icecache)")
        if not fname:
            return

        self.exporter_thread.export_file( fname, r'c:\temp', ('Color___', 'Size___' ) )

    def options( self ):
        pass
        
    def create_actions(self):
        self.load_cache_folder_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "&Load Cache Folder...", self, statusTip="Load Cache Folder", triggered=self.load_cache_folder)
        self.load_cache_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "Load Cache &File...", self, statusTip="Load Cache File", triggered=self.load_cache)
        self.load_cache_data_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "&Display Data", self, statusTip="Display Data", triggered=self.load_cache_data)
        self.export_cache_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "Export &Cache File...", self, statusTip="Export Cache", triggered=self.export_cache)
        self.export_selected_cache_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "Export Selected &Cache File", self, statusTip="Export Selected Cache", triggered=self.export_selected_cache)
        self.export_cache_folder_act = QtGui.QAction(QtGui.QIcon('./images/save.png'), "Export &Cache Folder...", self, statusTip="Export Cache Folder", triggered=self.export_cache_folder)

        self.quit_act = QtGui.QAction("&Quit", self, shortcut="Ctrl+Q", statusTip="Quit ICE Explorer", triggered=self.close)
        self.about_act = QtGui.QAction("&About", self, statusTip="Show About Dialog", triggered=self.about)

        self.options_act = QtGui.QAction("&Options", self, statusTip="Show Option Dialog", triggered=self.options)

        self.show_pers_act = QtGui.QAction("&Perspective", self, statusTip="Show Perspective View", triggered=self.viewer.perspective_view)
        self.show_top_act = QtGui.QAction("&Top", self, statusTip="Show Top View", triggered=self.viewer.top_view)
        self.show_front_act = QtGui.QAction("&Front", self, statusTip="Show Front View", triggered=self.viewer.front_view)
        self.show_right_act = QtGui.QAction("&Right", self, statusTip="Show Right View", triggered=self.viewer.right_view)
        self.show_left_act = QtGui.QAction("&Left", self, statusTip="Show Left View", triggered=self.viewer.left_view)

    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.load_cache_act)
        self.fileMenu.addAction(self.load_cache_folder_act)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.export_cache_act)
        self.fileMenu.addAction(self.export_cache_folder_act)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quit_act)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.options_act)
        
        self.viewMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.show_pers_act)
        self.viewMenu.addAction(self.show_top_act)
        self.viewMenu.addAction(self.show_front_act)
        self.viewMenu.addAction(self.show_right_act)
        self.viewMenu.addAction(self.show_left_act)

        #self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.about_act)

    def create_toolbars(self):
        self.viewToolBar = self.addToolBar("View")
        self.viewToolBar.addAction(self.show_pers_act)
        self.viewToolBar.addAction(self.show_top_act)
        self.viewToolBar.addAction(self.show_front_act)
        self.viewToolBar.addAction(self.show_right_act)
        self.viewToolBar.addAction(self.show_left_act)

    def create_statusbar(self):
        self.statusBar().showMessage("Ready")

    def create_dock_windows(self):
        # ICE Cache browser window
        dock = QtGui.QDockWidget("Browser", self)
        dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.treeWidget = QtGui.QTreeWidget(dock)
        self.treeWidget.setObjectName('ICECacheInspectorWidget')
        self.treeWidget.setColumnCount(2)
        self.treeWidget.headerItem().setText( 0, 'Item' )
        self.treeWidget.headerItem().setText( 1, 'Value' )
        self.treeWidget.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.treeWidget.customContextMenuRequested.connect( self.handle_browser_contextmenu )

        self.browser_contextmenu = QtGui.QMenu( self )
        self.browser_contextmenu.addAction( self.load_cache_data_act )
        self.browser_contextmenu.addAction( self.export_cache_act )

        self.attribute_contextmenu = QtGui.QMenu( self )
        self.attribute_contextmenu.addAction( self.load_cache_data_act )

        dock.setWidget(self.treeWidget)
        
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

        # playback widget
        dock = QtGui.QDockWidget("Play Back", self)
        dock.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
                
        self.playback = PlaybackWidget( self.viewer, dock )
        
        # connect playback signals to viewer slots
        self.playback.cacheChanged.connect(self.viewer.on_cache_change )        
        self.playback.startcacheChanged.connect(self.viewer.on_start_cache_change )
        self.playback.endcacheChanged.connect(self.viewer.on_end_cache_change )
        self.playback.playChanged.connect(self.viewer.on_play )
        self.playback.stopChanged.connect(self.viewer.on_stop )
        self.playback.loopChanged.connect(self.viewer.on_loop )

        dock.setWidget(self.playback)
            
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
        self.viewMenu.addAction(dock.toggleViewAction())

    def handle_browser_contextmenu(self, point):
        item = self.treeWidget.currentItem() 
        
        # show browser context menu on the widget
        if item.parent() != None and item.text(0) != 'Attribute':
            return
        
        if item.text(0) == 'Attribute':
            self.attribute_contextmenu.exec_( self.treeWidget.mapToGlobal(point) )
        else:
            self.browser_contextmenu.exec_( self.treeWidget.mapToGlobal(point) )

    def on_cache_loaded( self, cache, reader ):
        """update the browser"""
        
        # cache item
        itemcache = QtGui.QTreeWidgetItem(self.treeWidget)
        itemcache.setText( 0, 'Cache %d' % (cache) )
        self.treeWidget.addTopLevelItem( itemcache )
        
        # header items
        # Cache
        #    > Header
        #         <header items>
        headeritem = QtGui.QTreeWidgetItem( itemcache )        
        headeritem.setText( 0, 'Header' )
        headeritem.setText( 1, reader.header().name )
        version = QtGui.QTreeWidgetItem( headeritem )
        type = QtGui.QTreeWidgetItem( headeritem )
        edge_count = QtGui.QTreeWidgetItem( headeritem )
        particle_count = QtGui.QTreeWidgetItem( headeritem )
        polygon_count = QtGui.QTreeWidgetItem( headeritem )
        sample_count = QtGui.QTreeWidgetItem( headeritem )
        blob_count = QtGui.QTreeWidgetItem( headeritem )
        attribute_count = QtGui.QTreeWidgetItem( headeritem )
        
        version.setText( 0, 'Version' )
        version.setText( 1, str(reader.header().version) )
        type.setText( 0, 'Type' )
        type.setText( 1, str(reader.header().type) )
        particle_count.setText( 0, 'Particle Count' )
        particle_count.setText( 1, str(reader.header().particle_count) )
        edge_count.setText( 0, 'Edge Count' )
        edge_count.setText( 1, str(reader.header().edge_count) )
        polygon_count.setText( 0, 'Polygon Count' )
        polygon_count.setText( 1, str(reader.header().polygon_count) )
        sample_count.setText( 0, 'Sample Count' )
        sample_count.setText( 1, str(reader.header().sample_count) )
        blob_count.setText( 0, 'Blob Count' )
        blob_count.setText( 1, str(reader.header().blob_count) )
        attribute_count.setText( 0, 'Attribute Count' )
        attribute_count.setText( 1, str(reader.header().attribute_count) )                

        # attribute items
        # Cache
        #    > Header
        #         <header items>
        #    > Attribute <name>
        #         <attribute items>        
                
        for attrib in reader.attributes():
            attribitem = QtGui.QTreeWidgetItem( itemcache )
            attribitem.setText( 0, 'Attribute' )
            attribitem.setText( 1, attrib.name )

            # attribute description
            datatype = QtGui.QTreeWidgetItem( attribitem )
            structtype = QtGui.QTreeWidgetItem( attribitem )
            contexttype = QtGui.QTreeWidgetItem( attribitem )
            objid = QtGui.QTreeWidgetItem( attribitem )
            category = QtGui.QTreeWidgetItem( attribitem )
            ptlocator_size = QtGui.QTreeWidgetItem( attribitem )
            blobtype_count = QtGui.QTreeWidgetItem( attribitem )
            blobtype_names = QtGui.QTreeWidgetItem( attribitem )
            isconstant = QtGui.QTreeWidgetItem( attribitem )
            dataitem = QtGui.QTreeWidgetItem( attribitem )

            datatype.setText( 0, 'Data Type' )
            datatype.setText( 1, str(attrib.datatype) )
            structtype.setText( 0, 'Structure Type' )
            structtype.setText( 1, str(attrib.structtype) )
            contexttype.setText( 0, 'Context Type' )
            contexttype.setText( 1, str(attrib.contexttype) )
            objid.setText( 0, 'Object ID' )
            objid.setText( 1, str(attrib.objid) )
            category.setText( 0, 'Category' )
            category.setText( 1, str(attrib.category) )
            ptlocator_size.setText( 0, 'PointLocator Size' )
            ptlocator_size.setText( 1, str(attrib.ptlocator_size) )
            blobtype_count.setText( 0, 'Blob Type Count' )
            blobtype_count.setText( 1, str(attrib.blobtype_count) )
            blobtype_names.setText( 0, 'Blob Type Name' )
            blobtype_names.setText( 1, str(attrib.blobtype_names) )
            isconstant.setText( 0, 'Constant Data' )
            isconstant.setText( 1, str(attrib.isconstant) )

            # attribute data items
            # Cache
            #    > Header
            #         <header items>
            #    > Attribute <name>
            #         <attribute items>        
            #         > Data
            #              <values>
            dataitem.setText( 0, 'Data' )
            
            # values are displayed through the popup menu

if __name__ == '__main__':

    import sys
    notice = """
ICE Cache Explorer  Copyright (C) 2010  M.A.Belzile
"""
    print notice
    app = QtGui.QApplication(sys.argv)
    mainWin = ICECacheExplorerWindow()
    mainWin.show()
    sys.exit(app.exec_())
