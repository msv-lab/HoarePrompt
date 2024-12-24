def polygon_area(points):
  
    if len(points) < 3:
        return 0.0  #

    shoelace_sum = 0
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        shoelace_sum += x1 * y2 - y1 * x2

    area = abs(shoelace_sum) / 2.0
    return area
