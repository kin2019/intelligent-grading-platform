#!/usr/bin/env python3
"""
演示用HTTP服务器
提供基本的批改API接口
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import time
from datetime import datetime

class CorrectionHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        """设置CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/api/v1/health':
            self._health_check()
        else:
            self._not_found()
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == '/api/v1/homework/submit':
            self._handle_homework_submit()
        elif self.path == '/api/v1/image/ocr':
            self._handle_ocr()
        else:
            self._not_found()
    
    def _health_check(self):
        """健康检查"""
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "ZYJC Math Correction Service",
            "version": "1.0.0"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def _handle_homework_submit(self):
        """处理作业提交"""
        try:
            # 获取请求数据长度
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 简化处理 - 模拟批改结果
            homework_id = int(time.time())
            
            response = {
                "success": True,
                "message": "作业提交成功",
                "id": homework_id,
                "status": "processing",
                "estimated_time": "3-5分钟"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            print(f"收到作业提交请求，ID: {homework_id}")
            
        except Exception as e:
            self._error_response(f"处理失败: {str(e)}")
    
    def _handle_ocr(self):
        """处理OCR识别"""
        try:
            # 模拟OCR识别结果
            response = {
                "success": True,
                "text": "12 + 8 = 20\n15 - 7 = 8\n6 * 4 = 24\n18 / 3 = 6",
                "question_count": 4,
                "confidence": 0.95,
                "processing_time": 1.2
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
            print("OCR识别请求处理完成")
            
        except Exception as e:
            self._error_response(f"OCR识别失败: {str(e)}")
    
    def _not_found(self):
        """404响应"""
        response = {
            "error": "Not Found",
            "message": f"接口 {self.path} 不存在"
        }
        
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def _error_response(self, message, status_code=500):
        """错误响应"""
        response = {
            "error": "Internal Server Error",
            "message": message
        }
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(port=8000):
    """启动HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CorrectionHandler)
    
    print("=" * 60)
    print("中小学智能批改平台后端服务 (演示版)")
    print("=" * 60)
    print(f"服务地址: http://localhost:{port}")
    print(f"健康检查: http://localhost:{port}/api/v1/health")
    print(f"API文档: 作业提交 - POST /api/v1/homework/submit")
    print(f"API文档: OCR识别 - POST /api/v1/image/ocr")
    print("=" * 60)
    print("按 Ctrl+C 停止服务")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n停止服务...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server(8001)