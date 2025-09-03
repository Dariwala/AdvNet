from multiflow.split_trace import split
from multiflow.convert import convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.packet_log_parser import parse
import subprocess
from config import parent_folder
import os
import numpy as np
from os import sleep
from single_cc.evaluate import run_command
import shutil

def extract_ports_from_log(lines):
    ports = []
    for line in lines:
        if 'port' in line and '[' in line:
            port = int(line.split()[-6])
            ports.append(port)
    return ports

def run(bw_file, lt_file, queue_length, ref, tar, durations):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system("sleep 1")
    os.system("iperf -s &")
    os.system("sleep 0.1")
    command1 = "mm-delay-link-rrc 10 "+parent_folder +"AdvNet/traces/"+lt_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder+"packet-logs/ --uplink-log="+parent_folder+"packet-logs/uplink --downlink-log="+parent_folder+"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    commands = f"""
        {command1}
        sleep 0.1
        sudo iperf -c 100.64.0.1 -Z {ref} -t {str(sum(durations) / 1000)} &
        sudo iperf -c 100.64.0.1 -Z {tar} -t {str(sum(durations) / 1000)}
        exit
    """
    output, errors = shell.communicate(commands)
    ref_port, tar_port = extract_ports_from_log(output.split('\n'))

    return parse(ref_port, tar_port)

def run_parallel(durations, ref, tar, bw_file, lt_file, queue_length = 860, lock=None, core = 0):
    sleep(1)
    # os.system("mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"packet-logs/ --uplink-log="+ parent_folder +"packet-logs/uplink --downlink-log="+ parent_folder +"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+ str(queue_length) +" sudo iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000))
    folder = f"{uuid.uuid4().hex}/"
    os.makedirs(parent_folder + folder)
    shell = subprocess.Popen("/bin/bash",stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    lock.acquire()
    core_number = core.value
    #PDO writing enabled
    # command1 = "taskset -c "+str(core_number)+" mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder + folder + " --uplink-log="+ parent_folder + folder + "uplink --downlink-log="+ parent_folder + folder + "downlink --uplink-queue=droptail --uplink-queue-args=packets="+ str(queue_length)
    # PDO writing disabled
    command1 = "taskset -c "+str(core_number + 2)+" mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder + folder + " --uplink-log= --downlink-log= --uplink-queue=droptail --uplink-queue-args=packets="+ str(queue_length)
    command3 = "sudo tcpdump -i ingress host 100.64.0.1 and port 5001 -w "+alg+".pcap &"
    # command3 = "sudo python3 tcp_seq_extractor.py &"# > " + alg + "_ebpf"
    # print(command1)
    commands = f"""
            {command1}
            {'sleep 0.5'}
        """

    egress_addr = run_command(shell, commands, True)
    server_port = str(int(egress_addr.split('.')[-1]) + 5000)
    # os.system("sudo kill -9 $(sudo lsof -t -i :"+server_port+")")
    core.value = (core_number + 3) % os.cpu_count()
    lock.release()
    os.system("sudo kill -9 $(sudo lsof -t -i :"+server_port+");sleep 0.5;taskset -c "+str(core_number)+" iperf -s -p " + server_port + " &")
    # command2 = "taskset -c "+str(core_number + 1)+" sudo iperf -c " + egress_addr + " -p "+server_port+" -Z " + alg + " -t " + str(duration / 1000)
    commands = f"""
        sudo iperf -c {egress_addr} -Z {ref} -t {str(sum(durations) / 1000)} &
        sudo iperf -c {egress_addr} -Z {tar} -t {str(sum(durations) / 1000)}
    """
    _ = run_command(shell, commands, False)
    _ = run_command(shell, "exit", False)
    # shell.stdin.close()  # Close input stream when done
    stdout, stderr = shell.communicate(timeout=150)  # Final read with timeout
    print(stdout, stderr)
    sleep(1)
    ref_port, tar_port = extract_ports_from_log(stdout.split('\n'))

    return parse(ref_port, tar_port, folder), folder


def evaluate(trace, ref, n_evals, tar, log = False):
    bandwidths, latencies, durations, queue_length = split(trace)
    bandwidths, latencies, durations, queue_length = convert(bandwidths, latencies, durations, queue_length)

    bandwidths.append(bandwidths[0])
    latencies.append(latencies[0])
    durations.append(100 * 1000)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)

    logs = []

    with multiprocessing.Manager() as manager:
        lock = manager.Lock()
        core_number = manager.Value('i', 0)  # 'i' for int
        ref_bytes_list = []
        tar_bytes_list = []
        param_list = [(durations, ref, tar, bw_file, lt_file, queue_length, lock, core_number) for _ in range(n_evals)]

        with multiprocessing.Pool(processes=n_evals) as pool:
            perfs = pool.starmap(run_parallel, param_list)
        for ref_bytes, tar_bytes, folder  in perf_logs:
            ref_bytes_list.append(ref_bytes)
            tar_bytes_list.append(tar_bytes)
            if log:
                logs.append([ref_bytes, tar_bytes])
            
            shutil.rmtree(parent_folder + folder)

                
    noiseHandler = NoiseHandler().mean
    ref_bytes = noiseHandler(ref_bytes_list)
    tar_bytes = noiseHandler(tar_bytes_list)
    
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        return ref_bytes / (ref_bytes + tar_bytes)