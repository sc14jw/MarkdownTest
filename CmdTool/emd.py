import sys
import argparse

sys.path.append(".")

from CmdTool.CmdClient import CmdClient


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("incorrect usage please use as so: emd.py <.emd file> <output file name>")
        sys.exit(1)

    inputName = sys.argv[1]
    outputName = sys.argv[2]

    cmdClient = CmdClient()

    cmdClient.createPdf(inputName, outputName)
