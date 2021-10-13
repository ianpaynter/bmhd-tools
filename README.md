Lots of experiments and fragments in here, but the following might be useful:

s3 inventory interactions:

s3inventoryProcessing.py works with s_s3InventoryReport.py and c_s3Intentory.py to pull inventory manifests for s3 buckets from s3 Inventory service in AWS and publish them to Slack via c_SlackBot.py

Benchmarking/profiling tools:

BenchmarkingToolkit.py is trying to integrate line_profiler, memory_profiler, resource, ps_util and other profiling tools to provide beginner-friendly benchmarking for code (with an eye to cloud migration). The idea is to take a .py piece of code as a text file, and add @profile decorators and other profiling tools automatically, then profile the code and return a copy of the original code with comments on each line showing the profiling results.

Probably not much else useful here for now. Eventually I'll port the highlights to the EFSI Toolkit.