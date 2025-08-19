"""Shell command execution tool for the AI agent."""
import asyncio
import subprocess
import os
import shutil
from typing import Any, List, Dict
from pathlib import Path

from agents import function_tool, RunContextWrapper


@function_tool
async def execute_shell_command(
    ctx: RunContextWrapper[Any], 
    command: str, 
    working_directory: str | None = None,
    timeout: int = 30
) -> str:
    """Execute a shell command on the local Linux machine.
    
    This tool allows the AI agent to run shell commands on the local system.
    Use with caution as it can potentially execute harmful commands.
    
    Args:
        command: The shell command to execute (e.g., 'ls -la', 'pwd', 'echo "hello"')
        working_directory: Optional working directory to run the command in
        timeout: Maximum time in seconds to wait for command completion (default: 30)
        
    Returns:
        The output of the command, or error message if the command fails
    """
    try:
        # Validate working directory if provided
        if working_directory:
            working_dir = Path(working_directory)
            if not working_dir.exists():
                return f"Error: Working directory '{working_directory}' does not exist"
            if not working_dir.is_dir():
                return f"Error: '{working_directory}' is not a directory"
        else:
            working_directory = os.getcwd()
        
        # Security: Basic command validation
        dangerous_commands = [
            'rm -rf /', 'sudo rm -rf', 'mkfs', 'dd if=', 'kill -9 1',
            ':(){ :|:& };:', 'chmod -R 777 /', 'chown -R root /'
        ]
        
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                return f"Error: Command blocked for security reasons: '{command}'"
        
        # Execute command
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory,
            env=os.environ.copy()
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return f"Error: Command timed out after {timeout} seconds"
        
        # Format output
        output_lines = []
        
        if stdout:
            output_lines.append("STDOUT:")
            output_lines.append(stdout.decode('utf-8', errors='replace').strip())
        
        if stderr:
            output_lines.append("STDERR:")
            output_lines.append(stderr.decode('utf-8', errors='replace').strip())
        
        if process.returncode != 0:
            output_lines.append(f"Exit code: {process.returncode}")
        
        if not output_lines:
            output_lines.append("Command executed successfully with no output.")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error executing command: {str(e)}"


@function_tool
async def list_directory(ctx: RunContextWrapper[Any], path: str = ".") -> str:
    """List contents of a directory.
    
    Args:
        path: Directory path to list (default: current directory)
        
    Returns:
        Directory listing with file/folder information
    """
    try:
        target_path = Path(path).expanduser().resolve()
        
        if not target_path.exists():
            return f"Error: Path '{path}' does not exist"
        
        if not target_path.is_dir():
            return f"Error: Path '{path}' is not a directory"
        
        items = []
        try:
            for item in sorted(target_path.iterdir()):
                if item.is_dir():
                    items.append(f"[DIR]  {item.name}/")
                else:
                    size = item.stat().st_size
                    items.append(f"[FILE] {item.name} ({size} bytes)")
        except PermissionError:
            return f"Error: Permission denied accessing '{path}'"
        
        if not items:
            return f"Directory '{path}' is empty"
        
        return f"Contents of '{path}':\n" + "\n".join(items)
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@function_tool
async def get_system_info(ctx: RunContextWrapper[Any]) -> str:
    """Get basic system information about the Linux machine.
    
    Returns:
        System information including OS, architecture, memory, etc.
    """
    try:
        info_lines = []
        
        # OS information
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                for line in os_info.split('\n'):
                    if line.startswith('PRETTY_NAME='):
                        os_name = line.split('=', 1)[1].strip('"')
                        info_lines.append(f"OS: {os_name}")
                        break
        except:
            info_lines.append("OS: Unknown Linux distribution")
        
        # Architecture
        process = await asyncio.create_subprocess_shell(
            'uname -m',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()
        if stdout:
            arch = stdout.decode().strip()
            info_lines.append(f"Architecture: {arch}")
        
        # Kernel version
        process = await asyncio.create_subprocess_shell(
            'uname -r',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate()
        if stdout:
            kernel = stdout.decode().strip()
            info_lines.append(f"Kernel: {kernel}")
        
        # Memory information
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_kb = int(line.split()[1])
                        mem_gb = round(mem_kb / (1024 * 1024), 2)
                        info_lines.append(f"Total Memory: {mem_gb} GB")
                        break
        except:
            pass
        
        # Current working directory
        cwd = os.getcwd()
        info_lines.append(f"Current Directory: {cwd}")
        
        # Current user
        import getpass
        user = getpass.getuser()
        info_lines.append(f"Current User: {user}")
        
        return "System Information:\n" + "\n".join(info_lines)
        
    except Exception as e:
        return f"Error getting system information: {str(e)}"


@function_tool
async def check_file_exists(ctx: RunContextWrapper[Any], filepath: str) -> str:
    """Check if a file or directory exists and get basic information about it.
    
    Args:
        filepath: Path to the file or directory to check
        
    Returns:
        Information about the file/directory existence and properties
    """
    try:
        path = Path(filepath).expanduser().resolve()
        
        if not path.exists():
            return f"File/directory '{filepath}' does not exist"
        
        info = [f"Path: {path}"]
        
        if path.is_file():
            info.append("Type: File")
            size = path.stat().st_size
            info.append(f"Size: {size} bytes")
        elif path.is_dir():
            info.append("Type: Directory")
            try:
                item_count = len(list(path.iterdir()))
                info.append(f"Items: {item_count}")
            except PermissionError:
                info.append("Items: Permission denied")
        else:
            info.append("Type: Other (symlink, device, etc.)")
        
        # Permissions
        stat = path.stat()
        import stat as stat_module
        mode = stat.st_mode
        perms = stat_module.filemode(mode)
        info.append(f"Permissions: {perms}")
        
        return "\n".join(info)
        
    except Exception as e:
        return f"Error checking file: {str(e)}"


class ShellTool:
    """Container class for shell-related tools."""
    
    @staticmethod
    def get_tools() -> List:
        """Get all shell tools for the agent."""
        return [
            execute_shell_command,
            list_directory,
            get_system_info,
            check_file_exists
        ]
