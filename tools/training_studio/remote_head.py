"""Isolated DGX container entry point, kept separate from the existing teacher service."""
import argparse
from pathlib import Path


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--run",type=Path,required=True)
  args=parser.parse_args()
  from tools.training_studio.head import train
  train(args.run)


if __name__=="__main__":
  main()
