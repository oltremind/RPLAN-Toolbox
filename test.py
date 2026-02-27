import os
import sys 
import random
import logging
import datetime
import matplotlib.pyplot as plt

from absl import app, flags

from rplan.floorplan import Floorplan
from rplan.align import align_fp_gt
from rplan.decorate import get_dw
from rplan.measure import compute_tf
from rplan.plot import get_figure,get_axes,plot_category,plot_boundary,plot_graph,plot_fp,plot_tf

# Define flags
FLAGS = flags.FLAGS

flags.DEFINE_string(
    "data_path",
    default=os.path.join(
            os.getcwd(), "data"
    ),
    help="Path to the input data.",
)

flags.DEFINE_string(
    "save_path",
    default=None,
    help="Path to save the output.",
)

def main(argv):

    # Determine save path
    current_dir_name = "rplan"

    if FLAGS.save_path:
        save_path = FLAGS.save_path
    else:
        current_datetime = datetime.datetime.now().strftime('%y%m%d_%H%M')
        save_path = os.path.join(
            os.getcwd(),
            f"logs/{current_dir_name}/test_{current_datetime}"
        )
    os.makedirs(save_path, exist_ok=True)

    # Configure logging
    logging.root.name = current_dir_name
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)-3s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(os.path.join(save_path, "test.log"), mode='w'),
            logging.StreamHandler()
        ],
        force=True
    )

    # Process the floorplan data
    data_path = FLAGS.data_path
    if not os.path.exists(data_path):
        logging.error(f"Data path does not exist: {data_path}")
        sys.exit(1)

    logging.info(f"Using data path: {data_path}")

    # Check number of files in the data path
    num_files = len(os.listdir(data_path))
    logging.info(f"Number of files in data path: {num_files}")

    # Select an image file from the data path
    image_files = [f for f in os.listdir(data_path) if f.endswith('.png')]
    if not image_files:
        logging.error(f"No image files found in data path: {data_path}")
        sys.exit(1)

    # Randomly select an image file for processing
    image_file = random.choice(image_files)
    file_path = os.path.join(data_path, image_file)
    logging.info(f"Processing file: {file_path}")

    # Image name without extension
    image_name = os.path.splitext(image_file)[0]

    fp = Floorplan(file_path)
    data = fp.to_dict()

    boxes_aligned, order, room_boundaries = align_fp_gt(data['boundary'],data['boxes'],data['types'],data['edges'])
    data['boxes_aligned'] = boxes_aligned
    data['order'] = order
    data['room_boundaries'] = room_boundaries

    doors,windows = get_dw(data)
    data['doors'] = doors
    data['windows'] = windows

    fig = get_figure([512,512])
    plot_boundary(data['boundary'],ax=get_axes(fig=fig,rect=[0,0.5,0.5,0.5]))
    ax = plot_category(fp.category,ax=get_axes(fig=fig,rect=[0.5,0.5,0.5,0.5]))
    plot_graph(data['boundary'],data['boxes'],data['types'],data['edges'],ax=ax)
    plot_fp(data['boundary'], data['boxes_aligned'][order], data['types'][order],ax=get_axes(fig=fig,rect=[0,0,0.5,0.5]))
    plot_fp(data['boundary'], data['boxes_aligned'][order], data['types'][order],data['doors'],data['windows'],ax=get_axes(fig=fig,rect=[0.5,0,0.5,0.5]))
    fig.canvas.draw()
    fig.canvas.print_figure(os.path.join(save_path, f"{image_name}_floorplan.png"), dpi=300, bbox_inches='tight')
    plt.figure(constrained_layout=True)
    x, y = compute_tf(data['boundary'])
    plot_tf(x, y)
    plt.savefig(os.path.join(save_path, f"{image_name}_tf.png"), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    app.run(main)
