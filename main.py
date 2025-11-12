from zipfile import ZipFile

from molviewspec import create_builder
from molviewspec.mvsx_converter import mvsj_to_mvsx

from src.convert.geometric import get_list_of_all_geometric_segmentations
from src.convert.lattice import get_list_of_all_lattice_segmentations
from src.convert.mesh import get_list_of_all_mesh_segmentations
from src.convert.volume import get_list_of_all_volumes
from src.io.cvsx_loader import load_cvsx_entry
from src.models.cvsx.cvsx_file import CVSXFile
from src.models.mvsx.mvsx_segmentation import (
    MVSXGeometricSegmentation,
    MVSXMeshSegmentation,
)
from src.models.mvsx.mvsx_volume import MVSXVolume


def convert_cvsx_to_mvsx(cvsx_path: str):
    cvsx_file: CVSXFile = load_cvsx_entry(cvsx_path)
    volumes: list[MVSXVolume] = get_list_of_all_volumes(cvsx_file)
    mesh_segmentations: list[MVSXMeshSegmentation] = get_list_of_all_mesh_segmentations(
        cvsx_file
    )
    lattice_segmentations: list[MVSXMeshSegmentation] = (
        get_list_of_all_lattice_segmentations(cvsx_file)
    )
    geometric_segmentations: list[MVSXGeometricSegmentation] = (
        get_list_of_all_geometric_segmentations(cvsx_file)
    )

    print("volumes")
    for volume in volumes:
        volume.print_fields()
        print()

    print("mesh segmentations")
    for segmentation in mesh_segmentations:
        segmentation.print_fields()
        print()

    print("lattice segmentations")
    for segmentation in lattice_segmentations:
        segmentation.print_fields()
        print()

    print("geometric segmentations")
    for segmentation in geometric_segmentations:
        segmentation.print_fields()
        print()

    builder = create_builder()
    for volume in volumes:
        with ZipFile(cvsx_path, "r") as zip_ref:
            zip_ref.extract(volume.source_filepath, "temp/volumes")
        volume_cif = builder.download(
            url=volume.destination_filepath,
        ).parse(format="bcif")
        volume_data = volume_cif.volume(channel_id=volume.channel_id)
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=volume.isovalue,
            show_faces=True,
            show_wireframe=False,
        )
        volume_representation.color(color=volume.color).opacity(opacity=0.2)
    for segmentation in geometric_segmentations[:5]:
        builder.primitives(
            opacity=segmentation.opacity,
        ).sphere(
            color=segmentation.color,
            center=segmentation.center,
            radius=segmentation.radius,
        )
    for segmentation in lattice_segmentations:
        builder.primitives(
            opacity=segmentation.opacity,
        ).mesh(
            color=segmentation.color,
            vertices=segmentation.vertices.ravel().tolist(),
            indices=segmentation.indices.ravel().tolist(),
            triangle_groups=segmentation.triangle_groups.ravel().tolist(),
        )
    state = builder.get_state()
    with open("temp/mesh.mvsj", "w") as f:
        f.write(state.model_dump_json(exclude_none=True))
    mvsj_to_mvsx(
        input_mvsj_path="temp/mesh.mvsj",
        output_mvsx_path="temp/mesh.mvsx",
    )


if __name__ == "__main__":
    convert_cvsx_to_mvsx("data/cvsx/zipped/emd-1832.cvsx")
