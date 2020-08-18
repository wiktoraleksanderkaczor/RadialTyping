import math

#https://stackoverflow.com/questions/23411688/drawing-polygon-with-n-number-of-sides-in-python-3-2

def polygon(sides, radius=1, rotation=0, translation=None):
    one_segment = math.pi * 2 / sides

    points = [(math.sin(one_segment * i + rotation) * radius, 
                math.cos(one_segment * i + rotation) * radius) 
                for i in range(sides)]

    if translation:
        points = [[sum(pair) for pair in zip(point, translation)] for point in points]

    return points

if __name__ == "__main__":
    points = polygon(5)
    print(points[0][0])