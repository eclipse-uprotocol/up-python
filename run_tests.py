import subprocess

def run_tests_with_coverage():
    print("\nRunning tests with coverage...")
    subprocess.run(["python", "-m", "coverage", "run", "--source", "uprotocol/", "-m", "pytest", "-v"])

    print("\nGenerating terminal coverage report...")
    subprocess.run(["python", "-m", "coverage", "report"])

    print("\nGenerating HTML coverage report...")
    subprocess.run(["python", "-m", "coverage", "html"])

    print("\nHTML report generated in ./htmlcov/index.html")
    print("Open it in your browser to view detailed coverage.")

if __name__ == "__main__":
    run_tests_with_coverage()

