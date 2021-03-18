import numpy as np
from napari.layers.image.image import Image
from napari.layers.labels.labels import Labels
from napari.layers.points.points import Points
from napari.layers.shapes.shapes import Shapes
from napari.layers.surface.surface import Surface
from napari.layers.tracks.tracks import Tracks
from napari.layers.vectors.vectors import Vectors


class LayerFactory(object):
    def __init__(self, dimension=None):
        if dimension is None:
            dimension = (512, 512)
        self.default_dimension = dimension

    def set_dimension(self, dimension):
        self.default_dimension = dimension

    def create_image_layer(self, data=None, dimensions=None, **kwargs):
        if data is not None:
            return Image(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension
        data = np.random.randint(low=0, high=256, size=dimensions + (3,))
        return Image(data, rgb=True, **kwargs)

    def create_label_layer(
        self, data=None, num_labels=256, dimensions=None, **kwargs
    ):
        if data is not None:
            return Labels(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension
        data = np.random.randint(low=0, high=num_labels, size=dimensions)
        return Labels(data, **kwargs)

    def create_point_layer(
        self, data=None, num_points=10, dimensions=None, **kwargs
    ):
        if data is not None:
            return Points(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension
        data = np.array(
            [
                [
                    np.random.randint(low=0, high=dimension)
                    for dimension in dimensions
                ]
                for _ in range(num_points)
            ]
        )
        return Points(data, **kwargs)

    def create_shape_layer(
        self,
        data=None,
        num_shapes=10,
        max_points=20,
        dimensions=None,
        **kwargs,
    ):
        if data is not None:
            return Shapes(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension

        shape_types = {
            'line': (2, 2),
            'rectangle': (4, 4),
            'ellipse': (4, 4),
            'path': (2, max_points),
            'polygon': (2, max_points),
        }
        shapes = np.random.choice(list(shape_types.keys()), num_shapes)
        data = np.array(
            [
                [
                    [
                        np.random.randint(low=0, high=dimension)
                        for dimension in dimensions
                    ]
                    for _ in range(
                        np.random.randint(
                            low=shape_types[shape][0],
                            high=shape_types[shape][1] + 1,
                        )
                    )
                ]
                for shape in shapes
            ]
        )

        return Shapes(data, shape_type=shapes, **kwargs)

    def create_surface_layer(
        self, data=None, num_surfaces=10, dimensions=None, **kwargs
    ):
        if data is not None:
            return Surface(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension
        data = (
            np.array(
                [
                    [
                        np.random.randint(low=0, high=dimension)
                        for dimension in dimensions
                    ]
                    for _ in range(num_surfaces)
                ]
            ),
            np.array(
                [
                    [np.random.randint(low=0, high=num_surfaces)]
                    for _ in range(num_surfaces)
                ]
            ),
            np.random.rand(num_surfaces),
        )
        return Surface(data, **kwargs)

    def create_track_layer(
        self,
        data=None,
        num_tracks=10,
        max_time=10,
        dimensions=None,
        **kwargs,
    ):
        if data is not None:
            return Tracks(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension

        data = []
        for i in range(num_tracks):
            for t in range(max_time):
                row = [i, t]
                row.extend(
                    [
                        np.random.randint(low=0, high=dimension)
                        for dimension in dimensions
                    ]
                )
                data.append(row)
        data = np.array(data)
        return Tracks(data, **kwargs)

    def create_vector_layer(
        self, data=None, num_vectors=10, dimensions=None, **kwargs
    ):
        if data is not None:
            return Vectors(data, **kwargs)
        if dimensions is None:
            dimensions = self.default_dimension
        data = np.array(
            [
                [
                    [
                        np.random.randint(low=0, high=dimension)
                        for dimension in dimensions
                    ]
                    for _ in range(2)
                ]
                for _ in range(num_vectors)
            ]
        )
        return Vectors(data, **kwargs)
