import torch
from pathlib import Path
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device
from utils.dataloaders import LoadImages
from typing import List, Optional, Dict, Any


def detect_objects(
    weights: str,
    source: str,
    data: str = './data.yaml',
    imgsz: tuple= (640, 640),
    conf_thres: float = 0.25,
    iou_thres: float = 0.45,
    device: str = '',
    classes: Optional[List[int]] = None,
    max_det: int = 1000,
) -> List[List[Dict[str, Any]]]:
    """
    Run YOLOv5 inference and return detection results without displaying or saving images.

    Args:
        weights (str): Path to model weights (.pt file).
        source (str): Image file, directory, or webcam index (e.g., '0').
        data (str): Path to dataset YAML file (contains class names).
        imgsz (tuple[int, int]): Inference size (height, width).
        conf_thres (float): Confidence threshold.
        iou_thres (float): NMS IoU threshold.
        device (str): CUDA device index or 'cpu'.
        classes (Optional[List[int]]): List of class indices to filter, or None for no filtering.
        max_det (int): Maximum detections per image.

    Returns:
        List of lists, each inner list contains dicts with 'class_id', 'name', 'confidence'.
    """
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=False, data=data, fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = (imgsz[0] - imgsz[0] % stride, imgsz[1] - imgsz[1] % stride)

    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)

    results: List[List[Dict[str, Any]]] = []
    for path, im, im0, vid_cap, _ in dataset:
        # Preprocess image
        im = torch.from_numpy(im).to(model.device)
        im = im.float() / 255.0
        if im.ndim == 3:
            im = im.unsqueeze(0)

        # Inference
        pred = model(im, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, False, max_det=max_det)

        dets: List[Dict[str, Any]] = []
        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in det:
                    cls_id = int(cls)
                    dets.append({'class_id': cls_id, 'name': names[cls_id], 'confidence': float(conf)})

        results.append(dets)

    return results


# Example usage:
# from detect_api import detect_objects
# results = detect_objects(
#     weights='./best.pt',
#     source='./egg.jpg',  # or image path/directory
#     data='./data.yaml',
#     device='cpu'
# )
# print(results)
