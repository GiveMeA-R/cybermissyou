package main

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"time"
)

const (
	OPEN        = "OPEN"
	CLOSED      = "CLOSED"
	FILTERED    = "FILTERED"
	UDP_TIMEOUT = 1000 // Định nghĩa giá trị timeout cho UDP tại đây (milliseconds)
)

const portScannerMsg string = "CheckPortOpen"

func main() {
	var network string
	var startPort, endPort int

	// Nhập địa chỉ mạng con từ người dùng
	fmt.Print("Nhập địa chỉ mạng con (ví dụ: 192.168.5.0/24): ")
	_, err := fmt.Scan(&network)
	if err != nil {
		fmt.Println("Lỗi khi nhập địa chỉ mạng con:", err)
		return
	}

	// Nhập dãy cổng từ người dùng
	fmt.Print("Nhập cổng bắt đầu: ")
	_, err = fmt.Scan(&startPort)
	if err != nil {
		fmt.Println("Lỗi khi nhập cổng bắt đầu:", err)
		return
	}

	fmt.Print("Nhập cổng kết thúc: ")
	_, err = fmt.Scan(&endPort)
	if err != nil {
		fmt.Println("Lỗi khi nhập cổng kết thúc:", err)
		return
	}

	// Tạo và mở file để lưu kết quả
	file, err := os.Create("result.txt")
	if err != nil {
		fmt.Println("Lỗi khi tạo file:", err)
		return
	}
	defer file.Close()

	// Chuyển đổi địa chỉ mạng con thành danh sách các địa chỉ IP con
	ipList, err := generateIPList(network)
	if err != nil {
		fmt.Println("Địa chỉ mạng con không hợp lệ:", err)
		return
	}

	for _, ip := range ipList {
		for port := startPort; port <= endPort; port++ {
			result := Scan(ip, strconv.Itoa(port))

			switch result {
			case OPEN, FILTERED:
				fmt.Fprintf(file, "Host %s - Cổng %d: %s\n", ip, port, result)
			}
		}
	}
}

func generateIPList(network string) ([]net.IP, error) {
	ipList := []net.IP{}
	ip, ipNet, err := net.ParseCIDR(network)
	if err != nil {
		return nil, err
	}

	for ip := ip.Mask(ipNet.Mask); ipNet.Contains(ip); inc(ip) {
		ipCopy := make(net.IP, len(ip))
		copy(ipCopy, ip)
		ipList = append(ipList, ipCopy)
	}

	return ipList, nil
}

func inc(ip net.IP) {
	for j := len(ip) - 1; j >= 0; j-- {
		ip[j]++
		if ip[j] > 0 {
			break
		}
	}
}

func Scan(ip net.IP, port string) string {
	p, _ := strconv.Atoi(port)
	udpAddr := net.UDPAddr{IP: ip, Port: p}
	conn, err := net.DialUDP("udp4", nil, &udpAddr)
	if err != nil {
		if strings.Contains(err.Error(), "resource temporarily unavailable") {
			fmt.Println("Waiting for a moment and retrying...")
			time.Sleep(time.Millisecond * time.Duration(UDP_TIMEOUT))
			return Scan(ip, port)
		} else {
			return CLOSED
		}
	}
	defer conn.Close()
	_, err = conn.Write([]byte(portScannerMsg))
	if err != nil {
		return CLOSED
	}
	conn.SetReadDeadline(time.Now().Add(time.Duration(UDP_TIMEOUT) * time.Millisecond))
	buf := make([]byte, 15)
	n, err := conn.Read(buf)
	if err != nil {
		if nerr, ok := err.(net.Error); ok && nerr.Timeout() {
			return FILTERED
		} else {
			return CLOSED
		}
	}

	if string(buf[:n]) == portScannerMsg {
		return CLOSED
	}

	return OPEN
}
