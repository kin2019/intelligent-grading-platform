"""
API代理路由
"""
import httpx
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from ...shared.utils.auth import get_current_user
from ...shared.config.settings import get_settings

router = APIRouter()
settings = get_settings()

# 微服务映射
SERVICE_MAPPING = {
    "/users": "http://user-service:8000",
    "/homework": "http://math-service:8000",  # 根据学科路由到不同服务
    "/math": "http://math-service:8000",
    "/chinese": "http://chinese-service:8000",
    "/english": "http://english-service:8000",
    "/ocr": "http://ocr-service:8000",
    "/analysis": "http://analysis-service:8000",
    "/generator": "http://generator-service:8000",
    "/payment": "http://payment-service:8000",
    "/notification": "http://notification-service:8000",
}


class ServiceProxy:
    """服务代理类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def proxy_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        form_data: Dict[str, Any] = None,
        files: Dict[str, Any] = None
    ) -> httpx.Response:
        """代理请求到目标服务"""
        try:
            # 准备请求参数
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers or {},
                "params": params,
            }
            
            # 添加请求体数据
            if json_data:
                request_kwargs["json"] = json_data
            elif form_data:
                request_kwargs["data"] = form_data
            elif files:
                request_kwargs["files"] = files
            
            # 发送请求
            response = await self.client.request(**request_kwargs)
            return response
            
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="服务响应超时"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="服务暂时不可用"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"代理请求失败: {str(e)}"
            )
    
    def get_target_service(self, path: str) -> str:
        """根据路径获取目标服务"""
        for prefix, service_url in SERVICE_MAPPING.items():
            if path.startswith(prefix):
                return service_url
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对应的服务"
        )
    
    def build_target_url(self, path: str, query_string: str = None) -> str:
        """构建目标URL"""
        service_url = self.get_target_service(path)
        
        # 移除服务前缀，保留实际路径
        for prefix in SERVICE_MAPPING.keys():
            if path.startswith(prefix):
                actual_path = path[len(prefix):] or "/"
                break
        else:
            actual_path = path
        
        target_url = f"{service_url}{actual_path}"
        
        if query_string:
            target_url += f"?{query_string}"
        
        return target_url


# 全局服务代理实例
service_proxy = ServiceProxy()


async def proxy_to_service(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """通用服务代理函数"""
    try:
        # 构建目标URL
        path = request.url.path.replace("/api", "", 1)  # 移除/api前缀
        query_string = str(request.url.query) if request.url.query else None
        target_url = service_proxy.build_target_url(path, query_string)
        
        # 准备请求头
        headers = dict(request.headers)
        
        # 移除Host头以避免冲突
        headers.pop("host", None)
        
        # 添加用户信息到请求头
        headers["X-User-ID"] = str(current_user["id"])
        headers["X-User-Role"] = current_user["role"]
        headers["X-User-OpenID"] = current_user["openid"]
        if current_user.get("vip_type"):
            headers["X-User-VIP-Type"] = current_user["vip_type"]
        
        # 处理请求体
        json_data = None
        form_data = None
        files = None
        
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            json_data = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
        elif "multipart/form-data" in content_type:
            form = await request.form()
            form_data = {}
            files = {}
            for key, value in form.items():
                if hasattr(value, "file"):  # 文件类型
                    files[key] = (value.filename, value.file, value.content_type)
                else:
                    form_data[key] = value
        
        # 代理请求
        response = await service_proxy.proxy_request(
            method=request.method,
            url=target_url,
            headers=headers,
            json_data=json_data,
            form_data=form_data,
            files=files
        )
        
        # 构建响应
        response_headers = dict(response.headers)
        
        # 移除可能冲突的响应头
        response_headers.pop("content-encoding", None)
        response_headers.pop("transfer-encoding", None)
        
        return StreamingResponse(
            content=iter([response.content]),
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"代理请求失败: {str(e)}"
        )


# 注册所有代理路由
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_all_requests(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """代理所有API请求"""
    return await proxy_to_service(request, current_user)


# 特殊路由处理
@router.post("/homework/submit")
async def submit_homework(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """提交作业的特殊处理"""
    # 检查配额
    from ..routes.auth import check_and_consume_quota
    await check_and_consume_quota(current_user)
    
    # 代理到相应的学科服务
    return await proxy_to_service(request, current_user)


@router.get("/services/status")
async def get_services_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取所有服务状态"""
    services_status = {}
    
    for service_name, service_url in SERVICE_MAPPING.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url,
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            services_status[service_name] = {
                "status": "error",
                "url": service_url,
                "error": str(e)
            }
    
    return {
        "code": 200,
        "message": "获取服务状态成功",
        "data": services_status
    }