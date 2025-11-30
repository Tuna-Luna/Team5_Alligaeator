import torch
import cv2
import tempfile
import os
from pathlib import Path
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device
from utils.dataloaders import LoadImages
from typing import List, Optional, Dict, Any

def detect_objects(
    weights: str,
    source: str,
    data: str = './data2.yaml',
    imgsz: tuple = (640, 640),
    conf_thres: float = 0.25,
    iou_thres: float = 0.45,
    device: str = '',
    classes: Optional[List[int]] = None,
    max_det: int = 1,
    temp_img_save_path: Optional[str] = None,  # <-- 추가
) -> List[List[Dict[str, Any]]]:
    """
    Run YOLOv5 inference and return detection results.
    If `source` is numeric (webcam), captures one frame, saves it as:
      - a NamedTemporaryFile for inference
      - and, if `temp_img_save_path` is given, also at that path permanently.
    """
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=False, data=data, fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = (imgsz[0] - imgsz[0] % stride, imgsz[1] - imgsz[1] % stride)

    src = str(source)
    use_temp_image = src.isnumeric()
    if use_temp_image:
        # 1) 웹캠에서 프레임 읽기
        cap = cv2.VideoCapture(int(src))
        if not cap.isOpened():
            raise RuntimeError("Failed to open webcam")
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("Failed to capture frame from webcam")

        # 2) NamedTemporaryFile 에 쓰기 (inference 용)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            temp_img_path = tmp.name
            cv2.imwrite(temp_img_path, frame)

        # 3) 추가 저장 경로가 있으면 그곳에도 쓰기
        if temp_img_save_path:
            # 폴더가 없으면 생성
            os.makedirs(os.path.dirname(temp_img_save_path), exist_ok=True)
            cv2.imwrite(temp_img_save_path, frame)

        source = temp_img_path

    # LoadImages 는 단일 이미지 .jpg 경로 처리
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    results: List[List[Dict[str, Any]]] = []

    for path, im, im0, vid_cap, _ in dataset:
        # 전처리
        im = torch.from_numpy(im).to(model.device)
        im = im.float() / 255.0
        if im.ndim == 3:
            im = im.unsqueeze(0)

        # 추론 + NMS
        pred = model(im, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, False, max_det=max_det)

        dets: List[Dict[str, Any]] = []
        for det in pred:
            if det is not None and len(det):
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in det:
                    cls_id = int(cls)
                    dets.append({
                        'class_id': cls_id,
                        'name': names[cls_id],
                        'confidence': float(conf)
                    })
        results.append(dets)

    # NamedTemporaryFile 은 delete=False 여서 수동 삭제가 필요할 수 있습니다.
    if use_temp_image and os.path.exists(temp_img_path):
        os.unlink(temp_img_path)

    return results
