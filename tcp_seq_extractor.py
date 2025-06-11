# from bcc import BPF
# import socket

# # Define the eBPF program
# bpf_program = """
# #define KBUILD_MODNAME "tcp_seq_extractor"
# #include <uapi/linux/bpf.h>
# #include <linux/if_ether.h>
# #include <linux/ip.h>
# #include <linux/tcp.h>

# // eBPF program to process packets
# int process_packet(struct xdp_md *ctx) {
#     // Get data and data_end pointers
#     void *data = (void *)(long)ctx->data;
#     void *data_end = (void *)(long)ctx->data_end;

#     // Parse Ethernet header
#     struct ethhdr *eth = data;
#     if ((void *)(eth + 1) > data_end) {
#         return XDP_PASS;
#     }

#     // Check for IP packet
#     if (eth->h_proto != __constant_htons(ETH_P_IP)) {
#         return XDP_PASS;
#     }

#     // Parse IP header
#     struct iphdr *ip = data + sizeof(*eth);
#     if ((void *)(ip + 1) > data_end) {
#         return XDP_PASS;
#     }

#     // Check for TCP packet
#     if (ip->protocol != IPPROTO_TCP) {
#         return XDP_PASS;
#     }

#     // Parse TCP header
#     struct tcphdr *tcp = (void *)ip + (ip->ihl * 4);
#     if ((void *)(tcp + 1) > data_end) {
#         return XDP_PASS;
#     }

#     // Extract details from TCP header
#     u16 sport = ntohs(tcp->source);  // Source port
#     u16 dport = ntohs(tcp->dest);   // Destination port
#     u32 seq = ntohl(tcp->seq);      // Sequence number
#     u32 ack = ntohl(tcp->ack_seq);  // Acknowledgment number

#     // Get the current timestamp in nanoseconds
#     u64 ts = bpf_ktime_get_ns();

#     // Log details in parts due to trace_printk limitations
#     bpf_trace_printk("Timestamp: %llu, Src Port: %u\\n", ts, sport);
#     bpf_trace_printk("Dst Port: %u, Seq: %u, Ack: %u\\n", dport, seq, ack);

#     return XDP_PASS;
# }

# """

# # Load and attach the eBPF program
# b = BPF(text=bpf_program)
# fn = b.load_func("process_packet", BPF.XDP)

# # Replace with your network interface
# interface = "lo"  # Change this to your actual interface name
# b.attach_xdp(interface, fn, 0)
# # b.attach_raw_socket(fn, interface)

# print(f"Listening on interface {interface}... Press Ctrl+C to stop.")

# # Function to detach XDP program
# def cleanup():
#     print("\nDetaching XDP program...")
#     b.remove_xdp(interface, 0)

# # Handle program exit
# try:
#     while True:
#         # Continuously print trace output from the eBPF program
#         print(b.trace_readline())
# except KeyboardInterrupt:
#     cleanup()
# except Exception as e:
#     print(f"Error: {e}")
#     cleanup()

from bcc import BPF

# Define the BPF program
bpf_program = """
#define KBUILD_MODNAME "tcp_seq_extractor"
#include <linux/ptrace.h>
#include <net/sock.h>
#include <net/tcp.h>

// Tracepoint for the 'tcp_rcv_established' function
int trace_tcp_rcv_established(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb) {
    struct tcphdr tcp_header;
    u32 skb_len;
    
    // Use bpf_probe_read to safely access skb->len
    bpf_probe_read(&skb_len, sizeof(skb_len), &skb->len);
    
    // Check if the packet is large enough
    if (skb_len < sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct tcphdr))
        return 0;

    // Use bpf_probe_read to read the TCP header
    bpf_probe_read(&tcp_header, sizeof(tcp_header), (void *)(skb->data + sizeof(struct ethhdr) + sizeof(struct iphdr)));

    // Extract information: source port, destination port, sequence number, ack number
    u16 src_port = ntohs(tcp_header.source);
    u16 dst_port = ntohs(tcp_header.dest);
    u32 seq_num = ntohl(tcp_header.seq);
    u32 ack_num = ntohl(tcp_header.ack_seq);

    // Print source port and timestamp in the first trace_printk
    bpf_trace_printk("TCP Packet - Src Port: %d, Timestamp: %llu\\n", src_port, bpf_ktime_get_ns());

    // Print destination port, seq, and ack in the second trace_printk
    bpf_trace_printk("Dst Port: %d, Seq: %u, Ack: %u\\n", dst_port, seq_num, ack_num);

    return 0;
}
"""

# Load the BPF program
b = BPF(text=bpf_program)

# Attach the tracepoint to the tcp_rcv_established function
b.attach_kprobe(event="tcp_rcv_established", fn_name="trace_tcp_rcv_established")

print("Tracing TCP packets. Press Ctrl+C to stop...")

# Read trace output in real-time
try:
    while True:
        print(b.trace_readline())
except KeyboardInterrupt:
    print("Detaching BPF program...")
