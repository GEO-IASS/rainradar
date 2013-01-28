from PIL import Image
import math

class RainRadar(object):
    """
    Generic interface for querying rainfall radar images. You probably only
    want to use the nearest_rain method.
    """

    def distance(self, a, b):
        """
        Simple 2D euclidean distance.
        """
        return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))

    def nearest_rain(self, position, image_path):
        """
        Find the nearest rain to a given position (expressed in x,y pixels with
        0,0 being the top left corner of the image).

        Params:
        position   A 2-tuple, with the x,y coordinates of the location from
                   which you wish to calculate distances.
        image_path The path to the image with the rainfall radar data.

        Return:
        An array containing four elements which are the distances from
        'position' to the nearest rain in the quadrants around the position (in
        the order NW, SW, NE, SE).
        """
        # Cache
        rain_colours = self.rain_colours()

        # Get the pixels from the image
        image = Image.open(image_path)
        image = image.convert('RGB')
        pixels = image.load()

        # Is it raining at our position?
        if pixels[position] in rain_colours:
            return [0, 0, 0, 0]

        # Find the nearest rain in the NW,NE,SW,SE directions from 
        quadrants = {}
        for point in self.search_outwards(position, max(image.size)):
            if len(quadrants) >= 4:
                break
            try:
                if pixels[point] in rain_colours:
                    quadrant = (
                        cmp(point[0], position[0]),
                        cmp(point[1], position[1])
                    )
                    if quadrant not in quadrants:
                        quadrants[quadrant] = point
            except IndexError:
                pass

        # Sort the results and round the distances to the nearest pixel.
        # TODO: Concert pixel distances to km or minutes
        result = []
        for quadrant in sorted(quadrants):
            result.append(
                math.floor(self.distance(quadrants[quadrant], position))
            )
        return result

    def rain_colours(self):
        """
        The RGB colour values in the rainfall radar image which denote rain.
        """
        return ()

    def search_outwards(self, center, max_distance):
        """
        Iterator for searching in an increasing box around a given pixel.

        Parameters:
            center       The pixel to search around.
            max_distance The furthest deviation in the x,y plane from the
                         center point.

        Yields:
            A series of (x,y) coordinates progressing outwards from the center
            point.
        """
        for distance in range(1, max_distance + 1):
            (x_min, x_max) = (center[0] - distance, center[0] + distance)
            (y_min, y_max) = (center[1] - distance, center[1] + distance)

            x = x_min
            y = y_min
            while x <= x_max and y <= y_max:
                yield (x,y)
                if y in (y_min, y_max):
                    if x == x_max:
                        x = x_min
                        y += 1
                    else:
                        x += 1
                elif x == x_min:
                    x = x_max
                elif x == x_max:
                    x = x_min
                    y += 1

class MetEireannRainRadar(RainRadar):
    """
    See RainRadar for the details. This is for reading info from
    http://www.met.ie/latest/rainfall_radar.asp.
    """
    def rain_colours(self):
        """
        The colours which denote rain in Met Eireann's rainfall radar images.
        """
        return  (
                    (230, 227, 230), # 32 mm/hour
                    (188, 189, 188), # 24 mm/hour
                    (239, 0, 0),     # 16 mm/hour
                    (255, 153, 153), # 12 mm/hour
                    (255, 85, 255),  # 8 mm/hour
                    (132, 0, 132),   # 6 mm/hour
                    (255, 255, 140), # 4 mm/hour
                    (239, 243, 0),   # 3 mm/hour
                    (0, 211, 0),     # 2 mm/hour
                    (82, 243, 123),  # 1.5 mm/hour
                    (0, 254, 254),   # 1 mm/hour
                    (89, 169, 254),  # 0.5 mm/hour
                    (81, 72, 254),   # 0.25 mm/hour
                    (0, 0, 187),     # 0.1 mm/hour
                )
