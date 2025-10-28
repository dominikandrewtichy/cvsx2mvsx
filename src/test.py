from typing import Literal

from molviewspec import create_builder
from molviewspec.nodes import GlobalMetadata, States

from src.io.cvsx_loader import load_cvsx_entry
from src.io.mvsj_builder import mvsj_add_volume
from src.models.intermediary.inter import InterEntryInfo
from src.models.mvsx.mvsx_entry import MVSXEntry, MVSXSnapshot
from src.models.mvsx.mvsx_volume import MVSXVolume


def get_volume_path(volume_file: str) -> str:
    return f"volumes/{volume_file}"


def get_segmentation_path(
    kind: Literal["lattice", "mesh", "geometric"],
    segmentation_file: str,
) -> str:
    return f"segmentations/{kind}/{segmentation_file}"


cvsx_filepath = "data/cvsx/zipped/custom-tubhiswt.cvsx"

# original
cvsx_entry = load_cvsx_entry(cvsx_filepath)


inter_entry = InterEntryInfo.from_cvsx_entry(cvsx_entry)

# final model
snapshots = []

# todo: convert to mvsx model which is used to generate the
for timeframe in inter_entry.timeframes:
    volume_models = []
    for volume in timeframe.volumes:
        volume_model = MVSXVolume(
            source_filepath=volume.filepath,
            destination_filepath=get_volume_path(volume.filepath),
            channel_id=volume.channelId,
            format="bcif",
        )
    snapshot = MVSXSnapshot(volumes=volume_models)
    snapshots.append(snapshot)
mvsx_entry = MVSXEntry(snapshots=snapshots)

# todo: convert and save volumes and segmentations into the archive

# todo: generate the multi mvsj file
snapshots = []
for snapshot in mvsx_entry.snapshots:
    builder = create_builder()
    for volume in snapshot.volumes:
        mvsj_add_volume(builder, volume)
    snap = builder.get_snapshot(
        title=snapshot.title,
        description=snapshot.description,
    )
    snapshots.append(snap)
states = States(snapshots=snapshots, metadata=GlobalMetadata())


print(states)
