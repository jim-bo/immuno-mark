import argparse
import pickle
from pickle import UnpicklingError
import os
import sys
import math

from immunomark import viz

def _load_images(args):
    """ load these images """

    # argument sanity check
    assert os.path.isfile(args.img_path)

    # open the h5 and extract the channels
    try:
        with open(args.img_path, 'rb') as fin:
            img_set = pickle.load(fin)
    except UnpicklingError:
        print("Bad file, call Jimbo")
        sys.exit(1)

    return img_set


def list_cases(args):
    """ list cases in the provided pickle """

    # load images
    img_set = _load_images(args)

    print("==")
    print()
    print("already processed?\ttps\tcommand to view")
    print()

    # print the keys
    for case_id in img_set.keys():

        # check if its processed
        key_set = img_set[case_id].keys()
        processed = "no"
        if 'all_cells' in key_set:
            processed = "yes"

        # compute tps if processed
        tps = "na"
        if processed == 'yes':
            all_cells = img_set[case_id]['all_cells'].shape[0]
            tumor_cells = img_set[case_id]['tumor_cells'].shape[0]
            tumorpos_cells = img_set[case_id]['tumor_pdl1pos'].shape[0]
            tps = float(tumorpos_cells) / float(tumor_cells)
            tps = '%.1f' % (tps * 100)
        

        print(f"{processed}\t: {tps}%\t: immunomark view {args.img_path} {case_id}")


def view_case(args):

    # load images
    img_set = _load_images(args)

    try:
        img_set[args.case_id]
    except KeyError:
        print(f"{args.case_id} is not a valid case in this project!")
        print()
        list_cases(args)

    # run the visualization (returns viewer object)
    viewer = viz.viz_img(img_set, args.case_id)

    # record the results into dictionary
    viz.record_points(viewer, img_set, args.case_id)

    # over-write the results
    with open(args.img_path, 'wb') as fout:
        pickle.dump(img_set, fout)

def main():

    # main parser
    parser = argparse.ArgumentParser(description='Immunoviz')

    # training mode
    mode_parser = parser.add_subparsers(dest="mode", help='Types of operations')
    mode_parser.required = True
    list_parser = mode_parser.add_parser("list")
    view_parser = mode_parser.add_parser("view")

    # training arguments
    list_parser.set_defaults(func=list_cases)
    list_parser.add_argument("img_path", help="Path to the file containing the imaging data", type=str)
    
    # test arguments
    view_parser.set_defaults(func=view_case)
    view_parser.add_argument("img_path", help="Path to the file containing the imaging data", type=str)
    view_parser.add_argument("case_id", help="Id of the case to visualize and annotate", type=str)

    # call the function with args
    args = parser.parse_args()
    args.func(args)

# setup the parser
if __name__ == "__main__":
    main()
    