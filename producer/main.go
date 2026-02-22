package main

import (
	"bytes"
	"encoding"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
	"os"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/mmcdole/gofeed"
	"github.com/joho/godotenv"
)

// Load env variables
gatewayURL := os.Getenv("GATEWAY_URL")
pollInterval := os.Getenv("POLL_INTERVAL")

// RSS Feeds (The Wires)
var RSSFeeds = map[string]string{
	"yahoo_finance": "https://finance.yahoo.com/news/rssindex",
	"coindesk":      "https://www.coindesk.com/arc/outboundfeeds/rss/",
	"wsj_markets":   "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
}

// Match payload with the Gateway's expected JSON schema
type Payload struct {
	UserID string `json:"user_id"`
	DocumentID string `json:"document_id"`
	Content string `json:"content"`
	Metadata map[string]string `json:"metadata"`
}

func main() {
	fmt.Println("[*] Starting Go Feed Producer (The Wire)")

	// --- Configuration Loader ---
	if gatewayURL == "" {
		gatewayURL = "http://gateway:8080/ingest"
		fmt.Printf(" [!] GATEWAY_URL not set. Defaulting to %\n, gatewayURL")
	}

	defaultpollIntervalStr := 60
	pollInterval = 60 * time.Second
	if pollIntervalStr != "" {
		sec, err := strconv.Atoi(pollIntervalStr)
		if err == nil {
			pollInterval = time.Duration(sec) * time.Second
		} else {
			fmt.Printf(" [!] Invalid POLL_INTERVAL_SEC. Defaulting to 60s\n")
		}
	}

	fp := gofeed.NewParser()

	for {
		fmt.Printf("\n--- Polling %d RSS Feeds Concurrently ---\n", len(RSSFeeds))

		var wg sync.WaitGroup
		
		for source, url := range RSSFeeds {
			wg.Add(1)
			go fetchAndPush(fp, source, url, gatewayURL,&wg)
		}

		wg.Wait()

		fmt.Printf("[*] Cycle complete. Sleeping for %v...\n", pollInterval)
		time.Sleep(pollInterval)
	}	
}

// Pass gatewayURl into the worket function