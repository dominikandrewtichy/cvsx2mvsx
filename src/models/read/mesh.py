from numpy import ndarray
from pydantic import BaseModel

from src.models.read.common import (
    CifFile,
    VolumeData3dInfo,
)


class Mesh(BaseModel):
    id: ndarray[int]


class MeshVertex(BaseModel):
    mesh_id: ndarray[int]
    vertex_id: ndarray[int]
    x: ndarray[float]
    y: ndarray[float]
    z: ndarray[float]


class MeshTriangle(BaseModel):
    mesh_id: ndarray[int]
    vertex_id: ndarray[int]


class MeshBlock(BaseModel):
    volume_data_3d_info: VolumeData3dInfo
    mesh: Mesh
    mesh_vertex: MeshVertex
    mesh_triangle: MeshTriangle


class MeshCif(CifFile):
    mesh_block: MeshBlock
