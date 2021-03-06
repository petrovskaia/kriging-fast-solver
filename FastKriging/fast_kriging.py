# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FastKriging
								 A QGIS plugin
 Performs fast kriging on uniform grid of points
							  -------------------
		begin				 : 2017-12-18
		git sha				 : $Format:%H$
		copyright			 : (C) 2017 by Skoltech NLA course students
		email				 : anna.petrovskaia@skoltech.ru
 ***************************************************************************/

/***************************************************************************
 *																		   *
 *	 This program is free software; you can redistribute it and/or modify  *
 *	 it under the terms of the GNU General Public License as published by  *
 *	 the Free Software Foundation; either version 2 of the License, or	   *
 *	 (at your option) any later version.								   *
 *																		   *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from fast_kriging_dialog import FastKrigingDialog
import os.path


class FastKriging:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		print('__init__')
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
	
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'FastKriging_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		
		
		# Declare instance attributes
		self.actions = []
		self.menu = self.tr(u'&Fast Kriging')
		# TODO: We are going to let the user set this up in a future iteration
		self.toolbar = self.iface.addToolBar(u'FastKriging')
		self.toolbar.setObjectName(u'FastKriging')
		


	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('FastKriging', message)


	def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):
		"""Add a toolbar icon to the toolbar.

		:param icon_path: Path to the icon for this action. Can be a resource
			path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
		:type icon_path: str

		:param text: Text that should be shown in menu items for this action.
		:type text: str

		:param callback: Function to be called when the action is triggered.
		:type callback: function

		:param enabled_flag: A flag indicating if the action should be enabled
			by default. Defaults to True.
		:type enabled_flag: bool

		:param add_to_menu: Flag indicating whether the action should also
			be added to the menu. Defaults to True.
		:type add_to_menu: bool

		:param add_to_toolbar: Flag indicating whether the action should also
			be added to the toolbar. Defaults to True.
		:type add_to_toolbar: bool

		:param status_tip: Optional text to show in a popup when mouse pointer
			hovers over the action.
		:type status_tip: str

		:param parent: Parent widget for the new action. Defaults None.
		:type parent: QWidget

		:param whats_this: Optional text to show in the status bar when the
			mouse pointer hovers over the action.

		:returns: The action that was created. Note that the action is also
			added to self.actions list.
		:rtype: QAction
		"""
		print('add_action')
		# Create the dialog (after translation) and keep reference
		self.dlg = FastKrigingDialog()

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""
		print('initGui')
		icon_path = ':/plugins/FastKriging/icon.png'
		self.add_action(
			icon_path,
			text=self.tr(u'Performs fast kriging on uniform grid of points'),
			callback=self.run,
			parent=self.iface.mainWindow())


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&Fast Kriging'),
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar
		
	def select_output_file(self):
		print("select_output_file")
		filename = QFileDialog.getSaveFileName(self.dlg, "Save prediction as ","", '*.txt')
		print("filename"+str(filename))
		self.dlg.lineEdit.setText(filename)
	
	
	def run(self):
		"""Run method that performs all the real work"""
		print('run')
		layers = self.iface.legendInterface().layers()
		layer_list = []
		import numpy as np
		for layer in layers:
			layer_list.append(layer.name())
		
		selectedLayerIndex = self.dlg.comboBox.currentIndex()
		selectedLayer = layers[selectedLayerIndex]
		
		from osgeo import gdal
		
		#raster_layer = selectedLayer.dataProvider().identify(selectedLayer.IdentifyFormatValue).results().values()
	
		
		# layer = selectedLayer.raster
		# gtif = layer.ReadRaster(xoff=0, yoff=0,
						   # xsize=band.XSize, ysize=1,
						   # buf_xsize=band.XSize, buf_ysize=1,
						   # buf_type=gdal.GDT_Float32)
						   
		provider = selectedLayer.dataProvider()

		extent = provider.extent()

		rows = layer.height()
		cols = layer.width()

		xmin = extent.xMinimum()
		ymax = extent.yMaximum()
		xsize = layer.rasterUnitsPerPixelX()
		ysize = layer.rasterUnitsPerPixelY()

		print rows, cols

		block = provider.block(1, extent, cols, rows)

		values = [ [] for i in range(rows) ]

		for i in range(rows):
			for j in range(cols):
				if block.value(i,j) == 1 and block.value(i-1,j) == 16:
					print "yes1", i, j
					block.setValue(i,j,-9999)
					values[i].append(block.value(i,j))
				elif block.value(i,j) == 1 and block.value(i-1,j) == 4:
					print "yes2", i, j
					block.setValue(i,j,1)
					values[i].append(block.value(i,j))
				else:
					values[i].append(block.value(i,j))

		raster = np.array(values)
		print (raster)
			
				
		self.dlg.comboBox.clear()		
		self.dlg.comboBox.addItems(layer_list)
		
		self.dlg.lineEdit.clear()
		self.dlg.pushButton.clicked.connect(self.select_output_file)
		
		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec_()
		
		print('result ' + str(result))
		#See if OK was pressed
		if result:
			#Do something useful here - delete the line containing pass and
			#substitute with your code.
			filename = self.dlg.lineEdit.text()
			output_file = open(filename, 'w')

			selectedLayerIndex = self.dlg.comboBox.currentIndex()
			selectedLayer = layers[selectedLayerIndex]
			fields = selectedLayer.pendingFields()
			fieldnames = [field.name() for field in fields]

			for f in selectedLayer.getFeatures():
				line = ','.join(unicode(f[x]) for x in fieldnames) + '\n'
				unicode_line = line.encode('utf-8')
				output_file.write(unicode_line)
			output_file.close()
			
		pass
