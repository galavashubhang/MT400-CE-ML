"""Train the YOLO detection model. Run in Colab (see notebooks/01)."""
import argparse
from ultralytics import YOLO


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/yolo_detect/data.yaml")
    ap.add_argument("--model", default="yolo26n.pt")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--project", default="runs/detect")
    ap.add_argument("--name", default="yolo26n-corrosion")
    args = ap.parse_args()
    model = YOLO(args.model)
    results = model.train(data=args.data, epochs=args.epochs, imgsz=args.imgsz,
                          batch=args.batch, project=args.project, name=args.name,
                          seed=42, patience=15)
    print(f"Done. Best weights: {results.save_dir}/weights/best.pt")
    print("Copy that file to models/detect/best.pt for the app.")


if __name__ == "__main__":
    main()
