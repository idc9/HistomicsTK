import json
import logging
import os

import large_image

import histomicstk.preprocessing.color_deconvolution as htk_cd
from histomicstk.cli import utils
from histomicstk.cli.utils import CLIArgumentParser

logging.basicConfig()


def main(args):
    import skimage.io

    # Read Input Image
    print('>> Reading input image')

    print(args.inputImageFile)

    ts = large_image.getTileSource(args.inputImageFile)

    im_input = ts.getRegion(
        format=large_image.tilesource.TILE_FORMAT_NUMPY,
        **utils.get_region_dict(args.region, args.maxRegionSize, ts)
    )[0]

    # Create stain matrix
    print('>> Creating stain matrix')

    w = utils.get_stain_matrix(args)
    print(w)

    # Perform color deconvolution
    print('>> Performing color deconvolution')
    im_stains = htk_cd.color_deconvolution(im_input, w).Stains

    # write stain images to output
    print('>> Outputting individual stain images')

    print(args.outputStainImageFile_1)
    skimage.io.imsave(args.outputStainImageFile_1, im_stains[:, :, 0])

    print(args.outputStainImageFile_2)
    skimage.io.imsave(args.outputStainImageFile_2, im_stains[:, :, 1])

    print(args.outputStainImageFile_3)
    skimage.io.imsave(args.outputStainImageFile_3, im_stains[:, :, 2])

    if args.outputAnnotationFile:
        region = utils.get_region_dict(args.region, args.maxRegionSize, ts)['region']
        annotation = [{
            'name': 'Deconvolution %s - %s' % (
                args.stain_1 if args.stain_1 != 'custom' else str(args.stain_1_vector),
                os.path.splitext(os.path.basename(args.outputAnnotationFile))[0]),
            'description': 'Used params %r' % vars(args),
            'elements': [{
                'type': 'image',
                'girderId': 'outputStainImageFile_1',
                'transform': {
                    'xoffset': region.get('left', 0),
                    'yoffset': region.get('top', 0),
                },
            }],
        }, {
            'name': 'Deconvolution %s - %s' % (
                args.stain_2 if args.stain_2 != 'custom' else str(args.stain_2_vector),
                os.path.splitext(os.path.basename(args.outputAnnotationFile))[0]),
            'description': 'Used params %r' % vars(args),
            'elements': [{
                'type': 'image',
                'girderId': 'outputStainImageFile_2',
                'transform': {
                    'xoffset': region.get('left', 0),
                    'yoffset': region.get('top', 0),
                },
            }],
        }, {
            'name': 'Deconvolution %s - %s' % (
                args.stain_3 if args.stain_3 != 'custom' else str(args.stain_3_vector),
                os.path.splitext(os.path.basename(args.outputAnnotationFile))[0]),
            'description': 'Used params %r' % vars(args),
            'elements': [{
                'type': 'image',
                'girderId': 'outputStainImageFile_3',
                'transform': {
                    'xoffset': region.get('left', 0),
                    'yoffset': region.get('top', 0),
                },
            }],
        }]
        if args.stain_3 == 'null':
            annotation[2:] = []
        if args.stain_2 == 'null':
            annotation[1:2] = []

        with open(args.outputAnnotationFile, 'w') as annotation_file:
            json.dump(annotation, annotation_file, indent=2, sort_keys=False)


if __name__ == "__main__":
    main(CLIArgumentParser().parse_args())
