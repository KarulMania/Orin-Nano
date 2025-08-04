import argparse


def parseArguments():
    parser = argparse.ArgumentParser(description='Video processing and data sending script.')
    parser.add_argument('--personCam', type=int, default=1, help='source for cam1; 1 for iptv on personcam ; 0 for videopath on personcam')
    parser.add_argument('--bicycleCam', type=int, default=1, help='source for cam2; 1 for iptv on bicyclecam ; 0 for videopath on bicyclecam')
    parser.add_argument('--reverse', type=int, default=0, help='1 for bicycleCounter on Personcam else 0')
    parser.add_argument('--personCamFps', type=int, default=0, help='Cam fps for personcam')
    parser.add_argument('--bicycleCamFps', type=int, default=0, help='Cam fps for backCam')

    args = parser.parse_args()

    return args