"""Utilities for printing and displaying model contents."""

from src.models.cvsx.cvsx_entry import CVSXEntry


def print_cvsx_entry(entry: CVSXEntry, indent: int = 0) -> None:
    """Print the contents of a CVSXEntry model in a formatted, readable way.

    Args:
        entry: The CVSXEntry instance to print
        indent: Initial indentation level (for nested calls)
    """
    ind = "  " * indent

    print(f"{ind}CVSXEntry:")
    print(f"{ind}  filepath: {entry.filepath}")

    # Print Index
    print(f"{ind}  index:")
    print(f"{ind}    query: {entry.index.query}")
    print(f"{ind}    metadata: {entry.index.metadata}")
    print(f"{ind}    annotations: {entry.index.annotations}")
    print(f"{ind}    volumes: {len(entry.index.volumes)} volume(s)")
    for vol_key, vol_info in entry.index.volumes.items():
        print(f"{ind}      {vol_key}:")
        print(f"{ind}        type: {vol_info.type}")
        print(f"{ind}        channelId: {vol_info.channelId}")
        print(f"{ind}        timeframeIndex: {vol_info.timeframeIndex}")

    if entry.index.meshSegmentations:
        print(f"{ind}    meshSegmentations: {len(entry.index.meshSegmentations)} segmentation(s)")
        for i, mesh_seg in enumerate(entry.index.meshSegmentations):
            print(f"{ind}      [{i}]:")
            print(f"{ind}        type: {mesh_seg.type}")
            print(f"{ind}        segmentationId: {mesh_seg.segmentationId}")
            print(f"{ind}        timeframeIndex: {mesh_seg.timeframeIndex}")
            print(f"{ind}        segmentsFilenames: {len(mesh_seg.segmentsFilenames)} file(s)")
            for j, filename in enumerate(mesh_seg.segmentsFilenames):
                print(f"{ind}          [{j}] {filename}")

    if entry.index.latticeSegmentations:
        print(f"{ind}    latticeSegmentations: {len(entry.index.latticeSegmentations)} segmentation(s)")
        for lat_key, lat_seg in entry.index.latticeSegmentations.items():
            print(f"{ind}      {lat_key}:")
            print(f"{ind}        type: {lat_seg.type}")
            print(f"{ind}        segmentationId: {lat_seg.segmentationId}")
            print(f"{ind}        timeframeIndex: {lat_seg.timeframeIndex}")

    if entry.index.geometricSegmentations:
        print(f"{ind}    geometricSegmentations: {len(entry.index.geometricSegmentations)} segmentation(s)")
        for geo_key, geo_seg in entry.index.geometricSegmentations.items():
            print(f"{ind}      {geo_key}:")
            print(f"{ind}        type: {geo_seg.type}")
            print(f"{ind}        segmentationId: {geo_seg.segmentationId}")
            print(f"{ind}        timeframeIndex: {geo_seg.timeframeIndex}")

    # Print Annotations
    print(f"{ind}  annotations:")
    print(f"{ind}    name: {entry.annotations.name}")
    print(f"{ind}    entry_id: {entry.annotations.entry_id}")
    print(f"{ind}    descriptions: {len(entry.annotations.descriptions)} description(s)")
    for desc_key in entry.annotations.descriptions.keys():
        print(f"{ind}      {desc_key}")
    print(f"{ind}    segment_annotations: {len(entry.annotations.segment_annotations)} annotation(s)")
    for seg_ann in entry.annotations.segment_annotations:
        print(f"{ind}      segment_id={seg_ann.segment_id}, kind={seg_ann.segment_kind}, segmentation_id={seg_ann.segmentation_id}")
    if entry.annotations.details:
        print(f"{ind}    details: {entry.annotations.details[:50]}..." if len(entry.annotations.details) > 50 else f"{ind}    details: {entry.annotations.details}")
    if entry.annotations.volume_channels_annotations:
        print(f"{ind}    volume_channels_annotations: {len(entry.annotations.volume_channels_annotations)} channel(s)")

    # Print Metadata
    print(f"{ind}  metadata:")
    print(f"{ind}    entry_id: {entry.metadata.entry_id}")
    print(f"{ind}    volumes:")
    print(f"{ind}      channel_ids: {entry.metadata.volumes.channel_ids}")
    print(f"{ind}      time_info: kind={entry.metadata.volumes.time_info.kind}, start={entry.metadata.volumes.time_info.start}, end={entry.metadata.volumes.time_info.end}")

    if entry.metadata.segmentation_lattices:
        print(f"{ind}    segmentation_lattices:")
        print(f"{ind}      segmentation_ids: {entry.metadata.segmentation_lattices.segmentation_ids}")

    if entry.metadata.segmentation_meshes:
        print(f"{ind}    segmentation_meshes:")
        print(f"{ind}      segmentation_ids: {entry.metadata.segmentation_meshes.segmentation_ids}")

    if entry.metadata.geometric_segmentation:
        print(f"{ind}    geometric_segmentation:")
        print(f"{ind}      segmentation_ids: {entry.metadata.geometric_segmentation.segmentation_ids}")

    if entry.metadata.entry_metadata:
        print(f"{ind}    entry_metadata:")
        if entry.metadata.entry_metadata.description:
            desc = entry.metadata.entry_metadata.description
            print(f"{ind}      description: {desc[:50]}..." if len(desc) > 50 else f"{ind}      description: {desc}")
        if entry.metadata.entry_metadata.url:
            print(f"{ind}      url: {entry.metadata.entry_metadata.url}")

    # Print Query
    print(f"{ind}  query:")
    print(f"{ind}    entry_id: {entry.query.entry_id}")
    print(f"{ind}    source_db: {entry.query.source_db}")
    if entry.query.segmentation_kind:
        print(f"{ind}    segmentation_kind: {entry.query.segmentation_kind}")
    if entry.query.time is not None:
        print(f"{ind}    time: {entry.query.time}")
    if entry.query.channel_id:
        print(f"{ind}    channel_id: {entry.query.channel_id}")
    if entry.query.segmentation_id:
        print(f"{ind}    segmentation_id: {entry.query.segmentation_id}")
    if entry.query.detail_lvl is not None:
        print(f"{ind}    detail_lvl: {entry.query.detail_lvl}")
    if entry.query.max_points is not None:
        print(f"{ind}    max_points: {entry.query.max_points}")
