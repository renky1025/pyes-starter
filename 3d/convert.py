################################################################
# 3d model converter functions
#Python=3.9
#conda install conda-forge::pythonocc-core
#pip install aspose-3d
################################################################
def stl_to_gltf(path_to_stl, out_path):
    import aspose.threed as a3d
    scene = a3d.Scene.from_file(path_to_stl)
    scene.save(out_path)
    print("Done! Exported to %s" %out_path)

def read_step(filename):
    from OCC.Core.STEPControl import STEPControl_Reader
    from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity

    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        failsonly = False
        step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
        step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity) 

        ok = step_reader.TransferRoot(1)
        _nbs = step_reader.NbShapes()
        return step_reader.Shape(1)
    else:
        raise ValueError('Cannot read the file')

def write_stl(shape, filename, fd=0.1):
    from OCC.Core.StlAPI import StlAPI_Writer
    import os

    directory = os.path.split(__name__)[0]
    stl_output_dir = os.path.abspath(directory)
    assert os.path.isdir(stl_output_dir)

    stl_file = os.path.join(stl_output_dir, filename)

    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(False)

    from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
    mesh = BRepMesh_IncrementalMesh(shape, fd)
    mesh.Perform()
    assert mesh.IsDone()

    stl_writer.Write(shape, stl_file)
    assert os.path.isfile(stl_file)

stepFile  = "737DM4M2.STEP"
stlFile = "737DM4M2.STL"
gltfFile = "737DM4M2.gltf"

data = read_step(stepFile)
write_stl(data, stlFile, 0.1)
stl_to_gltf(stlFile, gltfFile)

import os
import random

from OCC.Core.MeshDS import MeshDS_DataSource
from OCC.Core.RWStl import rwstl
from OCC.Core.MeshVS import *
from OCC.Core.Aspect import Aspect_SequenceOfColor
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_GRAY,
    Quantity_NOC_BLUE1,
    Quantity_NOC_BLACK,
)
from OCC.Core.TColStd import TColStd_DataMapOfIntegerReal

from OCC.Display.SimpleGui import init_display

stl_filename = os.path.join(stlFile)

# read the stl file
a_stl_mesh = rwstl.ReadFile(stl_filename)

# create the data source
a_data_source = MeshDS_DataSource(a_stl_mesh)

# create a mesh from the data source
a_mesh = MeshVS_Mesh()
a_mesh.SetDataSource(a_data_source)

# assign nodal builder to the mesh
a_builder = MeshVS_NodalColorPrsBuilder(
    a_mesh, MeshVS_DMF_NodalColorDataPrs | MeshVS_DMF_OCCMask
)
a_builder.UseTexture(True)

# prepare color map
aColorMap = Aspect_SequenceOfColor()
aColorMap.Append(Quantity_Color(Quantity_NOC_GRAY))
aColorMap.Append(Quantity_Color(Quantity_NOC_BLUE1))

# assign color scale map values (0..1) to nodes
aScaleMap = TColStd_DataMapOfIntegerReal()

# iterate through the nodes and add an node id and
# an appropriate value to the map
# color should be from 0. to 1.
for anId in range(1000):  # TODO use the mesh number of nodes
    aValue = random.uniform(0, 1)
    aScaleMap.Bind(anId, aValue)

# pass color map and color scale values to the builder
a_builder.SetColorMap(aColorMap)
a_builder.SetInvalidColor(Quantity_Color(Quantity_NOC_BLACK))
a_builder.SetTextureCoords(aScaleMap)
a_mesh.AddBuilder(a_builder, True)

# display
display, start_display, add_menu, add_function_to_menu = init_display()
display.Context.Display(a_mesh, True)
display.FitAll()
start_display()