from app import App
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="traffic_analyzer")
    parser.add_argument('--window_title', type=str, default="Tkinter and OpenCV",
                        help='Title of the application window')
    parser.add_argument('--config_path', type=str, default='config.yml',
                        help='Path to the configuration file')
    parser.add_argument('--is_simulation', type=bool, default=False,
                        help='Flag to run in simulation mode')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Create a window and pass it to the Application object
    application = App(
        config_path=args.config_path,
        is_simulation=args.is_simulation,
        window_title=args.window_title,
    )
