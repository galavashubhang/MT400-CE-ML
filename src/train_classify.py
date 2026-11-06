"""Train the YOLO classification model (Dive Deeper type). Run in Colab."""
import argparse
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/cls")
    ap.add_argument("--model", default="yolo26n-cls.pt")
    ap.add_argument("--epochs", type=int, default=25)
    ap.add_argument("--imgsz", type=int, default=224)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--project", default="runs/classify")
    ap.add_argument("--name", default="yolo26n-corrosion-type")
    args = ap.parse_args()
    model = YOLO(args.model)
    results = model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz,
                          batch=args.batch, project=args.project, name=args.name,
                          seed=42, patience=10)
    print(f"Done. Best weights: {results.save_dir}/weights/best.pt")
    print("Copy that file to models/classify/best.pt for the app.")


if __name__ == "__main__":
    main()
