import json
import argparse
from operator import itemgetter
import yaml # type: ignore
import fnmatch
import os

def get_params():
    parser = argparse.ArgumentParser(description="Convert Json to Markdown")
    parser.add_argument("--input", required=True, help="Json file path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()
    return args.input, args.output

# def append(path):
#     return os.getcwd() + path

def load_ignore_patterns(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    # dir = os.getcwd()
    # return list(map(lambda path: f"{dir}/{path}", config.get('ignore', [])))
    return config.get('ignore', [])

def should_ignore(file_path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def generate_markdown_report(coverage_data, ignore_patterns):
    report = "# Code Coverage Report\n\n"
    report += "| File | Coverage | Executable Lines | Covered Lines  |\n"
    report += "| --- | --- | --- | --- |\n"

    for target in coverage_data['targets']:
        if target['name'] != "Artemis.app":
            continue
        # report += f"## {target['name']}\n\n"
        # files = sorted(target['files'], key=itemgetter('lineCoverage'), reverse=True)
        files = sorted(target['files'], key=lambda k: (k['lineCoverage'],+k['executableLines']), reverse=True)
        for file in files:
            dir = os.getcwd()
            filename = file['path'].replace(dir, '')
            if should_ignore(filename, ignore_patterns):
                print(f"ingore file: {filename}")
                continue
            coverage = file['lineCoverage']
            total = file['executableLines']
            hit = file['coveredLines']
            report += f"| {filename} | {coverage:.2%} | {total} | {hit} |\n"
        report += "\n"

    return report


def main():
    input, output = get_params()
    print(f"current dir: {os.getcwd()}")
    print(f"current dir: {os.path.abspath('.')}")
    ignore_patterns = load_ignore_patterns('.slather.yml')

    with open(input, 'r') as file:
        coverage_data = json.load(file)

    markdown_report = generate_markdown_report(coverage_data, ignore_patterns)
    with open(output, 'w') as file:
        file.write(markdown_report)

if __name__ == "__main__":
    main()
