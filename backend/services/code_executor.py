"""
Docker 代码执行沙箱服务
提供安全的代码执行环境，支持资源限制和隔离
"""

import docker
import tempfile
import os
import time
from typing import Dict, Optional, Any, Tuple
import threading
from contextlib import redirect_stdout, redirect_stderr
import io


class CodeExecutor:
    """Docker 代码执行器"""

    # 危险函数和模块调用模式
    DANGEROUS_PATTERNS = [
        'os.system', 'os.popen', 'os.exec', 'os.spawn',
        'subprocess', 'commands.', 'importlib',
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file(', 'input(',
        'shutil.rmtree', 'os.remove', 'os.unlink',
        'os.rmdir', 'os.makedirs',
        'sys.exit', 'quit(', 'exit(',
        'signal.', 'multiprocessing',
        'threading._start_new_thread',
        'ctypes', 'cffi',
        'import socket',
    ]

    # 危险的 import 模块列表
    DANGEROUS_IMPORTS = ['os', 'subprocess', 'shutil', 'ctypes', 'signal']

    def __init__(
        self,
        timeout: int = 30,
        memory_limit: str = "512m",
        cpu_limit: float = 0.5,
        image: str = "python:3.10-slim",
        docker_base_url: str = "unix:///var/run/docker.sock"
    ):
        """
        初始化代码执行器

        Args:
            timeout: 执行超时时间（秒）
            memory_limit: 内存限制（如 "512m", "1g"）
            cpu_limit: CPU 限制（0.5 表示 0.5 个核心）
            image: Docker 镜像名称
            docker_base_url: Docker daemon 地址
        """
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.image = image
        self.docker_base_url = docker_base_url

        # 初始化 Docker 客户端
        try:
            self.client = docker.DockerClient(base_url=self.docker_base_url)
        except Exception:
            # 如果 Docker 不可用，设置为 None
            self.client = None

    def execute(
        self,
        code: str,
        env: Optional[Dict[str, str]] = None,
        workdir: str = "/workspace"
    ) -> Dict[str, Any]:
        """
        在 Docker 容器中执行代码

        Args:
            code: 要执行的 Python 代码
            env: 环境变量字典
            workdir: 容器内的工作目录

        Returns:
            包含 stdout, stderr, exit_code 的字典
        """
        # 安全检查
        if not self._security_check(code):
            return {
                'stdout': '',
                'stderr': 'Security violation: Dangerous code pattern detected',
                'exit_code': -1
            }

        # 如果 Docker 不可用，使用本地模拟执行
        if self.client is None:
            return self._mock_execute(code, env, workdir)

        container = None
        temp_file = None
        try:
            # 创建临时文件来存储代码
            temp_file = self._create_temp_file(code)

            # 启动容器
            container = self._start_container(temp_file, env, workdir)

            # 等待执行完成或超时
            if not self._wait_for_container(container):
                return {
                    'stdout': '',
                    'stderr': 'Execution timeout',
                    'exit_code': -1
                }

            # 获取执行结果
            return self._get_execution_result(container)

        except Exception as e:
            return {
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'exit_code': -1
            }
        finally:
            # 清理资源
            self._cleanup(container, temp_file)

    def _create_temp_file(self, code: str) -> str:
        """创建临时文件存储代码"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            return f.name

    def _start_container(self, temp_file: str, env: Optional[Dict[str, str]], workdir: str):
        """启动 Docker 容器"""
        return self.client.containers.run(
            image=self.image,
            command="python /workspace/code.py",
            detach=True,
            remove=False,
            mem_limit=self.memory_limit,
            nano_cpus=int(self.cpu_limit * 1e9),
            network_disabled=True,
            read_only=True,
            tmpfs={'/tmp': 'rw,noexec,nosuid,size=100m'},
            environment=env or {},
            working_dir=workdir,
            volumes={
                temp_file: {
                    'bind': '/workspace/code.py',
                    'mode': 'ro'
                }
            }
        )

    def _wait_for_container(self, container) -> bool:
        """等待容器执行完成，返回是否成功完成"""
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            container.reload()
            if container.status == 'exited':
                return True
            time.sleep(0.1)

        # 超时，杀死容器
        container.kill()
        return False

    def _get_execution_result(self, container) -> Dict[str, Any]:
        """获取容器执行结果"""
        exit_code = container.attrs['State']['ExitCode']
        stdout = container.logs(stdout=True, stderr=False).decode('utf-8')
        stderr = container.logs(stdout=False, stderr=True).decode('utf-8')

        return {
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': exit_code
        }

    def _cleanup(self, container, temp_file: str) -> None:
        """清理容器和临时文件"""
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

        # 清理容器
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass

    def _security_check(self, code: str) -> bool:
        """
        代码安全检查

        Args:
            code: 要检查的代码

        Returns:
            是否安全
        """
        # 检查危险模式
        if self._contains_dangerous_patterns(code):
            return False

        # 检查危险导入
        if self._contains_dangerous_imports(code):
            return False

        return True

    def _contains_dangerous_patterns(self, code: str) -> bool:
        """检查代码是否包含危险模式"""
        return any(pattern in code for pattern in self.DANGEROUS_PATTERNS)

    def _contains_dangerous_imports(self, code: str) -> bool:
        """检查代码是否包含危险的 import 语句"""
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                if any(module in line for module in self.DANGEROUS_IMPORTS):
                    return True
        return False

    def _mock_execute(
        self,
        code: str,
        env: Optional[Dict[str, str]] = None,
        workdir: str = "/workspace"
    ) -> Dict[str, Any]:
        """
        当 Docker 不可用时的模拟执行

        Args:
            code: 要执行的代码
            env: 环境变量
            workdir: 工作目录

        Returns:
            执行结果
        """
        # 设置环境变量
        old_env = self._set_environment_variables(env)

        try:
            # 捕获输出
            stdout_capture, stderr_capture = self._capture_output()

            # 执行代码
            exit_code = self._execute_code(code, stdout_capture, stderr_capture)

            return {
                'stdout': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue(),
                'exit_code': exit_code
            }

        finally:
            # 恢复环境变量
            self._restore_environment_variables(old_env)

    def _set_environment_variables(self, env: Optional[Dict[str, str]]) -> Dict[str, Optional[str]]:
        """设置环境变量并返回旧值"""
        old_env = {}
        if env:
            for key, value in env.items():
                old_env[key] = os.environ.get(key)
                os.environ[key] = value
        return old_env

    def _restore_environment_variables(self, old_env: Dict[str, Optional[str]]) -> None:
        """恢复环境变量"""
        for key, old_value in old_env.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value

    def _capture_output(self) -> Tuple[io.StringIO, io.StringIO]:
        """创建输出捕获器"""
        return io.StringIO(), io.StringIO()

    def _execute_code(
        self,
        code: str,
        stdout_capture: io.StringIO,
        stderr_capture: io.StringIO
    ) -> int:
        """执行代码并返回退出码"""
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            try:
                # 创建执行环境
                safe_globals = {'__builtins__': __builtins__}
                exec(code, safe_globals)
                return 0
            except Exception as e:
                print(f"{type(e).__name__}: {e}", file=stderr_capture)
                return 1

    def close(self):
        """关闭 Docker 客户端连接"""
        if self.client:
            self.client.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
