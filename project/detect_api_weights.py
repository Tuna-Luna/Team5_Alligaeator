import torch
from pathlib import Path
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_boxes
from utils.torch_utils import select_device
from utils.dataloaders import LoadImages, LoadStreams
from typing import List, Optional, Dict, Any
import cv2
import serial


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
    ### arduino ####
    serial_port : str = '/dev/ttyUSBo', # check later if it's right
    baudrate: int = 9600,
    serial_timeout: float = 0.1,
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
    ######### arduino serial port ##############
    ser = None 
    if serial_port:
        ser = seral.Serial(serial_port, baudrate, timeout=serial_timeout)


    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=False, data=data, fp16=False)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = (imgsz[0] - imgsz[0] % stride, imgsz[1] - imgsz[1] % stride)

    source = str(source)
    is_webcam = source.isnumeric()
    if is_webcam:
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)

    results: List[List[Dict[str, Any]]] = []
    for path, im, im0, vid_cap, _ in dataset:
        # webcam imshow
        if is_webcam:
            im = im[0]     
            im0 = im0[0] 

        # read arduino serial
        serial_data = None 
        if ser and ser.in_waiting:
            try:
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    serial_data = float(line) 
            except Exception:
                serial_data = None
            
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
                    dets.append({'class_id': cls_id, 'name': names[cls_id], 'confidence': float(conf), 'weights' : serial_data})
                    
                    x1, y1, x2, y2 = map(int, xyxy)
                    label = f"{names[cls_id]} {conf:.2f}"
                    cv2.rectangle(im0, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(im0, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

               
        
        results.append(dets)
        # --- 5) 웹캠 모드에서만 화면에 띄우기
        if is_webcam:
            cv2.imshow('YOLOv5 Webcam', im0)
            if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
                break

    # 웹캠 윈도우 정리
    if is_webcam:
        cv2.destroyAllWindows()

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
