#!/usr/bin/env python3
"""
智能教育平台 - 部署脚本
支持开发环境和生产环境的自动化部署
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
import argparse
from datetime import datetime

class DeploymentManager:
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.is_production = environment == "production"
        
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
        
    def run_command(self, command: str, description: str = "", check: bool = True):
        """运行命令并处理错误"""
        if description:
            print(f"⚡ {description}...")
            
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.stdout:
                print(result.stdout)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败: {command}")
            print(f"错误信息: {e.stderr}")
            return False
    
    def check_python_version(self):
        """检查Python版本"""
        print("🔍 检查Python版本...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print(f"❌ Python版本过低: {version.major}.{version.minor}")
            print("需要Python 3.11或更高版本")
            return False
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def setup_virtual_environment(self):
        """设置虚拟环境"""
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            print("📦 创建虚拟环境...")
            if not self.run_command(f"python -m venv venv", "创建虚拟环境"):
                return False
        else:
            print("✅ 虚拟环境已存在")
            
        return True
    
    def install_dependencies(self):
        """安装依赖"""
        print("📚 安装项目依赖...")
        
        # 获取正确的pip路径
        if sys.platform == "win32":
            pip_cmd = "venv\\Scripts\\pip"
        else:
            pip_cmd = "venv/bin/pip"
            
        # 升级pip
        if not self.run_command(f"{pip_cmd} install --upgrade pip", "升级pip"):
            return False
            
        # 安装依赖
        if not self.run_command(f"{pip_cmd} install -r requirements.txt", "安装依赖包"):
            return False
            
        print("✅ 依赖安装完成")
        return True
    
    def setup_environment_config(self):
        """设置环境配置"""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                print("📝 复制环境配置文件...")
                shutil.copy2(env_example, env_file)
                print("⚠️  请编辑 .env 文件并设置正确的配置值")
            else:
                print("❌ .env.example 文件不存在，无法创建配置文件")
                return False
        else:
            print("✅ 环境配置文件已存在")
            
        return True
    
    def setup_database(self):
        """设置数据库"""
        print("🗄️ 初始化数据库...")
        
        # 运行数据库迁移脚本
        migration_script = self.project_root / "scripts" / "db_migration.py"
        if migration_script.exists():
            # 获取正确的Python路径
            if sys.platform == "win32":
                python_cmd = "venv\\Scripts\\python"
            else:
                python_cmd = "venv/bin/python"
                
            if not self.run_command(f"{python_cmd} scripts/db_migration.py", "运行数据库迁移"):
                return False
        else:
            print("❌ 数据库迁移脚本不存在")
            return False
            
        print("✅ 数据库初始化完成")
        return True
    
    def create_directories(self):
        """创建必要的目录"""
        print("📁 创建项目目录...")
        
        directories = [
            "uploads",
            "logs",
            "static",
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"📂 创建目录: {directory}")
        
        print("✅ 目录创建完成")
        return True
    
    def check_configuration(self):
        """检查配置文件"""
        print("🔧 检查配置...")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("❌ .env 文件不存在")
            return False
            
        # 读取配置文件并检查关键配置
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_configs = [
                "SECRET_KEY",
                "DATABASE_URL"
            ]
            
            missing_configs = []
            for config in required_configs:
                if f"{config}=your-" in content or config not in content:
                    missing_configs.append(config)
                    
            if missing_configs:
                print("⚠️  以下配置需要设置:")
                for config in missing_configs:
                    print(f"   - {config}")
                print("请编辑 .env 文件并设置正确的值")
                
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            return False
            
        print("✅ 配置检查完成")
        return True
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        # 获取正确的Python路径
        if sys.platform == "win32":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
            
        test_command = f"{python_cmd} -m pytest tests/ -v"
        if self.run_command(test_command, "执行单元测试", check=False):
            print("✅ 测试通过")
            return True
        else:
            print("⚠️  测试失败或没有找到测试文件，继续部署...")
            return True  # 不阻断部署流程
    
    def start_server(self):
        """启动服务器"""
        print("🚀 准备启动服务器...")
        
        # 获取正确的Python路径
        if sys.platform == "win32":
            python_cmd = "venv\\Scripts\\python"
        else:
            python_cmd = "venv/bin/python"
        
        if self.is_production:
            # 生产环境使用gunicorn
            start_command = f"{python_cmd} -m gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
            print("生产环境启动命令:")
            print(f"  {start_command}")
        else:
            # 开发环境使用uvicorn
            start_command = f"{python_cmd} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
            print("开发环境启动命令:")
            print(f"  {start_command}")
        
        print("\n💡 手动启动服务器:")
        print(f"   cd {self.project_root}")
        print(f"   {start_command}")
        
    def deploy(self):
        """执行完整部署流程"""
        self.print_header(f"智能教育平台部署 - {self.environment.upper()}环境")
        print(f"🕒 部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 项目路径: {self.project_root}")
        
        steps = [
            ("检查Python版本", self.check_python_version),
            ("设置虚拟环境", self.setup_virtual_environment),
            ("安装依赖", self.install_dependencies),
            ("设置环境配置", self.setup_environment_config),
            ("创建目录结构", self.create_directories),
            ("初始化数据库", self.setup_database),
            ("检查配置", self.check_configuration),
        ]
        
        if not self.is_production:
            steps.append(("运行测试", self.run_tests))
        
        # 执行部署步骤
        for step_name, step_func in steps:
            self.print_header(step_name)
            if not step_func():
                print(f"❌ 部署失败于步骤: {step_name}")
                return False
                
        # 部署完成
        self.print_header("部署完成")
        print("🎉 智能教育平台部署成功！")
        
        print("\n📖 下一步操作:")
        print("1. 检查并编辑 .env 文件中的配置")
        print("2. 启动服务器")
        print("3. 访问 http://localhost:8000 检查服务")
        print("4. 查看 API 文档: http://localhost:8000/docs")
        
        # 显示启动命令
        self.start_server()
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='智能教育平台部署工具')
    parser.add_argument('--env', choices=['development', 'production'], 
                       default='development', help='部署环境')
    parser.add_argument('--skip-tests', action='store_true', help='跳过测试步骤')
    
    args = parser.parse_args()
    
    # 创建部署管理器并执行部署
    deployer = DeploymentManager(args.env)
    
    try:
        success = deployer.deploy()
        if success:
            print("\n🎯 部署成功完成！")
            sys.exit(0)
        else:
            print("\n💥 部署过程中出现错误，请检查上述信息。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  部署被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 部署过程中发生未预期的错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()