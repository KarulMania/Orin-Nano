# Python'un gömülü argüman işleme kütüphanesini içe aktarır. 
# Bu kütüphane, komut satırından verilen argümanları kolayca okumayı ve işlemeyi sağlar.
# Örneğin: python main.py --personCamFps 30 gibi bir çağrının içeriği burdan ayrıştırılır.
import argparse


def parseArguments():
    parser = argparse.ArgumentParser(description='Video processing and data sending script.')

    # Komut satırından alınacak argümanları tanımlar.
    # --personCam, --bicycleCam, --reverse, --personCamFps ve --bicycleCamFps argümanları için --help yazarsa açıklama alır.
    # Terminalde örnek girdi:
       # python main.py --help
    # Örnek çıktı:
       # Video processing and data sending script.
          # --personCam    source for cam1 ....
          # --bicycleCam   source for cam2 ....
    parser.add_argument('--personCam', type=int, default=1, help='source for cam1; 1 for iptv on personcam ; 0 for videopath on personcam')
    parser.add_argument('--bicycleCam', type=int, default=1, help='source for cam2; 1 for iptv on bicyclecam ; 0 for videopath on bicyclecam')
    parser.add_argument('--reverse', type=int, default=0, help='1 for bicycleCounter on Personcam else 0')
    parser.add_argument('--personCamFps', type=int, default=0, help='Cam fps for personcam')
    parser.add_argument('--bicycleCamFps', type=int, default=0, help='Cam fps for backCam')
    
    # Terminalden verilen argümanları ayrıştırır ve args değişkenine atar.
      # Bu, kullanıcı tarafından verilen argümanların işlenmesini sağlar.
      # Örneğin: args.PersonCamFps --30 gibi bir argüman verilirse, args.personCamFps 30 değerini alır.
    args = parser.parse_args()

    return args
