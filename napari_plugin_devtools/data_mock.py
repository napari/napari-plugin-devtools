import numpy as np
import pytest
from napari.components import ViewerModel


@pytest.fixture
def mock_data_factory():
    class MockDataFactory(object):
        def __init__(self):
            self.viewer_model = ViewerModel()
            self.default_dimension = (512, 512)

        def set_dimension(self, dimension):
            self.default_dimension = dimension

        def mock_image(self, data=None, dimensions=None, **kwargs):
            if data is not None:
                return self.viewer_model.add_image(data, **kwargs)
            if dimensions is None:
                dimensions = self.default_dimension
            data = np.random.randint(
                low=0, high=256, size=dimensions.append(3)
            )
            return self.viewer_model.add_image(data, rgb=True, **kwargs)

        def mock_labels(
            self, data=None, num_labels=256, dimensions=None, **kwargs
        ):
            if data is not None:
                return self.viewer_model.add_labels(data, **kwargs)
            if dimensions is None:
                dimensions = self.default_dimension
            data = np.random.randint(low=0, high=num_labels, size=dimensions)
            return self.viewer_model.add_labels(data, **kwargs)

        def mock_points(
            self, data=None, num_points=10, dimensions=None, **kwargs
        ):
            if data is not None:
                return self.viewer_model.add_points(data, **kwargs)
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
            return self.viewer_model.add_points(data, **kwargs)

        def mock_shapes(
            self,
            data=None,
            num_shapes=10,
            max_points=20,
            dimensions=None,
            **kwargs,
        ):
            if data is not None:
                return self.viewer_model.add_shapes(data, **kwargs)
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

            return self.viewer_model.add_shapes(
                data, shape_type=shapes, **kwargs
            )

        def mock_surfaces(
            self, data=None, num_surfaces=10, dimensions=None, **kwargs
        ):
            if data is not None:
                return self.viewer_model.add_surfaces(data, **kwargs)
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
            return self.viewer_model.add_surface(data, **kwargs)

        def mock_tracks(
            self,
            data=None,
            num_tracks=10,
            max_time=10,
            dimensions=None,
            **kwargs,
        ):
            if data is not None:
                return self.viewer_model.add_tracks(data, **kwargs)
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
            return self.viewer_model.add_tracks(data, **kwargs)

        def mock_vectors(
            self, data=None, num_vectors=10, dimensions=None, **kwargs
        ):
            if data is not None:
                return self.viewer_model.add_vectors(data, **kwargs)
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
            return self.viewer_model.add_vectors(data, **kwargs)

    return MockDataFactory()
