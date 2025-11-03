"""Generalized MVSX file generator."""

import os
from pathlib import Path

import numpy as np
from molviewspec import create_builder
from molviewspec.builder import Root
from molviewspec.mvsx_converter import mvsj_to_mvsx
from skimage import measure

from lib.convert.lattice_segmentation import (
    bcif_to_lattice_segmentation_cif,
    get_lattice_segment,
    read_bcif_file,
)
from lib.models.cif.lattice_segmentation import LatticeSegmentationCIF
from lib.models.config.mvsx_config import MVSXGeneratorConfig, SegmentationConfig
from lib.utils.transforms import compute_voxel_to_world_transform, matrix_to_flat_list


class MVSXGenerator:
    """Generates MVSX files from CVSX data with configurable parameters."""

    def __init__(self, config: MVSXGeneratorConfig):
        """Initialize the generator with configuration.

        Args:
            config: Configuration for MVSX generation
        """
        self.config = config
        self.builder: Root | None = None

    def generate(self) -> None:
        """Generate MVSX file from configuration."""
        # Ensure temp directory exists
        self.config.temp_dir.mkdir(parents=True, exist_ok=True)

        # Create builder
        self.builder = create_builder()

        # Add volume if configured
        if self.config.volume:
            self._add_volume()

        # Process segmentations
        segmentations = self._get_segmentations()
        for segmentation in segmentations:
            self._add_segmentation(segmentation)

        # Export to MVSJ
        state = self.builder.get_state()
        mvsj_content = state.model_dump_json(exclude_none=True)

        # Save intermediate MVSJ if requested
        if self.config.mvsj_output_path:
            with open(self.config.mvsj_output_path, "w") as f:
                f.write(mvsj_content)
        else:
            # Use temporary file
            temp_mvsj = self.config.temp_dir / "temp.mvsj"
            with open(temp_mvsj, "w") as f:
                f.write(mvsj_content)

        # Convert to MVSX
        mvsj_path = self.config.mvsj_output_path or temp_mvsj
        mvsj_to_mvsx(
            input_mvsj_path=str(mvsj_path),
            output_mvsx_path=str(self.config.mvsx_output_path),
        )

        # Clean up temporary MVSJ if not requested
        if not self.config.mvsj_output_path and temp_mvsj.exists():
            temp_mvsj.unlink()

    def _get_segmentations(self) -> list[SegmentationConfig]:
        """Get list of segmentations to process.

        If config.segmentations is empty, will attempt to auto-discover from CVSX.
        For now, returns the configured list.

        Returns:
            List of segmentation configurations
        """
        if self.config.segmentations:
            return self.config.segmentations

        # TODO: Implement auto-discovery by inspecting CVSX zip contents
        return []

    def _add_volume(self) -> None:
        """Add volume visualization to the builder."""
        if not self.config.volume:
            return

        volume_config = self.config.volume
        volume_cif = self.builder.download(url=volume_config.url).parse(format="bcif")
        volume_data = volume_cif.volume(channel_id=volume_config.channel_id)
        volume_representation = volume_data.representation(
            type="isosurface",
            relative_isovalue=volume_config.relative_isovalue,
            show_faces=volume_config.show_faces,
            show_wireframe=volume_config.show_wireframe,
        )
        volume_representation.color(color=volume_config.color).opacity(
            opacity=volume_config.opacity
        )

    def _add_segmentation(self, segmentation: SegmentationConfig) -> None:
        """Add segmentation meshes to the builder.

        Args:
            segmentation: Segmentation configuration
        """
        # Determine inner path
        inner_path = segmentation.inner_path
        if inner_path is None:
            inner_path = f"lattice_{segmentation.segmentation_id}_0.bcif"

        # Read BCIF data
        data = read_bcif_file(
            zip_path=str(self.config.cvsx_input_path),
            inner_path=inner_path,
        )
        lattice_model = bcif_to_lattice_segmentation_cif(data, "0")

        # Process each segment
        segment_ids = (
            lattice_model.segmentation_block.segmentation_data_table.segment_id
        )
        for segment_id in set(segment_ids):
            if segment_id == 0:
                continue

            self._add_segment(
                lattice_model=lattice_model,
                segmentation_id=segmentation.segmentation_id,
                segment_id=segment_id,
            )

    def _add_segment(
        self,
        lattice_model: LatticeSegmentationCIF,
        segmentation_id: str,
        segment_id: int,
    ) -> None:
        """Add a single segment mesh to the builder.

        Args:
            lattice_model: Lattice segmentation model
            segmentation_id: ID of the segmentation
            segment_id: ID of the segment
        """
        # Get segment with smoothing
        model = get_lattice_segment(
            lattice_model.model_copy(deep=True),
            segment_id,
            f"{segment_id}",
            smooth_iterations=self.config.mesh_config.smooth_iterations,
        )

        # Generate mesh from voxels
        vertices, indices, triangle_groups = self._voxel_to_mesh(model)

        # Compute transformation matrix
        info = model.segmentation_block.volume_data_3d_info
        voxel_size = np.array(
            [
                info.spacegroup_cell_size_0 / info.sample_count_0,
                info.spacegroup_cell_size_1 / info.sample_count_1,
                info.spacegroup_cell_size_2 / info.sample_count_2,
            ]
        )
        origin = np.array([info.origin_0, info.origin_1, info.origin_2])

        transform_matrix = compute_voxel_to_world_transform(
            origin=origin,
            voxel_size=voxel_size,
            origin_offset=self.config.mesh_config.origin_offset,
        )
        matrix = matrix_to_flat_list(transform_matrix)

        # Get segment color
        color = self.config.get_segment_color(segmentation_id, segment_id)

        # Add to builder
        self.builder.primitives(instances=[matrix]).mesh(
            vertices=vertices.tolist(),
            indices=indices.tolist(),
            triangle_groups=triangle_groups.tolist(),
            color=color,
            tooltip=f"{segment_id}",
        )

    def _voxel_to_mesh(
        self, lattice_cif: LatticeSegmentationCIF
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert voxel data to mesh using marching cubes.

        Args:
            lattice_cif: Lattice segmentation CIF model

        Returns:
            Tuple of (vertices, indices, triangle_groups)
        """
        values = lattice_cif.segmentation_block.segmentation_data_3d.values
        info = lattice_cif.segmentation_block.volume_data_3d_info

        nx, ny, nz = (
            int(info.sample_count_0),
            int(info.sample_count_1),
            int(info.sample_count_2),
        )

        # Reshape and transpose to correct orientation
        data = values.reshape((nz, ny, nx)).transpose((2, 1, 0))

        # Apply marching cubes
        verts, faces, normals, values = measure.marching_cubes(
            data,
            level=self.config.mesh_config.marching_cubes_level,
            method=self.config.mesh_config.marching_cubes_method,
        )

        # Reverse face winding order
        faces = faces[:, ::-1]

        # Flatten arrays
        vertices = verts.ravel()
        indices = faces.ravel()
        triangle_groups = np.zeros(len(faces))

        return vertices, indices, triangle_groups


def generate_mvsx_from_config(config: MVSXGeneratorConfig) -> None:
    """Convenience function to generate MVSX from configuration.

    Args:
        config: Configuration for MVSX generation
    """
    generator = MVSXGenerator(config)
    generator.generate()


def generate_mvsx_from_config_file(config_path: Path) -> None:
    """Generate MVSX from a configuration file.

    Args:
        config_path: Path to JSON or YAML configuration file
    """
    if config_path.suffix.lower() in [".yaml", ".yml"]:
        config = MVSXGeneratorConfig.from_yaml_file(config_path)
    elif config_path.suffix.lower() == ".json":
        config = MVSXGeneratorConfig.from_json_file(config_path)
    else:
        raise ValueError(f"Unsupported config file format: {config_path.suffix}")

    generate_mvsx_from_config(config)
