"""
视觉OCR文字提取服务
使用多种OCR引擎进行图片文字识别和提取
"""
import base64
import json
import re
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
from datetime import datetime

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("EasyOCR未安装，将使用模拟OCR")

try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("PaddleOCR未安装，将使用模拟OCR")


class TextRegion:
    """文字区域信息"""
    def __init__(self, text: str, bbox: List[int], confidence: float, 
                 region_type: str = 'text'):
        self.text = text.strip()
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.confidence = confidence
        self.region_type = region_type  # text, number, formula, choice
        self.position = self._calculate_position()
    
    def _calculate_position(self) -> Dict[str, int]:
        """计算文字区域的位置信息"""
        return {
            'x': self.bbox[0],
            'y': self.bbox[1], 
            'width': self.bbox[2] - self.bbox[0],
            'height': self.bbox[3] - self.bbox[1],
            'center_x': (self.bbox[0] + self.bbox[2]) // 2,
            'center_y': (self.bbox[1] + self.bbox[3]) // 2
        }


class VisionOCRService:
    """视觉OCR服务"""
    
    def __init__(self):
        self.ocr_engines = []
        self._init_ocr_engines()
        
        # 文字类型识别模式
        self.text_patterns = {
            'question_number': r'^(\d+)[\.、)]\s*',
            'choice_option': r'^[A-H][\.、)]\s*',
            'formula': r'[\+\-\×\÷\=\(\)\^\²\³\√\∫\∑]',
            'number': r'^\d+\.?\d*$',
            'fraction': r'\d+/\d+',
            'percentage': r'\d+\.?\d*%',
            'chinese_number': r'[零一二三四五六七八九十百千万]',
            'english_word': r'^[A-Za-z]+$',
            'mixed_math': r'[0-9\+\-\×\÷\=\(\)]+',
            'punctuation': r'^[。，！？、；：""''（）【】]+$'
        }
    
    def _init_ocr_engines(self):
        """初始化OCR引擎"""
        try:
            # 初始化EasyOCR
            if EASYOCR_AVAILABLE:
                self.easy_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                self.ocr_engines.append('easyocr')
                print("EasyOCR初始化成功")
        except Exception as e:
            print(f"EasyOCR初始化失败: {e}")
        
        try:
            # 初始化PaddleOCR  
            if PADDLEOCR_AVAILABLE:
                self.paddle_ocr = paddleocr.PaddleOCR(
                    use_angle_cls=True, 
                    lang='ch',
                    show_log=False
                )
                self.ocr_engines.append('paddleocr')
                print("PaddleOCR初始化成功")
        except Exception as e:
            print(f"PaddleOCR初始化失败: {e}")
        
        if not self.ocr_engines:
            print("警告：没有可用的OCR引擎，将使用模拟OCR")
            self.ocr_engines.append('mock')
    
    def extract_text_from_image(self, image_path: str, 
                              preprocessing: bool = True) -> Dict[str, Any]:
        """
        从图片中提取文字内容
        
        Args:
            image_path: 图片文件路径
            preprocessing: 是否进行图片预处理
            
        Returns:
            包含提取结果的字典
        """
        try:
            # 读取和预处理图片
            image = self._load_and_preprocess_image(image_path, preprocessing)
            
            # 使用多个OCR引擎提取文字
            ocr_results = []
            
            for engine in self.ocr_engines:
                if engine == 'easyocr' and EASYOCR_AVAILABLE:
                    result = self._extract_with_easyocr(image)
                elif engine == 'paddleocr' and PADDLEOCR_AVAILABLE:
                    result = self._extract_with_paddleocr(image)
                else:
                    result = self._extract_with_mock_ocr(image_path)
                
                if result:
                    ocr_results.append(result)
            
            # 融合多个OCR结果
            final_result = self._merge_ocr_results(ocr_results)
            
            # 分析文字区域和类型
            analyzed_regions = self._analyze_text_regions(final_result['regions'])
            
            # 构建结构化结果
            structured_result = self._build_structured_result(analyzed_regions)
            
            return {
                'success': True,
                'message': f'成功提取文字，共识别{len(analyzed_regions)}个文字区域',
                'total_regions': len(analyzed_regions),
                'regions': analyzed_regions,
                'structured_content': structured_result,
                'raw_text': self._extract_plain_text(analyzed_regions),
                'confidence_score': self._calculate_overall_confidence(analyzed_regions),
                'extraction_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"文字提取失败: {e}")
            return {
                'success': False,
                'message': f'文字提取失败: {str(e)}',
                'regions': [],
                'structured_content': {},
                'raw_text': '',
                'confidence_score': 0.0
            }
    
    def _load_and_preprocess_image(self, image_path: str, 
                                 preprocessing: bool = True) -> np.ndarray:
        """加载并预处理图片"""
        
        # 读取图片
        if image_path.startswith('data:image'):
            # 处理base64编码的图片
            image_data = base64.b64decode(image_path.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
        else:
            # 处理文件路径
            image = Image.open(image_path)
        
        # 转换为RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 图片预处理（如果启用）
        if preprocessing:
            image = self._enhance_image_quality(image)
        
        # 转换为numpy数组
        return np.array(image)
    
    def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """增强图片质量以提高OCR识别率"""
        
        # 调整对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # 调整锐度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # 降噪
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # 如果图片太小，进行放大
        width, height = image.size
        if width < 800 or height < 600:
            scale = max(800/width, 600/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = image.resize((new_width, new_height), Image.LANCZOS)
        
        return image
    
    def _extract_with_easyocr(self, image: np.ndarray) -> Dict[str, Any]:
        """使用EasyOCR提取文字"""
        try:
            results = self.easy_reader.readtext(image)
            regions = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3 and text.strip():  # 过滤置信度过低的结果
                    # EasyOCR返回的bbox是四个点的坐标，转换为矩形坐标
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    bbox_rect = [
                        int(min(x_coords)), int(min(y_coords)),
                        int(max(x_coords)), int(max(y_coords))
                    ]
                    
                    region = TextRegion(text, bbox_rect, confidence)
                    regions.append(region)
            
            return {
                'engine': 'easyocr',
                'regions': regions,
                'total_detected': len(results)
            }
            
        except Exception as e:
            print(f"EasyOCR提取失败: {e}")
            return None
    
    def _extract_with_paddleocr(self, image: np.ndarray) -> Dict[str, Any]:
        """使用PaddleOCR提取文字"""
        try:
            results = self.paddle_ocr.ocr(image, cls=True)
            regions = []
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        bbox_points, (text, confidence) = line
                        
                        if confidence > 0.5 and text.strip():
                            # 转换坐标格式
                            x_coords = [point[0] for point in bbox_points]
                            y_coords = [point[1] for point in bbox_points]
                            bbox_rect = [
                                int(min(x_coords)), int(min(y_coords)),
                                int(max(x_coords)), int(max(y_coords))
                            ]
                            
                            region = TextRegion(text, bbox_rect, confidence)
                            regions.append(region)
            
            return {
                'engine': 'paddleocr',
                'regions': regions,
                'total_detected': len(regions)
            }
            
        except Exception as e:
            print(f"PaddleOCR提取失败: {e}")
            return None
    
    def _extract_with_mock_ocr(self, image_path: str) -> Dict[str, Any]:
        """模拟OCR提取（用于开发测试）"""
        print("使用模拟OCR进行文字提取")
        
        # 根据文件名或路径推测可能的题目内容
        mock_texts = [
            "1. 计算 125 × 8 = ?",
            "A. 1000    B. 1200    C. 1500    D. 800",
            "2. 小明买了3本书，每本15元，一共花了多少钱？",
            "解：3 × 15 = 45（元）",
            "答：一共花了45元。",
            "3. 下列词语中，没有错别字的是（）",
            "A. 走投无路  B. 变本加利  C. 再接再励  D. 一如即往"
        ]
        
        regions = []
        y_offset = 50
        
        for i, text in enumerate(mock_texts):
            bbox = [50, y_offset, 300, y_offset + 30]
            confidence = 0.85 + (i % 3) * 0.05  # 模拟不同的置信度
            region = TextRegion(text, bbox, confidence)
            regions.append(region)
            y_offset += 60
        
        return {
            'engine': 'mock',
            'regions': regions,
            'total_detected': len(regions)
        }
    
    def _merge_ocr_results(self, ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """融合多个OCR引擎的结果"""
        if not ocr_results:
            return {'regions': []}
        
        # 如果只有一个结果，直接返回
        if len(ocr_results) == 1:
            return ocr_results[0]
        
        # 合并多个引擎的结果，去重并选择最佳结果
        all_regions = []
        for result in ocr_results:
            all_regions.extend(result.get('regions', []))
        
        # 简单的去重策略：按位置相近度合并
        merged_regions = self._deduplicate_regions(all_regions)
        
        return {
            'regions': merged_regions,
            'engines_used': [r['engine'] for r in ocr_results]
        }
    
    def _deduplicate_regions(self, regions: List[TextRegion]) -> List[TextRegion]:
        """去重相似的文字区域"""
        if not regions:
            return []
        
        # 按Y坐标排序
        sorted_regions = sorted(regions, key=lambda r: r.position['y'])
        
        deduplicated = []
        used_indices = set()
        
        for i, region in enumerate(sorted_regions):
            if i in used_indices:
                continue
            
            # 找到位置相近的区域
            similar_regions = [region]
            
            for j, other_region in enumerate(sorted_regions):
                if j <= i or j in used_indices:
                    continue
                
                # 判断是否为相似区域
                if self._are_regions_similar(region, other_region):
                    similar_regions.append(other_region)
                    used_indices.add(j)
            
            # 选择置信度最高的区域
            best_region = max(similar_regions, key=lambda r: r.confidence)
            deduplicated.append(best_region)
            used_indices.add(i)
        
        return deduplicated
    
    def _are_regions_similar(self, region1: TextRegion, region2: TextRegion, 
                           threshold: float = 0.7) -> bool:
        """判断两个文字区域是否相似"""
        
        # 计算位置重叠度
        bbox1, bbox2 = region1.bbox, region2.bbox
        
        # 计算重叠区域
        overlap_x1 = max(bbox1[0], bbox2[0])
        overlap_y1 = max(bbox1[1], bbox2[1]) 
        overlap_x2 = min(bbox1[2], bbox2[2])
        overlap_y2 = min(bbox1[3], bbox2[3])
        
        if overlap_x2 <= overlap_x1 or overlap_y2 <= overlap_y1:
            return False
        
        overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)
        
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        
        # 计算重叠比例
        overlap_ratio = overlap_area / min(area1, area2)
        
        return overlap_ratio > threshold
    
    def _analyze_text_regions(self, regions: List[TextRegion]) -> List[Dict[str, Any]]:
        """分析文字区域并识别类型"""
        analyzed_regions = []
        
        for region in regions:
            analysis = self._classify_text_type(region.text)
            
            region_dict = {
                'text': region.text,
                'bbox': region.bbox,
                'confidence': region.confidence,
                'position': region.position,
                'type': analysis['type'],
                'subtype': analysis.get('subtype'),
                'properties': analysis.get('properties', {}),
                'is_question_part': analysis.get('is_question_part', False),
                'is_answer_part': analysis.get('is_answer_part', False)
            }
            
            analyzed_regions.append(region_dict)
        
        return analyzed_regions
    
    def _classify_text_type(self, text: str) -> Dict[str, Any]:
        """识别文字类型"""
        text_clean = text.strip()
        
        # 题号识别
        if re.match(self.text_patterns['question_number'], text_clean):
            return {
                'type': 'question_number',
                'subtype': 'primary',
                'is_question_part': True,
                'properties': {'number': re.match(r'^(\d+)', text_clean).group(1)}
            }
        
        # 选择题选项
        if re.match(self.text_patterns['choice_option'], text_clean):
            return {
                'type': 'choice_option',
                'subtype': 'option',
                'is_answer_part': True,
                'properties': {'option': re.match(r'^([A-H])', text_clean).group(1)}
            }
        
        # 数学公式
        if re.search(self.text_patterns['formula'], text_clean):
            formula_type = 'arithmetic'
            if '=' in text_clean:
                formula_type = 'equation'
            elif any(symbol in text_clean for symbol in ['√', '∫', '∑']):
                formula_type = 'advanced'
            
            return {
                'type': 'formula',
                'subtype': formula_type,
                'is_question_part': True,
                'properties': {'complexity': len(re.findall(r'[+\-×÷=()]', text_clean))}
            }
        
        # 纯数字
        if re.match(self.text_patterns['number'], text_clean):
            return {
                'type': 'number',
                'subtype': 'decimal' if '.' in text_clean else 'integer',
                'is_answer_part': True,
                'properties': {'value': float(text_clean) if '.' in text_clean else int(text_clean)}
            }
        
        # 分数
        if re.search(self.text_patterns['fraction'], text_clean):
            return {
                'type': 'fraction',
                'is_answer_part': True,
                'properties': {'format': 'fraction'}
            }
        
        # 百分比
        if re.search(self.text_patterns['percentage'], text_clean):
            return {
                'type': 'percentage', 
                'is_answer_part': True,
                'properties': {'format': 'percentage'}
            }
        
        # 英文单词
        if re.match(self.text_patterns['english_word'], text_clean):
            return {
                'type': 'english_text',
                'subtype': 'word' if len(text_clean.split()) == 1 else 'phrase',
                'properties': {'word_count': len(text_clean.split())}
            }
        
        # 中文文本
        if any('\u4e00' <= char <= '\u9fff' for char in text_clean):
            return {
                'type': 'chinese_text',
                'subtype': 'sentence' if len(text_clean) > 10 else 'word',
                'properties': {'char_count': len(text_clean)}
            }
        
        # 标点符号
        if re.match(self.text_patterns['punctuation'], text_clean):
            return {
                'type': 'punctuation',
                'properties': {'symbols': list(text_clean)}
            }
        
        # 混合数学表达式
        if re.search(self.text_patterns['mixed_math'], text_clean):
            return {
                'type': 'math_expression',
                'is_question_part': True,
                'properties': {'has_operators': True}
            }
        
        # 默认为普通文本
        return {
            'type': 'text',
            'subtype': 'general',
            'properties': {'length': len(text_clean)}
        }
    
    def _build_structured_result(self, regions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建结构化的内容结果"""
        
        structured = {
            'questions': [],
            'answers': [],
            'formulas': [],
            'choices': [],
            'text_blocks': []
        }
        
        current_question = None
        
        for region in regions:
            region_type = region['type']
            
            # 题号处理
            if region_type == 'question_number':
                if current_question:
                    structured['questions'].append(current_question)
                
                current_question = {
                    'number': region['properties'].get('number'),
                    'bbox': region['bbox'],
                    'content_parts': [],
                    'answer_options': [],
                    'formulas': []
                }
            
            # 选择题选项
            elif region_type == 'choice_option':
                option_info = {
                    'option': region['properties'].get('option'),
                    'text': region['text'],
                    'bbox': region['bbox']
                }
                
                if current_question:
                    current_question['answer_options'].append(option_info)
                
                structured['choices'].append(option_info)
            
            # 公式和数学表达式
            elif region_type in ['formula', 'math_expression']:
                formula_info = {
                    'text': region['text'],
                    'bbox': region['bbox'],
                    'type': region.get('subtype', 'general'),
                    'complexity': region['properties'].get('complexity', 0)
                }
                
                if current_question:
                    current_question['formulas'].append(formula_info)
                
                structured['formulas'].append(formula_info)
            
            # 答案相关
            elif region.get('is_answer_part'):
                answer_info = {
                    'text': region['text'],
                    'type': region_type,
                    'bbox': region['bbox'],
                    'properties': region.get('properties', {})
                }
                structured['answers'].append(answer_info)
            
            # 题目内容部分
            elif region.get('is_question_part') or region_type in ['chinese_text', 'english_text']:
                text_info = {
                    'text': region['text'],
                    'type': region_type,
                    'bbox': region['bbox']
                }
                
                if current_question:
                    current_question['content_parts'].append(text_info)
                
                structured['text_blocks'].append(text_info)
        
        # 添加最后一个题目
        if current_question:
            structured['questions'].append(current_question)
        
        return structured
    
    def _extract_plain_text(self, regions: List[Dict[str, Any]]) -> str:
        """提取纯文本内容"""
        # 按位置排序（从上到下，从左到右）
        sorted_regions = sorted(regions, 
                              key=lambda r: (r['position']['y'], r['position']['x']))
        
        text_parts = []
        last_y = 0
        
        for region in sorted_regions:
            current_y = region['position']['y']
            
            # 如果是新行，添加换行符
            if current_y > last_y + 20:  # 20像素的行间距阈值
                text_parts.append('\n')
            
            text_parts.append(region['text'])
            text_parts.append(' ')  # 添加空格分隔
            
            last_y = current_y
        
        return ''.join(text_parts).strip()
    
    def _calculate_overall_confidence(self, regions: List[Dict[str, Any]]) -> float:
        """计算整体置信度"""
        if not regions:
            return 0.0
        
        total_confidence = sum(region['confidence'] for region in regions)
        return round(total_confidence / len(regions), 3)
    
    def get_text_statistics(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取文字提取统计信息"""
        if not ocr_result.get('success'):
            return {'error': '提取失败，无法生成统计信息'}
        
        regions = ocr_result.get('regions', [])
        structured = ocr_result.get('structured_content', {})
        
        stats = {
            'total_regions': len(regions),
            'questions_detected': len(structured.get('questions', [])),
            'choices_detected': len(structured.get('choices', [])),
            'formulas_detected': len(structured.get('formulas', [])),
            'average_confidence': ocr_result.get('confidence_score', 0),
            'text_types': {},
            'extraction_quality': 'unknown'
        }
        
        # 统计文字类型分布
        for region in regions:
            region_type = region.get('type', 'unknown')
            stats['text_types'][region_type] = stats['text_types'].get(region_type, 0) + 1
        
        # 评估提取质量
        confidence = stats['average_confidence']
        if confidence >= 0.8:
            stats['extraction_quality'] = 'excellent'
        elif confidence >= 0.6:
            stats['extraction_quality'] = 'good'
        elif confidence >= 0.4:
            stats['extraction_quality'] = 'fair'
        else:
            stats['extraction_quality'] = 'poor'
        
        return stats