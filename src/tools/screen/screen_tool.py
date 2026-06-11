"""Screen analysis and vision with EasyOCR"""

import logging
from typing import Dict, Any, Optional, List
import os
from src.tools.base_tool import BaseTool
from enum import Enum

try:
    import easyocr
except ImportError:
    easyocr = None

try:
    from PIL import Image, ImageGrab
except ImportError:
    Image = None
    ImageGrab = None

try:
    import cv2
except ImportError:
    cv2 = None

logger = logging.getLogger(__name__)

class ScreenAction(Enum):
    """Screen analysis actions"""
    SCREENSHOT = "screenshot"
    OCR = "ocr"
    DETECT_UI_ELEMENTS = "detect_ui_elements"
    ANALYZE_SCREEN = "analyze_screen"
    FIND_BUTTON = "find_button"
    READ_TEXT = "read_text"

class ScreenTool(BaseTool):
    """Tool for screen analysis and vision operations using EasyOCR"""
    
    def __init__(self):
        """Initialize screen tool"""
        super().__init__(
            name="Vision",
            description="Analyze screen: OCR, detect UI elements, extract text, analyze errors"
        )
        self.last_screenshot = None
        self.ocr_reader = None
        self._initialize_ocr()
    
    def _initialize_ocr(self) -> None:
        """Initialize EasyOCR reader"""
        if easyocr:
            try:
                logger.info("[Vision] Loading EasyOCR model...")
                self.ocr_reader = easyocr.Reader(['ko', 'en'], gpu=False)  # CPU mode
                logger.info("[Vision] EasyOCR model loaded")
            except Exception as e:
                logger.warning(f"[Vision] Failed to load EasyOCR: {e}")
        else:
            logger.warning("[Vision] EasyOCR not installed")
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute screen analysis action"""
        try:
            if action == ScreenAction.SCREENSHOT.value:
                return await self._take_screenshot()
            elif action == ScreenAction.OCR.value:
                return await self._ocr(kwargs.get("image_path"))
            elif action == ScreenAction.DETECT_UI_ELEMENTS.value:
                return await self._detect_ui_elements()
            elif action == ScreenAction.ANALYZE_SCREEN.value:
                return await self._analyze_screen()
            elif action == ScreenAction.FIND_BUTTON.value:
                return await self._find_button(kwargs.get("button_name"))
            elif action == ScreenAction.READ_TEXT.value:
                return await self._read_text()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"[Vision] Error executing action {action}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of current screen"""
        logger.info("[Vision] Taking screenshot")
        try:
            if not ImageGrab:
                return {"success": False, "error": "PIL not installed"}
            
            screenshot = ImageGrab.grab()
            path = "temp_screenshot.png"
            screenshot.save(path)
            self.last_screenshot = path
            
            logger.info(f"[Vision] Screenshot saved to {path}")
            return {
                "success": True,
                "path": path,
                "width": screenshot.width,
                "height": screenshot.height
            }
        except Exception as e:
            logger.error(f"[Vision] Failed to take screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    async def _ocr(self, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Perform OCR on image or screenshot"""
        logger.info(f"[Vision] Performing OCR on: {image_path}")
        
        if not self.ocr_reader:
            return {"success": False, "error": "OCR reader not available"}
        
        try:
            # Use provided image or take screenshot
            if image_path is None:
                if self.last_screenshot is None:
                    result = await self._take_screenshot()
                    if not result["success"]:
                        return result
                image_path = self.last_screenshot
            
            # Read image and perform OCR
            results = self.ocr_reader.readtext(image_path, detail=1)
            
            # Format results
            extracted_texts = []
            for detection in results:
                text = detection[1]
                confidence = detection[2]
                bbox = detection[0]
                
                extracted_texts.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
            
            # Combine all text
            full_text = "\n".join([item["text"] for item in extracted_texts])
            
            logger.info(f"[Vision] OCR completed, found {len(extracted_texts)} text regions")
            return {
                "success": True,
                "text": full_text,
                "detections": extracted_texts,
                "count": len(extracted_texts)
            }
        except Exception as e:
            logger.error(f"[Vision] OCR failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _detect_ui_elements(self) -> Dict[str, Any]:
        """Detect UI elements on screen using OCR"""
        logger.info("[Vision] Detecting UI elements")
        try:
            result = await self._take_screenshot()
            if not result["success"]:
                return result
            
            ocr_result = await self._ocr(result["path"])
            if not ocr_result["success"]:
                return ocr_result
            
            # Extract UI elements (buttons, text fields, etc.)
            ui_elements = []
            for detection in ocr_result["detections"]:
                text = detection["text"]
                # Simple heuristics for UI element detection
                if any(keyword in text.lower() for keyword in ["버튼", "button", "확인", "ok", "취소", "cancel", "검색", "search"]):
                    ui_elements.append({
                        "type": "button",
                        "text": text,
                        "bbox": detection["bbox"]
                    })
            
            logger.info(f"[Vision] Found {len(ui_elements)} UI elements")
            return {
                "success": True,
                "elements": ui_elements,
                "count": len(ui_elements)
            }
        except Exception as e:
            logger.error(f"[Vision] Failed to detect UI elements: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_screen(self) -> Dict[str, Any]:
        """Analyze current screen content"""
        logger.info("[Vision] Analyzing screen content")
        try:
            # Take screenshot
            screenshot_result = await self._take_screenshot()
            if not screenshot_result["success"]:
                return screenshot_result
            
            # Perform OCR
            ocr_result = await self._ocr(screenshot_result["path"])
            if not ocr_result["success"]:
                return ocr_result
            
            # Analyze content
            text = ocr_result["text"]
            analysis = {
                "title": "Screen Analysis",
                "text_content": text[:500],  # First 500 chars
                "total_characters": len(text),
                "lines": len(text.split('\n')),
                "has_buttons": any(word in text.lower() for word in ["버튼", "button", "클릭", "click"]),
                "has_errors": any(word in text.lower() for word in ["오류", "error", "경고", "warning"])
            }
            
            logger.info(f"[Vision] Screen analysis completed")
            return {"success": True, "analysis": analysis}
        except Exception as e:
            logger.error(f"[Vision] Failed to analyze screen: {e}")
            return {"success": False, "error": str(e)}
    
    async def _find_button(self, button_name: str) -> Dict[str, Any]:
        """Find a button on screen by name"""
        logger.info(f"[Vision] Finding button: {button_name}")
        try:
            screenshot_result = await self._take_screenshot()
            if not screenshot_result["success"]:
                return screenshot_result
            
            ocr_result = await self._ocr(screenshot_result["path"])
            if not ocr_result["success"]:
                return ocr_result
            
            # Find button by name
            for detection in ocr_result["detections"]:
                if button_name.lower() in detection["text"].lower():
                    bbox = detection["bbox"]
                    # Calculate center of bounding box
                    center_x = sum(point[0] for point in bbox) / len(bbox)
                    center_y = sum(point[1] for point in bbox) / len(bbox)
                    
                    logger.info(f"[Vision] Found button at ({center_x}, {center_y})")
                    return {
                        "success": True,
                        "button": button_name,
                        "location": (center_x, center_y),
                        "found": True
                    }
            
            logger.warning(f"[Vision] Button '{button_name}' not found")
            return {
                "success": False,
                "button": button_name,
                "found": False,
                "error": f"Button '{button_name}' not found on screen"
            }
        except Exception as e:
            logger.error(f"[Vision] Failed to find button: {e}")
            return {"success": False, "error": str(e)}
    
    async def _read_text(self) -> Dict[str, Any]:
        """Read all visible text on screen"""
        logger.info("[Vision] Reading screen text")
        try:
            screenshot_result = await self._take_screenshot()
            if not screenshot_result["success"]:
                return screenshot_result
            
            ocr_result = await self._ocr(screenshot_result["path"])
            if not ocr_result["success"]:
                return ocr_result
            
            return {
                "success": True,
                "text": ocr_result["text"],
                "detections_count": ocr_result["count"]
            }
        except Exception as e:
            logger.error(f"[Vision] Failed to read text: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters"""
        action = kwargs.get("action")
        return action is not None
