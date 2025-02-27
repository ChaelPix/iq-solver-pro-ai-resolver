#!/usr/bin/env python3
import os
import subprocess
import platform
import shutil

def check_compiler_exists(compiler):
    """Check if the specified compiler exists"""
    return shutil.which(compiler) is not None

def build_c_modules():
    """
    Build the C modules for the Algo X Knuth implementation.
    """
    print("Building C modules...")
    
    # Get the directory of the current script
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, 'src')
    
    # Path to C source file
    c_file = os.path.join(src_dir, 'algo_x_knuth_c.c')
    
    # Path for output library
    output_file = os.path.join(src_dir, 'algo_x_knuth_c.so')
    
    # Determine compiler flags based on platform
    system = platform.system()
    compiler = 'gcc'
    
    if not check_compiler_exists(compiler):
        print(f"Error: {compiler} compiler not found. Please install it first.")
        return False
    
    if system == 'Darwin':  # macOS
        compile_cmd = [compiler, '-shared', '-fPIC', '-O3', '-Wall', c_file, '-o', output_file]
    elif system == 'Linux':
        compile_cmd = [compiler, '-shared', '-fPIC', '-O3', '-Wall', c_file, '-o', output_file]
    elif system == 'Windows':
        # For Windows, we might need a different approach
        compiler = 'gcc'  # Assume MinGW or similar
        if not check_compiler_exists(compiler):
            print(f"Error: {compiler} compiler not found. On Windows, you might need MinGW or similar.")
            return False
        output_file = os.path.join(src_dir, 'algo_x_knuth_c.dll')
        compile_cmd = [compiler, '-shared', '-O3', '-Wall', c_file, '-o', output_file]
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
    # Execute the compile command
    print(f"Running: {' '.join(compile_cmd)}")
    result = subprocess.run(compile_cmd, check=False)
    
    if result.returncode != 0:
        print(f"Build failed with return code {result.returncode}")
        print("Make sure you have development tools installed for your platform.")
        print("- On Linux: sudo apt-get install build-essential")
        print("- On macOS: Install Xcode Command Line Tools")
        print("- On Windows: Install MinGW or Visual Studio Build Tools")
        return False
    
    print(f"Successfully built C module: {output_file}")
    return True

if __name__ == "__main__":
    success = build_c_modules()
    exit(0 if success else 1)
