
import torch

from pathlib import Path

from models.common import DetectMultiBackend

from utils.general import non_max_suppression, scale_boxes

from utils.torch_utils import select_device

from utils.dataloaders import LoadImages, LoadStreams

from typing import List, Optional, Dict, Any

import cv2
import tempfile 
import os





def detect_objects(
    weights: str,
    source: str,
    data: str = './data.yaml',
    imgsz: tuple= (640, 640),
    conf_thres: float = 0.25,
    iou_thres: float = 0.45,
    device: str = '',
    classes: Optional[List[int]] = None,
    max_det: int = 1,

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

    source = str(source)
    use_temp_image = source.isnumeric()
    if use_temp_image:
        cap = cv2.VideoCapture(int(source))
        if not cap.isOpened():
            raise RuntimeError("Failed to open webcam")
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError("Failed to capture frame from webcam")
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            temp_img_path = tmp.name
            cv2.imwrite(temp_img_path, frame)
        source = temp_img_path

    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)

    results: List[List[Dict[str, Any]]] = []

    # frame_limit = 1
    # frame_count = 0

    for path, im, im0, vid_cap, _ in dataset:

        # Preprocess image
        im = torch.from_numpy(im).to(model.device)
        im = im.float() / 255.0
        if im.ndim == 3:
            im = im.unsqueeze(0)

        # Inference
        pred = model(im, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, False, max_det=max_det)
        print("pred", pred)
        dets: List[Dict[str, Any]] = []
        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in det:
                    cls_id = int(cls)
                    dets.append({'class_id': cls_id, 'name': names[cls_id], 'confidence': float(conf)})

        results.append(dets)

        # frame_count += 1
        # if is_webcam and frame_count >= frame_limit:
        #     break

        # --- 5) 웹캠 모드에서만 화면에 띄우기
        # if is_webcam:
        #     cv2.imshow('YOLOv5 Webcam', im0)
        #     if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
        #         break



    # 웹캠 윈도우 정리

    # if is_webcam:
    #     dataset.close()
    #     cv2.destroyAllWindows()
    print(results)

    return results