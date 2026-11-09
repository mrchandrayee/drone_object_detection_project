def denormalize_polygon(points, width, height):
    return [(int(float(x)*width), int(float(y)*height)) for x,y in points]
def point_in_polygon(point, polygon):
    if not polygon: return False
    x,y=point; inside=False; j=len(polygon)-1
    for i in range(len(polygon)):
        xi,yi=polygon[i]; xj,yj=polygon[j]
        if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/(yj-yi+1e-9)+xi: inside=not inside
        j=i
    return inside
def box_anchor(box, anchor="bottom"):
    x1,y1,x2,y2=box
    if anchor=="center": return ((x1+x2)//2,(y1+y2)//2)
    if anchor=="top": return ((x1+x2)//2,y1)
    return ((x1+x2)//2,y2)
