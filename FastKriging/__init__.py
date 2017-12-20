# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FastKriging
                                 A QGIS plugin
 Performs fast kriging on uniform grid of points
                             -------------------
        begin                : 2017-12-18
        copyright            : (C) 2017 by Skoltech NLA course students
        email                : anna.petrovskaia@skoltech.ru
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FastKriging class from file FastKriging.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fast_kriging import FastKriging
    return FastKriging(iface)
