from pathlib import Path

from molviewspec import create_builder
from molviewspec.nodes import GlobalMetadata, States

from src.io.cvsx_reader.loader import load_cvsx_entry
from src.io.mvsx_writer.volumes import mvsj_add_volume
from src.models.intermediary.inter import InterEntryInfo
from src.models.mvsx.mvsx_entry import MVSXEntry, MVSXSnapshot
from src.models.mvsx.mvsx_volume import MVSXVolume


def extract_name(filepath):
    path = Path(filepath)
    name_only = path.stem
    return name_only


cvsx_filepath = "data/cvsx/zipped/custom-tubhiswt.cvsx"

# original
cvsx_entry = load_cvsx_entry(cvsx_filepath)

print(len(cvsx_entry.index.volumes))

exit(0)

# intermediate model
grouped = InterEntryInfo.from_cvsx_index(cvsx_entry)

# final model
snapshots = []

for timeframe in grouped.timeframes:
    volume_models = []
    for volume in timeframe.volumes:
        # TODO check that volume.timeframeIndex == timeframe.index
        volume_model = MVSXVolume(
            source_filepath=volume.filepath,
            destination_filepath=f"volumes/{volume}",
            channel_id=volume.channelId,
            format="bcif",  # TODO: check this
        )
    snapshot = MVSXSnapshot(volumes=volume_models)
    snapshots.append(snapshot)

mvsx_entry = MVSXEntry(snapshots=snapshots)

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
