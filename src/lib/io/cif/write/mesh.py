from ciftools.serialization import create_binary_writer

from lib.models.cif.read.mesh import MeshCif
from lib.models.cif.write.mesh.mesh import MeshCategory
from lib.models.cif.write.mesh.mesh_vertex import MeshVertexCategory
from lib.models.cif.write.volume.volume_data_3d_info import VolumeData3dInfoCategory
from src.lib.models.cif.write.mesh.mesh_triangle import MeshTriangleCategory


def mesh_to_bcif(mesh: MeshCif) -> bytes:
    writer = create_binary_writer(encoder="VolumeServer")

    writer.start_data_block("MESH_DATA")

    writer.write_category(
        VolumeData3dInfoCategory,
        [
            mesh.mesh_block.volume_data_3d_info,
        ],
    )
    writer.write_category(
        MeshCategory,
        [
            mesh.mesh_block.mesh,
        ],
    )
    writer.write_category(
        MeshVertexCategory,
        [
            mesh.mesh_block.mesh_vertex,
        ],
    )
    writer.write_category(
        MeshTriangleCategory,
        [
            mesh.mesh_block.mesh_triangle,
        ],
    )

    return writer.encode()
