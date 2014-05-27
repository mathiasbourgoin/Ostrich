# -*- coding:utf-8 -*-

import subprocess
import json
import os
import threading
import time

class WebbenchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.out = "[]"

    def run(self):
        webserver_script = ["python", "webbench.py"]
        stdout, stderr = subprocess.Popen(webserver_script,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE).communicate()
        self.out = stdout[:]


class Benchmark(object):
    def __init__(self, name, dir):
        self.name = name
        self.dir = dir

    def run_c_benchmark(self):
        """Run the C benchmark.  Assume that there is a build/c/run.sh script
           that will feed all the correct parameters."""

        prev_dir = os.getcwd()
        os.chdir(self.dir)

        runner_script = ["sh", os.path.join("build", "c", "run.sh")]
        results = []
        for _ in xrange(ITERS):
            stdout, stderr = subprocess.Popen(runner_script,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE).communicate()
            result = json.loads(stdout)
            results.append(result)
        os.chdir(prev_dir)
        return [r['time'] for r in results]


    def run_asmjs_benchmark(self, browser, browser_opts):
        """Run the asm.js inside the browser with the specified opts."""
        webserver_script = ["python", "webbench.py"]
        browser_script = [browser] + browser_opts + \
            ["http://0.0.0.0:8080/static/" + os.path.join(self.dir, "build", "asmjs", "run.html")]

        # Start webserver
        thr = WebbenchThread()
        thr.start()

        # Start browser
        time.sleep(1)
        subprocess.call(browser_script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        thr.join()
        return json.loads(thr.out)


    def build(self):
        """Move into the benchmark's directory and run make clean && make."""

        prev_dir = os.getcwd()
        os.chdir(self.dir)
        subprocess.call(["make", "clean"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chdir(prev_dir)


ITERS = 10
BENCHMARKS = [
    Benchmark("nqueens", "branch-and-bound/nqueens"),
    Benchmark("crc", "combinational-logic/crc"),
    Benchmark("lud", "dense-linear-algebra/lud"),
    Benchmark("nw", "dynamic-programming/nw"),
    Benchmark("hmm", "graphical-models/hmm"),
    Benchmark("bfs", "graph-traversal/bfs"),
    Benchmark("page-rank", "map-reduce/page-rank"),
    Benchmark("lavamd", "n-body-methods/lavamd"),
    #Benchmark("spmv", "sparse-linear-algebra/spmv"),
    Benchmark("fft", "spectral-methods/fft"),
    Benchmark("srad", "structured-grid/SRAD"),
    Benchmark("back-propagation", "unstructured-grid/back-propagation"),
]

for b in BENCHMARKS:
    b.build()

for b in BENCHMARKS:
    print "%s,C,N/A,%s" % (b.name, ','.join(str(x) for x in b.run_c_benchmark()))
    print "%s,asmjs,Chrome,%s" % (b.name, ','.join(str(x) for x in b.run_asmjs_benchmark("google-chrome", [])))
    print "%s,asmjs,Firefox,%s" % (b.name, ','.join(str(x) for x in b.run_asmjs_benchmark("firefox", [])))
