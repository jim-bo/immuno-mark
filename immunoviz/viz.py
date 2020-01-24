# import
from vispy.color import Colormap, ColorArray
import numpy as np
import napari

# make the colormaps
COLORS = [
    [228, 26, 28],
    [55, 126, 184],
    [77, 175, 74],
    [152, 78, 163],
    [255, 127, 0],
    [255, 255, 51],
    [255, 255, 255]
]
CMAPS = []
for r, g, b in COLORS:
    
    # set up colors
    color = ((r / 256), (g / 256), (b / 256))
    
    # make the map
    cmap = Colormap(ColorArray([[0, 0, 0], color]))
    
    CMAPS.append(cmap)
        
CMAP_NAMES = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "yellow",
    "white"
]

def viz_img(img_set, key_base):

    # setup data for this case
    channels = img_set[key_base]['img']
    cell_df = img_set[key_base]['cell_df']

    # do we have existing points?
    def fetch_points(key, case):
        """ helper to fetch existing cells"""
        cells = np.array([[0, 0]])
        if key in case:
            cells = case[key]
        return cells
        
    other_cells = fetch_points("other_cells", img_set[key_base])
    tumor_pdl1pos = fetch_points("tumor_pdl1pos", img_set[key_base])
    tumor_pdl1neg = fetch_points("tumor_pdl1neg", img_set[key_base])

    # compute the points
    points = np.array(list(cell_df.apply(lambda x: (x['x'], x['y']), axis=1)))
    
    # open napari
    with napari.gui_qt():

        # make image
        viewer = napari.Viewer()

        # loop over each channel
        for channel, cmap, cname in zip(channels, CMAPS, CMAP_NAMES):

            # parameters.
            visible = False  
            cmap = (cname, cmap)

            # customize.
            if channel == "DAPI":

                # make dapi only visible
                visible = True

                # switch to turbo
                cmap = "turbo"

            # add the layer
            layer = viewer.add_image(channels[channel], name=channel, colormap=cmap, 
                                     visible=visible, blending='additive')
            
        # add the know points.
        inform_layer = viewer.add_points(points, name="InForm cells", size=3, face_color="yellow")
        inform_layer.editable = False
        inform_layer.visible = False
        
        # add empty layer
        inform_layer = viewer.add_points(other_cells, 
                                         name="Other cells", size=3, face_color="white")
        inform_layer = viewer.add_points(tumor_pdl1pos, 
                                         name="Tumor PDL1+ cell", size=3, face_color="green")
        inform_layer = viewer.add_points(tumor_pdl1neg, 
                                         name="Tumor PDL1- cell", size=3, face_color="red")

    return viewer

def record_points(viewer, img_set, key_base):

    # loop over each layer
    for layer in viewer.layers:
        
        def save_layer(layer_name, layer, img_set, key_base):

            # strip off the dummy point.
            start_idx = 0
            if layer.data[0, 0] == 0 and layer.data[0, 1] == 0:
                start_idx = 1
                
            points = layer.data[start_idx:, :]

            # save the points.
            img_set[key_base][layer_name] = points
            
        if layer.name == "Tumor PDL1- cell":
            save_layer("tumor_pdl1neg", layer, img_set, key_base)

        elif layer.name == "Tumor PDL1+ cell":
            save_layer("tumor_pdl1pos", layer, img_set, key_base)
            
        elif layer.name == "Other cells":
            save_layer("other_cells", layer, img_set, key_base)
            