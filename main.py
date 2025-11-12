from zipfile import ZipFile

from molviewspec import create_builder
from molviewspec.builder import GlobalMetadata, Root, Snapshot, States
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
    MVSXSegmentation,
)
from src.models.mvsx.mvsx_volume import MVSXVolume


def create_index_snapshot(
    volumes: list[MVSXVolume],
    mesh_segmentations: list[MVSXMeshSegmentation],
    geometric_segmentations: list[MVSXGeometricSegmentation],
) -> Snapshot:
    builder = create_builder()

    for volume in volumes:
        add_volume(builder, volume)
    for mesh in mesh_segmentations:
        add_mesh_segmentation(builder, mesh)
    for geometric in geometric_segmentations:
        add_geometric_segmentation(builder, geometric)

    snapshot = builder.get_snapshot()

    return snapshot


def get_segmentation_tooltip(segmentation: MVSXSegmentation) -> str:
    tooltip = ""
    segmentation_id = segmentation.segmentation_id
    segment_id = segmentation.segment_id
    tooltip += f"{segmentation_id} | Segment {segment_id}"
    for description in segmentation.descriptions:
        if description.name is not None:
            tooltip += "\n\n"
            tooltip += f"{description.name}"
        if not description.external_references:
            continue
        for reference in description.external_references:
            tooltip += "\n\n"
            tooltip += f"{reference.label} [{reference.resource}:{reference.accession}]"
    return tooltip


def add_volume(builder: Root, volume: MVSXVolume):
    volume_raw = builder.download(url=volume.destination_filepath)
    volume_cif = volume_raw.parse(format="bcif")
    volume_data = volume_cif.volume(channel_id=volume.channel_id)
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=volume.isovalue,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color=volume.color)
    volume_representation.opacity(opacity=0.2)
    return builder


def add_mesh_segmentation(builder: Root, segmentation: MVSXMeshSegmentation):
    builder.primitives(
        snapshot_key="",
        opacity=segmentation.opacity,
    ).mesh(
        color=segmentation.color,
        vertices=segmentation.vertices.ravel().tolist(),
        indices=segmentation.indices.ravel().tolist(),
        triangle_groups=segmentation.triangle_groups.ravel().tolist(),
        tooltip=get_segmentation_tooltip(segmentation),
    )
    return builder


def add_geometric_segmentation(builder: Root, segmentation: MVSXGeometricSegmentation):
    primitives = builder.primitives(
        snapshot_key="",
        opacity=segmentation.opacity,
    )
    if segmentation.kind == "sphere":
        primitives.sphere(
            color=segmentation.color,
            center=segmentation.center,
            radius=segmentation.radius,
            tooltip=segmentation.descriptions,
        )
    return builder


def convert_cvsx_to_mvsx(cvsx_path: str):
    cvsx_file: CVSXFile = load_cvsx_entry(cvsx_path)
    volumes: list[MVSXVolume] = get_list_of_all_volumes(cvsx_file)
    mesh_segmentations: list[MVSXMeshSegmentation] = [
        *get_list_of_all_mesh_segmentations(cvsx_file),
        *get_list_of_all_lattice_segmentations(cvsx_file),
    ]
    geometric_segmentations: list[MVSXGeometricSegmentation] = (
        get_list_of_all_geometric_segmentations(cvsx_file)
    )

    # print("volumes")
    # for volume in volumes:
    #     print(volume.get_fields_str())
    #     print()

    # print("mesh segmentations")
    # for segmentation in mesh_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # print("lattice segmentations")
    # for segmentation in lattice_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # print("geometric segmentations")
    # for segmentation in geometric_segmentations:
    #     print(segmentation.get_fields_str())
    #     print()

    # copy over data
    for volume in volumes:
        with ZipFile(cvsx_path, "r") as zip_ref:
            zip_ref.extract(volume.source_filepath, "temp/volumes")

    index_snapshot = create_index_snapshot(
        volumes,
        mesh_segmentations,
        geometric_segmentations,
    )
    states = States(
        metadata=GlobalMetadata(),
        snapshots=[index_snapshot],
    )

    with open("temp/mesh.mvsj", "w") as f:
        f.write(states.model_dump_json(indent=2, exclude_none=True))

    mvsj_to_mvsx(
        input_mvsj_path="temp/mesh.mvsj",
        output_mvsx_path="temp/mesh.mvsx",
    )


if __name__ == "__main__":
    convert_cvsx_to_mvsx("data/cvsx/zipped/emd-1832.cvsx")
