from molviewspec import create_builder
from molviewspec.builder import Root

from src.utils.utils import rgba_to_hex


def emd_1832_volume(builder: Root):
    volume_cif = builder.download(
        url="./volume_0_0.bcif"
    ).parse(format="bcif")
    volume_data = volume_cif.volume()
    volume_representation = volume_data.representation(
        type="isosurface",
        relative_isovalue=2.73,
        show_faces=True,
        show_wireframe=False,
    )
    volume_representation.color(color="white").opacity(opacity=0.4)

    return builder


def emd_1832_lattices(builder: Root):
    segment_ids = [
        {
            "color": [0.521576881408691, 0.889867722988129, 0.848475754261017, 1.0],
            "id": "847fefd0-ebe2-4768-936f-de91e7b5cd00",
            "segment_id": 85,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
        {
            "color": [0.504164099693298, 0.644178092479706, 0.78633439540863, 1.0],
            "id": "c9577740-341d-4766-90a6-db9588fd0c24",
            "segment_id": 93,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
        {
            "color": [0.669882595539093, 0.86139714717865, 0.948218941688538, 1.0],
            "id": "35a55e35-b02b-4379-a4b2-f87d4fd7ac3b",
            "segment_id": 97,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
        {
            "color": [0.862361133098602, 0.965298295021057, 0.697644174098969, 1.0],
            "id": "482fd7d9-6ec7-45e3-94f1-17ac3481249f",
            "segment_id": 101,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
        {
            "color": [0.706890761852264, 0.626759827136993, 0.604495763778687, 1.0],
            "id": "07013de2-b1dc-40c0-b237-1c3b57fe7cb6",
            "segment_id": 103,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
        {
            "color": [0.787909328937531, 0.924791157245636, 0.951091408729553, 1.0],
            "id": "75f236b1-798c-4a43-b796-47018a62344e",
            "segment_id": 104,
            "segment_kind": "lattice",
            "segmentation_id": "0",
            "time": 0,
        },
    ]
    for segment_id in segment_ids:
        volume_cif = builder.download(
            url=f"./{segment_id['segment_id']}.cif"
        ).parse(format="mmcif")
        volume_data = volume_cif.volume()
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=2.73,
            show_wireframe=False,
            show_faces=True,
        )
        color = rgba_to_hex(*segment_id["color"])
        volume_representation.color(color=color).opacity(opacity=1)

    return builder


def emd_1832() -> Root:
    builder: Root = create_builder()

    emd_1832_volume(builder)
    emd_1832_lattices(builder)

    print(builder.get_state())

    return builder
