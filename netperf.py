#!/usr/bin/python3

import argparse, subprocess, string, sys

argp = argparse.ArgumentParser(description = 'Perform netperf tests')
argp.add_argument('--cpus', '-c')
argp.add_argument('--version', '-v')
argp.add_argument('--output', '-o')
argp.add_argument('--length', '-l', default = 10)

args = argp.parse_args()

nruns = 5
len = args.length
tests = ['TCP_STREAM', 'UDP_STREAM', 'TCP_RR', 'UDP_RR']

# row-column to scrape output from
scrape = {
    'TCP_STREAM': (6, 4),
    'UDP_STREAM': (5, 5),
    'TCP_RR': (6, 5),
    'UDP_RR': (6, 5),
}

def run_test(test, len):
    netperf = subprocess.Popen(args = ['netperf', '-H', '192.168.122.89', 
                                       '-t', test, '-l', str(len),
                                        ],
                               stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                               )
    outs, errs = netperf.communicate()
    outs = str(outs, 'utf-8') 
    rc = netperf.wait()
    row, col = scrape[test]
    if rc != 0:
        raise Exception('netperf failed', outs)
    return float(outs.splitlines()[row].split()[col])

results = {}

for test in tests:
    results[test] = []
    for run in range(nruns):
        result = run_test(test = test, len = len)
        results[test] += [result]

template = string.Template(
''',,,,
,,,,
,,,,
,,,,
,Commit,$version,,
,Host,muninn.cloudius,,
,Client,localhost,,
,CPUs,$cpus,,
,,,,
,TCP STREAM,UDP STREAM,TCP RR,UDP RR
,Mbps,Mbps,Tps,Tps
''')

output = open(args.output, 'w') if sys.stdout else args.output 

print(template.substitute(cpus = args.cpus, version = args.version), file = output)

for row in range(nruns):
    print(',', file = output, end = '')
    print(*[results[col][row] for col in tests], sep = ',', file = output)
print(',', file = output)