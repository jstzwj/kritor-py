
import subprocess
import glob
import os
import shutil

import re

def patch_file(path: str):
    pattern = r'^import "(.+?)/(.+?)\.proto";$'

    with open(path, 'r', encoding="utf-8") as file:
        content = file.read()

    modified_content = re.sub(pattern, r'import "kritor/protos/\1/\2.proto";', content, flags=re.MULTILINE)

    with open(path, 'w', encoding="utf-8") as file:
        file.write(modified_content)

def main():
    proto_files = glob.glob("kritor-core/protos/*/*.proto")
    
    for proto in proto_files:
        new_proto = proto.replace("\\", "/").replace("kritor-core", "kritor")
        os.makedirs(os.path.dirname(new_proto), exist_ok=True)
        shutil.copy(proto, new_proto)
    
    for proto in proto_files:
        new_proto = proto.replace("\\", "/").replace("kritor-core", "kritor")
        patch_file(new_proto)

    for proto in proto_files:
        print(proto)
        new_proto = proto.replace("\\", "/").replace("kritor-core", "kritor")
        result = subprocess.run([
            'python',
            '-m', 'grpc_tools.protoc',
            '-I.',
            '--python_out=.',
            '--grpc_python_out=.',
            '--pyi_out=.',
            new_proto,
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            print(result.returncode)

    for proto in proto_files:
        new_proto = proto.replace("\\", "/").replace("kritor-core", "kritor")
        os.remove(new_proto)

if __name__ == "__main__":
    main()
