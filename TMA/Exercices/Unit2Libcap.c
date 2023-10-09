#include <stdio.h>
#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

void packet_handler(unsigned char *user_data, const struct pcap_pkthdr *pkthdr, const unsigned char *packet) {
    struct ip *ip_header = (struct ip*)(packet + 14); // Skip Ethernet header
    struct tcphdr *tcp_header = (struct tcphdr*)(packet + 14 + (ip_header->ip_hl << 2)); // Skip IP header

    if (tcp_header->th_dport == htons(80) || tcp_header->th_dport == htons(443)) {
        printf("Timestamp: %s", ctime((const time_t*)&pkthdr->ts.tv_sec));
        printf("Source IP: %s\n", inet_ntoa(ip_header->ip_src));
        printf("Destination IP: %s\n", inet_ntoa(ip_header->ip_dst));
        printf("Packet Length: %d bytes\n", pkthdr->len);
        printf("--------------------------\n");
    }
}

int main() {
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;

    // Open network interface for packet capture
    handle = pcap_open_live("your_network_interface", BUFSIZ, 1, 1000, errbuf);

    if (handle == NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", "your_network_interface", errbuf);
        return 2;
    }

    // Set filter for port 80 and 443
    struct bpf_program fp;
    char filter_exp[] = "tcp port 80 or tcp port 443";
    bpf_u_int32 net;

    if (pcap_compile(handle, &fp, filter_exp, 0, net) == -1) {
        fprintf(stderr, "Couldn't parse filter %s: %s\n", filter_exp, pcap_geterr(handle));
        return 2;
    }

    if (pcap_setfilter(handle, &fp) == -1) {
        fprintf(stderr, "Couldn't install filter %s: %s\n", filter_exp, pcap_geterr(handle));
        return 2;
    }

    // Start capturing packets
    pcap_loop(handle, 0, packet_handler, NULL);

    // Close the handle
    pcap_close(handle);

    return 0;
}
